import random
import threading
import queue
import time
import tkinter as tk
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageTk

BASE_DIR = Path(__file__).parent


class Overlay:
    def __init__(self, gifs_path=None, gifs_enabled=True, vhs_enabled=True, corner="bottom-right", offset_x=20, offset_y=20, theme=None):
        self._queue = queue.Queue()
        self._running = True
        self._root = None
        self._hide_at = 0.0
        self._gifs_enabled = gifs_enabled
        self._vhs_enabled = vhs_enabled
        self._corner = corner
        self._offset_x = offset_x
        self._offset_y = offset_y
        self._gif_frames = []
        self._gif_index = 0
        self._gif_job = None
        self._gif_paths = []
        self._was_hidden = True
        self._theme = theme or {}
        if gifs_enabled and gifs_path:
            gif_dir = Path(gifs_path)
            if gif_dir.exists():
                self._gif_paths = list(gif_dir.glob("*.gif"))
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _vhs_effect(self, frame):
        w, h = frame.size
        r, g, b, a = frame.split()
        shift = 1
        r_img = Image.new("L", (w, h), 0)
        r_img.paste(r, (-shift, 0))
        b_img = Image.new("L", (w, h), 0)
        b_img.paste(b, (shift, 0))
        frame = Image.merge("RGBA", (r_img, g, b_img, a))
        scan = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        for y in range(0, h, 4):
            ImageDraw.Draw(scan).line([(0, y), (w, y)], fill=(0, 0, 0, 20))
        frame = Image.alpha_composite(frame, scan)

        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).rectangle([0, 0, w * 2 // 3, h * 2 // 3], fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(min(w, h) // 3))
        mask = mask.point(lambda x: x // 3)
        white = Image.new("RGBA", (w, h), (255, 255, 255, 255))
        clear = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        glare = Image.composite(white, clear, mask)
        return Image.alpha_composite(frame, glare)

    def _load_gif(self, gif_path):
        self._gif_frames.clear()
        self._gif_index = 0
        try:
            img = Image.open(gif_path)
            target_w = 150
            while True:
                frame = img.copy()
                frame = frame.resize((target_w, int(target_w * frame.size[1] / frame.size[0])), Image.LANCZOS)
                if frame.mode != "RGBA":
                    frame = frame.convert("RGBA")
                if self._vhs_enabled:
                    frame = self._vhs_effect(frame)
                solid = Image.new("RGBA", frame.size, "#222222")
                mask = frame.split()[-1]
                solid.paste(frame.convert("RGB"), (0, 0), mask)
                self._gif_frames.append(ImageTk.PhotoImage(solid))
                img.seek(img.tell() + 1)
        except EOFError:
            pass

    @staticmethod
    def _hex_to_rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    def _make_gradient(self, w, h):
        div = self._theme.get("gradient_divisor", 4)
        base_color = self._hex_to_rgb(self._theme.get("gradient_base", "#222222"))
        hl_color = self._hex_to_rgb(self._theme.get("gradient_highlight", "#ffffff"))
        grad = Image.new("L", (w, h), 0)
        draw = ImageDraw.Draw(grad)
        draw.rectangle([0, 0, w * 2 // 3, h * 2 // 3], fill=255)
        grad = grad.filter(ImageFilter.GaussianBlur(min(w, h) // 2))
        grad = grad.point(lambda x: x // div)
        base = Image.new("RGB", (w, h), base_color)
        highlight = Image.new("RGB", (w, h), hl_color)
        return Image.composite(highlight, base, grad)

    def _pick_new_gif(self):
        if not self._gif_paths:
            return
        self._stop_gif()
        gif_path = random.choice(self._gif_paths)
        self._load_gif(gif_path)
        if self._gif_frames:
            self._canvas.itemconfigure(self._gif_item, image=self._gif_frames[0])
            self._animate_gif()

    def _animate_gif(self):
        if not self._gif_frames:
            return
        self._gif_index = (self._gif_index + 1) % len(self._gif_frames)
        self._canvas.itemconfigure(self._gif_item, image=self._gif_frames[self._gif_index])
        self._gif_job = self._root.after(80, self._animate_gif)

    def _run(self):
        self._root = tk.Tk()
        self._root.withdraw()
        self._root.overrideredirect(True)
        self._root.attributes("-topmost", True)
        self._root.wm_attributes("-disabled", True)

        t = self._theme
        bg = t.get("bg", "#222222")
        border = t.get("border", "#444444")
        bar_bg = t.get("progress_bg", "#333333")
        bar_fill = t.get("progress_fill", "#ffffff")
        bar_w = 100
        bar_h = 6

        ts = t.get("text_status", {})
        ts_font = (ts.get("family", "Segoe UI"), ts.get("size", 20))
        ts_color = ts.get("color", "#ffffff")

        tn = t.get("text_station", {})
        tn_font = (tn.get("family", "Segoe UI"), tn.get("size", 12), tn.get("weight", "bold"))
        tn_color = tn.get("color", "#f0f0f0")

        tc = t.get("text_category", {})
        tc_font = (tc.get("family", "Segoe UI"), tc.get("size", 10))
        tc_color = tc.get("color", "#cccccc")

        ti = t.get("text_info", {})
        ti_font = (ti.get("family", "Segoe UI"), ti.get("size", 9))
        ti_color = ti.get("color", "#aaaaaa")

        self._canvas = tk.Canvas(
            self._root, highlightbackground=border, highlightthickness=1, bg=bg
        )

        self._bg_item = None
        self._bg_img = None

        self._blank_img = ImageTk.PhotoImage(Image.new("RGBA", (1, 1), (0, 0, 0, 0)))
        self._gif_item = self._canvas.create_image(0, 0, image=self._blank_img, anchor="nw", state="hidden")

        self._status_item = self._canvas.create_text(
            0, 0, text="", fill=ts_color, font=ts_font, anchor="center", state="hidden"
        )
        self._station_item = self._canvas.create_text(
            0, 0, text="", fill=tn_color, font=tn_font,
            anchor="center", width=150, state="hidden"
        )
        self._category_item = self._canvas.create_text(
            0, 0, text="", fill=tc_color, font=tc_font,
            anchor="center", width=150, state="hidden"
        )
        self._info_item = self._canvas.create_text(
            0, 0, text="", fill=ti_color, font=ti_font, anchor="center", state="hidden"
        )

        self._progress_bg = self._canvas.create_rectangle(
            0, 0, bar_w, bar_h, fill=bar_bg, outline="", state="hidden"
        )
        self._progress_fill = self._canvas.create_rectangle(
            0, 0, 0, bar_h, fill=bar_fill, outline="", state="hidden"
        )
        self._check_queue()
        self._root.mainloop()

    def _check_queue(self):
        msg = None
        try:
            while True:
                msg = self._queue.get_nowait()
        except queue.Empty:
            pass
        if msg is not None:
            self._show(msg)
        elif self._hide_at and time.time() >= self._hide_at:
            self._hide()
            self._hide_at = 0.0
        if self._running:
            self._root.after(100, self._check_queue)

    def _show(self, msg):
        p = self._theme.get("padding", {})
        padx = p.get("padx", 14)
        pady_top = p.get("pady_top", 10)
        pady_gap = p.get("pady_gap", 30)
        pady_station = p.get("pady_station", 4)
        pady_cat = p.get("pady_cat", 2)
        pady_info = p.get("pady_info", 4)
        pady_progress = p.get("pady_progress", 6)
        pady_bottom = p.get("pady_bottom", 10)

        title = msg.get("title", "")
        show_status = title == "Paused"
        show_volume = title == "Volume"
        show_other = not show_status and not show_volume

        if show_status:
            self._canvas.itemconfigure(self._status_item, text=title.upper())
        show_gif = self._gifs_enabled and (show_volume or show_other)

        station = msg.get("station", "")
        category = msg.get("category", "")
        info = msg.get("info", "")
        progress = msg.get("progress")

        if show_gif and not show_volume:
            self._pick_new_gif()

        if self._gif_frames:
            gif_w = self._gif_frames[0].width()
            gif_h = self._gif_frames[0].height()
        else:
            gif_w, gif_h = 0, 0

        content_w = max(178, gif_w + padx * 2, 100 + padx * 2)
        cx = content_w / 2
        cy = pady_top

        if show_gif:
            self._canvas.itemconfigure(self._status_item, state="hidden")
            gif_x = (content_w - gif_w) // 2
            self._canvas.coords(self._gif_item, gif_x, cy)
            self._canvas.itemconfigure(self._gif_item, state="normal")
            if self._gif_frames:
                if self._gif_job is None:
                    self._animate_gif()
                cy += gif_h + pady_gap
            else:
                cy += pady_gap
        else:
            self._stop_gif()
            self._canvas.itemconfigure(self._gif_item, state="hidden")
            if show_status:
                self._canvas.coords(self._status_item, cx, cy + 16)
                self._canvas.itemconfigure(self._status_item, state="normal")
                cy += 28
            else:
                self._canvas.itemconfigure(self._status_item, state="hidden")

        if show_status:
            for item in [self._station_item, self._category_item, self._info_item]:
                self._canvas.itemconfigure(item, state="hidden")
        else:
            if station:
                self._canvas.coords(self._station_item, cx, cy)
                self._canvas.itemconfigure(self._station_item, text=station, state="normal")
                cy += 18 + pady_cat
            else:
                self._canvas.itemconfigure(self._station_item, state="hidden")

            if category:
                self._canvas.coords(self._category_item, cx, cy)
                self._canvas.itemconfigure(self._category_item, text=category, state="normal")
                cy += 16 + pady_info
            else:
                self._canvas.itemconfigure(self._category_item, state="hidden")

            if info:
                self._canvas.coords(self._info_item, cx, cy)
                self._canvas.itemconfigure(self._info_item, text=info, state="normal")
                cy += 14 + 4
            else:
                self._canvas.itemconfigure(self._info_item, state="hidden")

        if progress is not None:
            pw = max(0, min(100, int(progress * 1)))
            pb_x = (content_w - 100) // 2
            pb_y = cy + pady_progress
            self._canvas.coords(self._progress_bg, pb_x, pb_y, pb_x + 100, pb_y + 6)
            self._canvas.itemconfigure(self._progress_bg, state="normal")
            self._canvas.coords(self._progress_fill, pb_x, pb_y, pb_x + pw, pb_y + 6)
            self._canvas.itemconfigure(self._progress_fill, state="normal")
            cy = pb_y + 6 + pady_bottom
        else:
            for item in [self._progress_bg, self._progress_fill]:
                self._canvas.itemconfigure(item, state="hidden")

        content_h = max(1, cy + 10)

        grad = self._make_gradient(content_w, content_h)
        self._bg_img = ImageTk.PhotoImage(grad)
        if self._bg_item is not None:
            self._canvas.delete(self._bg_item)
        self._bg_item = self._canvas.create_image(0, 0, image=self._bg_img, anchor="nw")
        self._canvas.tag_lower(self._bg_item)

        if not self._canvas.winfo_ismapped():
            self._canvas.pack(fill="both", expand=True)
        self._canvas.configure(width=content_w, height=content_h)

        w = max(170, content_w + 2)
        h = max(1, content_h + 2)
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()
        if self._corner == "top-left":
            x, y = self._offset_x, self._offset_y
        elif self._corner == "top-right":
            x, y = sw - w - self._offset_x, self._offset_y
        elif self._corner == "bottom-left":
            x, y = self._offset_x, sh - h - self._offset_y
        else:
            x, y = sw - w - self._offset_x, sh - h - self._offset_y

        self._root.geometry(f"{w}x{h}+{x}+{y}")
        self._root.deiconify()
        self._root.lift()

        timeout = msg.get("timeout", 3)
        self._hide_at = time.time() + timeout

    def _hide(self):
        if not self._queue.empty():
            self._hide_at = time.time() + 3
            return
        self._root.withdraw()
        self._was_hidden = True

    def notify(self, title, message="", station="", category="", timeout=3, progress=None, info=""):
        self._queue.put(
            {
                "title": title,
                "message": message,
                "station": station,
                "category": category,
                "timeout": timeout,
                "progress": progress,
                "info": info,
            }
        )

    def _stop_gif(self):
        if self._gif_job:
            self._root.after_cancel(self._gif_job)
            self._gif_job = None

    def stop(self):
        self._running = False
        if self._root:
            self._stop_gif()
            self._root.after(0, self._root.quit)
