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

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"
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


def load_state():
    try:
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(cat, station, vol, play):
    try:
        data = {"cat": cat, "station": station, "volume": vol, "playing": play}
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass


def main():
    config = load_config()
    categories = config["categories"]
    vol_step = config["volume_step"]
    vol_min = config["volume_min"]
    vol_max = config["volume_max"]
    vol_default = config.get("volume_default", 50)

    if not categories:
        return

    state = load_state()
    cat_names = list(categories.keys())

    check_timeout = config.get("check_timeout", 10)
    gifs_cfg = config.get("gifs_path", "gifs")
    gifs_path = gifs_cfg if os.path.isabs(gifs_cfg) else str(BASE_DIR / gifs_cfg)
    gifs_enabled = config.get("gifs_enabled", True)
    vhs_enabled = config.get("vhs_enabled", True)
    logs_cfg = config.get("logs_path", "logs")
    logs_path = logs_cfg if os.path.isabs(logs_cfg) else str(BASE_DIR / logs_cfg)
    logs_enabled = config.get("logs_enabled", True)

    if logs_enabled:
        os.makedirs(logs_path, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(logs_path, "trayfm.log"),
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            encoding="utf-8",
        )

    overlay_corner = config.get("overlay_corner", "bottom-right")
    overlay_offset_x = config.get("overlay_offset_x", 20)
    overlay_offset_y = config.get("overlay_offset_y", 20)
    theme = config.get("theme", {})

    proxy = config.get("proxy", "").strip()
    vlc_args = "--no-xlib --quiet"
    if proxy:
        os.environ["all_proxy"] = proxy
        os.environ["http_proxy"] = proxy
        os.environ["https_proxy"] = proxy
        vlc_args += f" --http-proxy={proxy}"

    instance = vlc.Instance(vlc_args)
    player = instance.media_player_new()
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
            _overlay.notify(title, station=station, category=category, timeout=3, progress=progress, info=info)

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
            logging.info("Paused %s - %s", cat_names[current_cat], get_station()["name"])
            show_overlay("Paused", station=get_station()["name"], category=cat_names[current_cat], info=get_info_text())
        else:
            player.play()
            playing = True
            logging.info("Resumed %s - %s", cat_names[current_cat], get_station()["name"])
            show_overlay("", station=get_station()["name"], category=cat_names[current_cat], info=get_info_text())

    def volume_up():
        nonlocal volume
        volume = min(volume + vol_step, vol_max)
        player.audio_set_volume(volume)
        logging.info("Volume up: %d%%", volume)
        show_overlay("Volume", station=f"{volume}%", progress=volume)

    def volume_down():
        nonlocal volume
        volume = max(volume - vol_step, vol_min)
        player.audio_set_volume(volume)
        logging.info("Volume down: %d%%", volume)
        show_overlay("Volume", station=f"{volume}%", progress=volume)

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
        player.stop()
        instance.release()
        if _overlay:
            _overlay.stop()

    def restart():
        save_state(current_cat, current_station, volume, playing)
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
    }

    keyboard.add_hotkey('ctrl+shift+num 8', volume_up)
    keyboard.add_hotkey('ctrl+shift+num 2', volume_down)
    keyboard.add_hotkey('ctrl+shift+num 4', prev_station)
    keyboard.add_hotkey('ctrl+shift+num 6', next_station)
    keyboard.add_hotkey('ctrl+shift+num 5', toggle_play)
    keyboard.add_hotkey('ctrl+shift+num 9', next_category)
    keyboard.add_hotkey('ctrl+shift+num 7', prev_category)
    keyboard.add_hotkey('ctrl+shift+num 0', restart)
    def on_tray_help(icon, item):
        help_win = tk.Toplevel()
        help_win.title("TrayFM Controls")
        help_win.geometry("380x280")
        help_win.resizable(False, False)
        help_win.attributes("-topmost", True)

        text = tk.Text(help_win, font=("Consolas", 10), bg="#1e1e1e", fg="#d4d4d4",
                       padx=12, pady=12, borderwidth=0, highlightthickness=0)
        text.insert("1.0", """  HOTKEYS (hold Ctrl + Shift + Numpad)

  Num8          Volume Up
  Num2          Volume Down
  Num4          Previous Station
  Num6          Next Station
  Num5          Play / Pause
  Num9          Next Category
  Num7          Previous Category
  Num0          Restart App
  Right-click tray icon for more options.
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

    def on_tray_restart(icon, item):
        save_state(current_cat, current_station, volume, playing)
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
        "TrayFM",
        pystray.Menu(
            pystray.MenuItem("Help", on_tray_help),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Open Config", on_tray_open),
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

    print("TrayFM started (Ctrl+Shift+Num5 to play)", flush=True)

    if resume:
        play_current()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        save_state(current_cat, current_station, volume, playing)
        player.stop()
        instance.release()
        if _overlay:
            _overlay.stop()
        if _tray_icon:
            _tray_icon.stop()


if __name__ == "__main__":
    main()
