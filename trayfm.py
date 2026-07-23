import ctypes
import json
import logging
import os
import subprocess
import sys
import threading
import time
import tkinter as tk
import winreg
from pathlib import Path

import keyboard
import pystray
import vlc
from PIL import Image, ImageDraw
from overlay import Overlay

__version__ = "1.0.0"

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"
STATIONS_PATH = BASE_DIR / "stations.json"
STATE_PATH = BASE_DIR / "state.json"



_mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "Local\\TrayFMMutex")
if ctypes.windll.kernel32.GetLastError() == 183:
    print("TrayFM is already running", flush=True)
    sys.exit(0)

_overlay = None

_tray_icon = None

def make_icon():
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([2, 2, 13, 13], fill="#ffffff", outline="#cccccc")
    draw.polygon([(7, 5), (7, 11), (11, 8)], fill="#222222")
    return img


def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_stations():
    with open(STATIONS_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_state():
    try:
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(cat, station, vol, play, sfx_file="", sfx_volumes=None):
    try:
        data = {"cat": cat, "station": station, "volume": vol, "playing": play, "sfx_file": sfx_file, "sfx_volumes": sfx_volumes or {}}
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass


def main():
    config = load_config()
    categories = load_stations()
    audio_cfg = config.get("audio", {})
    vol_step = audio_cfg.get("step", 5)
    vol_min = audio_cfg.get("min", 0)
    vol_max = audio_cfg.get("max", 100)
    vol_default = audio_cfg.get("default", 50)

    if not categories:
        return

    state = load_state()
    cat_names = list(categories.keys())

    check_timeout = audio_cfg.get("check_timeout", 10)

    overlay_cfg = config.get("overlay", {})
    overlay_timeout = overlay_cfg.get("timeout", 3)
    gifs_cfg = overlay_cfg.get("gifs_path", "gifs")
    gifs_path = gifs_cfg if os.path.isabs(gifs_cfg) else str(BASE_DIR / gifs_cfg)
    gifs_enabled = overlay_cfg.get("gifs_enabled", True)
    vhs_enabled = overlay_cfg.get("vhs_enabled", True)

    log_cfg = config.get("logging", {})
    logs_cfg = log_cfg.get("path", "logs")
    logs_path = logs_cfg if os.path.isabs(logs_cfg) else str(BASE_DIR / logs_cfg)
    logs_enabled = log_cfg.get("enabled", True)

    if logs_enabled:
        os.makedirs(logs_path, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(logs_path, "trayfm.log"),
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            encoding="utf-8",
        )

    overlay_corner = overlay_cfg.get("corner", "bottom-right")
    overlay_offset_x = overlay_cfg.get("offset_x", 20)
    overlay_offset_y = overlay_cfg.get("offset_y", 20)
    theme = overlay_cfg.get("theme", {})

    proxy = config.get("proxy", "").strip()
    vlc_args = "--no-xlib --quiet"
    if proxy:
        os.environ["all_proxy"] = proxy
        os.environ["http_proxy"] = proxy
        os.environ["https_proxy"] = proxy
        vlc_args += f" --http-proxy={proxy}"

    instance = vlc.Instance(vlc_args)
    player = instance.media_player_new()
    sfx_instance = vlc.Instance("--no-xlib --quiet --aout=directsound")
    sfx_player = sfx_instance.media_player_new()
    sfx_player.audio_set_volume(0)
    current_cat = state.get("cat", 0)
    current_station = state.get("station", 0)
    volume = state.get("volume", vol_default)
    playing = False
    resume = state.get("playing", False)

    try:
        _overlay = Overlay(gifs_path=gifs_path, gifs_enabled=gifs_enabled, vhs_enabled=vhs_enabled, corner=overlay_corner, offset_x=overlay_offset_x, offset_y=overlay_offset_y, theme=theme)
    except Exception as e:
        logging.warning("Overlay init failed: %s", e)
        _overlay = None

    def get_station():
        return categories[cat_names[current_cat]][current_station]

    def show_overlay(title, station="", category="", progress=None, info=""):
        if _overlay:
            _overlay.notify(title, station=station, category=category, timeout=overlay_timeout, progress=progress, info=info)

    def skip_current():
        next_station()
        show_overlay("Station Unavailable", station=get_station()["name"],
                      category=cat_names[current_cat], info=get_info_text())
        logging.info("Skipped to %s - %s", cat_names[current_cat], get_station()["name"])

    _check_id = 0

    def check_station(timeout=check_timeout, check_id=None):
        t = 0
        seen_progress = False
        while t < timeout:
            if not playing or (check_id is not None and check_id != _check_id):
                return
            state = player.get_state()
            if state == vlc.State.Playing:
                return
            if state in (vlc.State.Error, vlc.State.Ended):
                logging.warning("Station %s failed (state=%s)", get_station()["name"], state)
                break
            if state in (vlc.State.Opening, vlc.State.Buffering) and not seen_progress:
                seen_progress = True
                timeout += 6
            time.sleep(0.5)
            t += 0.5
        if playing and (check_id is None or check_id == _check_id):
            skip_current()

    sfx_cfg = config.get("sfx", {})
    sfx_path_cfg = sfx_cfg.get("path", "sfx")
    sfx_dir = sfx_path_cfg if os.path.isabs(sfx_path_cfg) else str(BASE_DIR / sfx_path_cfg)
    sfx_vol_max = sfx_cfg.get("vol_max", 150)
    sfx_vol_min = sfx_cfg.get("vol_min", 0)
    sfx_def_vol = 50
    sfx_volumes = {}
    sfx_files = sorted([f for f in os.listdir(sfx_dir) if f.endswith(('.wav', '.mp3', '.ogg', '.flac'))]) if os.path.isdir(sfx_dir) else []
    sfx_files.insert(0, "OFF")
    sfx_file = sfx_files[0] if sfx_files else ""
    sfx_path = "" if sfx_file == "OFF" else str(Path(sfx_dir) / sfx_file) if sfx_file else ""
    sfx_enabled = bool(sfx_files)
    for f in sfx_files:
        if f != "OFF":
            sfx_volumes[f] = sfx_def_vol
    sfx_volume_mode = False
    _sfx_media = None
    _sfx_media_path = ""

    def get_sfx_vol():
        return sfx_volumes.get(sfx_file, sfx_def_vol)

    def start_sfx():
        nonlocal _sfx_media, _sfx_media_path
        if sfx_file == "OFF" or not sfx_enabled or not os.path.isfile(sfx_path) or get_sfx_vol() == 0:
            return
        vol = get_sfx_vol()
        if _sfx_media is None or _sfx_media_path != sfx_path:
            _sfx_media = sfx_instance.media_new(sfx_path)
            _sfx_media.add_option(":loop")
            sfx_player.set_media(_sfx_media)
            _sfx_media_path = sfx_path
        sfx_player.play()
        sfx_player.audio_set_volume(vol)

    def stop_sfx():
        sfx_player.audio_set_volume(0)

    def next_sfx():
        nonlocal sfx_file, sfx_path
        if not sfx_files:
            return
        try:
            idx = sfx_files.index(sfx_file)
        except ValueError:
            idx = -1
        sfx_file = sfx_files[(idx + 1) % len(sfx_files)]
        sfx_path = "" if sfx_file == "OFF" else str(Path(sfx_dir) / sfx_file)
        sfx_volumes.setdefault(sfx_file, sfx_def_vol)
        if playing:
            if sfx_file == "OFF":
                stop_sfx()
            else:
                start_sfx()
        name = "OFF" if sfx_file == "OFF" else Path(sfx_file).stem.capitalize()
        logging.info("SFX switched to %s (vol=%d)", name, get_sfx_vol())
        show_overlay("SFX", station=name)

    def get_info_text():
        stations = categories[cat_names[current_cat]]
        idx = f"{current_station + 1}/{len(stations)}"
        bitrate = ""
        try:
            media = player.get_media()
            if media:
                stats = media.get_stats()
                if stats and stats.i_input_bitrate:
                    bitrate = f" · {stats.i_input_bitrate // 1000} kbps"
        except Exception:
            pass
        return idx + bitrate

    def play_current():
        nonlocal playing, _check_id
        _check_id += 1
        s = get_station()
        media = instance.media_new(s["url"])
        player.set_media(media)
        player.play()
        player.audio_set_volume(volume)
        playing = True
        logging.info("Playing %s - %s", cat_names[current_cat], s["name"])
        show_overlay("", station=s["name"], category=cat_names[current_cat], info=get_info_text())
        threading.Thread(target=check_station, daemon=True, args=(check_timeout, _check_id)).start()

    def toggle_play():
        nonlocal playing
        if not player.get_media():
            logging.info("Play (no media)")
            play_current()
        elif playing:
            player.pause()
            playing = False
            stop_sfx()
            logging.info("Paused %s - %s", cat_names[current_cat], get_station()["name"])
            show_overlay("Paused", station=get_station()["name"], category=cat_names[current_cat], info=get_info_text())
        else:
            player.play()
            playing = True
            start_sfx()
            logging.info("Resumed %s - %s", cat_names[current_cat], get_station()["name"])
            show_overlay("", station=get_station()["name"], category=cat_names[current_cat], info=get_info_text())

    def volume_up():
        nonlocal volume
        if sfx_volume_mode:
            if sfx_file == "OFF":
                logging.info("SFX is OFF, cannot change volume")
                show_overlay("SFX Volume", station="SFX is OFF")
                return
            vol = get_sfx_vol()
            was_zero = vol == 0
            vol = min(vol + vol_step, sfx_vol_max)
            sfx_volumes[sfx_file] = vol
            if was_zero and playing:
                start_sfx()
            else:
                sfx_player.audio_set_volume(vol)
            logging.info("SFX volume up: %d%%", vol)
            show_overlay("SFX Volume", station=f"SFX: {vol}%", progress=vol)
        else:
            volume = min(volume + vol_step, vol_max)
            player.audio_set_volume(volume)
            logging.info("Volume up: %d%%", volume)
            show_overlay("Radio Volume", station=f"Radio: {volume}%", progress=volume)

    def volume_down():
        nonlocal volume
        if sfx_volume_mode:
            if sfx_file == "OFF":
                logging.info("SFX is OFF, cannot change volume")
                show_overlay("SFX Volume", station="SFX is OFF")
                return
            vol = get_sfx_vol()
            vol = max(vol - vol_step, sfx_vol_min)
            sfx_volumes[sfx_file] = vol
            if vol == 0:
                stop_sfx()
            else:
                sfx_player.audio_set_volume(vol)
            logging.info("SFX volume down: %d%%", vol)
            show_overlay("SFX Volume", station=f"SFX: {vol}%", progress=vol)
        else:
            volume = max(volume - vol_step, vol_min)
            player.audio_set_volume(volume)
            logging.info("Volume down: %d%%", volume)
            show_overlay("Radio Volume", station=f"Radio: {volume}%", progress=volume)

    def toggle_volume_mode():
        nonlocal sfx_volume_mode
        sfx_volume_mode = not sfx_volume_mode
        mode = "SFX" if sfx_volume_mode else "Radio"
        logging.info("Volume mode: %s", mode)
        show_overlay("Volume Mode", station=f"Controlling: {mode}")

    def next_station():
        nonlocal current_station
        stations = categories[cat_names[current_cat]]
        current_station = (current_station + 1) % len(stations)
        play_current()

    def prev_station():
        nonlocal current_station
        stations = categories[cat_names[current_cat]]
        current_station = (current_station - 1) % len(stations)
        play_current()

    def next_category():
        nonlocal current_cat, current_station
        current_cat = (current_cat + 1) % len(cat_names)
        current_station = 0
        play_current()

    def prev_category():
        nonlocal current_cat, current_station
        current_cat = (current_cat - 1) % len(cat_names)
        current_station = 0
        play_current()

    def _exit_app():
        if _tray_icon:
            try:
                _tray_icon._hide()
            except Exception:
                pass
            try:
                _tray_icon.stop()
            except Exception:
                pass
        stop_sfx()
        player.stop()
        instance.release()
        sfx_instance.release()
        if _overlay:
            _overlay.stop()

    def restart():
        save_state(current_cat, current_station, volume, playing, sfx_file, sfx_volumes)
        _exit_app()
        subprocess.Popen([sys.executable] + sys.argv)
        os._exit(0)

    ACTIONS = {
        "volume_up": volume_up,
        "volume_down": volume_down,
        "prev_station": prev_station,
        "next_station": next_station,
        "toggle_play": toggle_play,
        "next_category": next_category,
        "prev_category": prev_category,
        "restart": restart,
        "toggle_volume_mode": toggle_volume_mode,
        "next_sfx": next_sfx,
    }

    keyboard.add_hotkey('ctrl+shift+num 8', volume_up)
    keyboard.add_hotkey('ctrl+shift+num 2', volume_down)
    keyboard.add_hotkey('ctrl+shift+num 4', prev_station)
    keyboard.add_hotkey('ctrl+shift+num 6', next_station)
    keyboard.add_hotkey('ctrl+shift+num 5', toggle_play)
    keyboard.add_hotkey('ctrl+shift+num 9', next_category)
    keyboard.add_hotkey('ctrl+shift+num 7', prev_category)
    keyboard.add_hotkey('ctrl+shift+num 0', restart)
    keyboard.add_hotkey('ctrl+shift+num *', toggle_volume_mode)
    keyboard.add_hotkey('ctrl+shift+num /', next_sfx)
    def on_tray_help(icon, item):
        help_win = tk.Toplevel()
        help_win.title(f"TrayFM v{__version__} Controls")
        help_win.geometry("380x280")
        help_win.resizable(False, False)
        help_win.attributes("-topmost", True)

        text = tk.Text(help_win, font=("Consolas", 10), bg="#1e1e1e", fg="#d4d4d4",
                       padx=12, pady=12, borderwidth=0, highlightthickness=0)
        text.insert("1.0", f"""  TrayFM v{__version__}

  HOTKEYS (hold Ctrl + Shift + Numpad)

  Num8          Volume Up
  Num2          Volume Down
  Num4          Previous Station
  Num6          Next Station
  Num5          Play / Pause
  Num9          Next Category
  Num7          Previous Category
  Num*          Volume Mode (Radio/SFX)
  Num/          Next SFX
  Num0          Restart App
  Right-click tray icon for more options.

  github.com/GusevNikita/TrayFM
""")
        text.config(state="disabled")
        text.pack(fill="both", expand=True)

        btn = tk.Button(help_win, text="OK", command=help_win.destroy,
                        bg="#333333", fg="#ffffff", bd=0, padx=20, pady=4)
        btn.pack(pady=(0, 10))

        help_win.transient()
        help_win.grab_set()

    def on_tray_open(icon, item):
        os.startfile(CONFIG_PATH)

    def on_tray_open_stations(icon, item):
        os.startfile(STATIONS_PATH)

    def on_tray_restart(icon, item):
        save_state(current_cat, current_station, volume, playing, sfx_file, sfx_volumes)
        _exit_app()
        subprocess.Popen([sys.executable, "-u", __file__], cwd=BASE_DIR)
        os._exit(0)

    def on_tray_exit(icon, item):
        _exit_app()
        os._exit(0)

    AUTORUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
    AUTORUN_NAME = "TrayFM"

    def is_autorun():
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTORUN_KEY, 0, winreg.KEY_READ)
            val, _ = winreg.QueryValueEx(key, AUTORUN_NAME)
            winreg.CloseKey(key)
            return bool(val)
        except FileNotFoundError:
            return False
        except Exception:
            return False

    def toggle_autorun():
        if is_autorun():
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTORUN_KEY, 0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, AUTORUN_NAME)
                winreg.CloseKey(key)
            except FileNotFoundError:
                pass
        else:
            vbs_path = str(BASE_DIR / "run_trayfm_background.vbs")
            if Path(vbs_path).exists():
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTORUN_KEY, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, AUTORUN_NAME, 0, winreg.REG_SZ, vbs_path)
                winreg.CloseKey(key)

    def on_tray_toggle_autorun(icon, item):
        toggle_autorun()
        if _tray_icon:
            _tray_icon.update_menu()

    _tray_icon = pystray.Icon(
        "TrayFM",
        make_icon(),
        f"TrayFM v{__version__}",
        pystray.Menu(
            pystray.MenuItem("Help", on_tray_help),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Open Config", on_tray_open),
            pystray.MenuItem("Open Stations", on_tray_open_stations),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Autorun",
                on_tray_toggle_autorun,
                checked=lambda _: is_autorun(),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Restart", on_tray_restart),
            pystray.MenuItem("Exit", on_tray_exit),
        ),
    )
    threading.Thread(target=_tray_icon.run, daemon=True).start()

    saved_sfx_file = state.get("sfx_file", "")
    saved_sfx_volumes = state.get("sfx_volumes", {})
    if saved_sfx_file and saved_sfx_file in sfx_files:
        sfx_file = saved_sfx_file
        sfx_path = "" if sfx_file == "OFF" else str(Path(sfx_dir) / sfx_file)
    if saved_sfx_volumes:
        sfx_volumes.update(saved_sfx_volumes)
    if sfx_file and sfx_file != "OFF" and sfx_file not in sfx_volumes:
        sfx_volumes[sfx_file] = sfx_def_vol

    print(f"TrayFM v{__version__} started (Ctrl+Shift+Num5 to play)", flush=True)

    if resume:
        play_current()
        start_sfx()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        save_state(current_cat, current_station, volume, playing, sfx_file, sfx_volumes)
        stop_sfx()
        player.stop()
        instance.release()
        sfx_instance.release()
        if _overlay:
            _overlay.stop()
        if _tray_icon:
            _tray_icon.stop()


if __name__ == "__main__":
    main()
