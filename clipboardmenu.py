import tkinter as tk
from tkinter import messagebox
import pyperclip
import json
import os
import sys
import winreg
import threading
import time
import keyboard
from datetime import datetime, timedelta
from PIL import Image, ImageDraw
import pystray

# =========================================================
# COLOR PALETTE
# =========================================================

BG_ROOT   = "#181C14"
BG_WIDGET = "#3C3D37"
BG_ACCENT = "#697565"
FG_TEXT   = "#ECDFCC"
FG_DIM    = "#8a9080"
FG_SELECT = "#ECDFCC"
BG_SELECT = "#697565"
CLR_CLOSE = "#8B2020"

# =========================================================
# PATHS
# =========================================================

APP_FOLDER = r"C:\clipboardmenu"
os.makedirs(APP_FOLDER, exist_ok=True)

DATA_FILE   = os.path.join(APP_FOLDER, "clipboard_data.json")
CONFIG_FILE = os.path.join(APP_FOLDER, "config.json")

# =========================================================
# SETTINGS
# =========================================================

MAX_CLIPBOARD_ITEMS = 1000
DELETE_AFTER_DAYS   = 30
CHECK_INTERVAL      = 1
APP_NAME            = "ClipboardHistoryManager"
STARTUP_REG_KEY     = r"Software\Microsoft\Windows\CurrentVersion\Run"

# =========================================================
# CONFIG
# =========================================================

def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4)

# =========================================================
# WINDOWS STARTUP REGISTRY
# =========================================================

def _exe_path():
    if getattr(sys, "frozen", False):
        return sys.executable
    return f'"{sys.executable}" "{os.path.abspath(__file__)}"'

def add_to_startup():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, STARTUP_REG_KEY,
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, _exe_path())
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"[startup] failed to add registry key: {e}")
        return False

def remove_from_startup():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, STARTUP_REG_KEY,
            0, winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)
    except:
        pass

def is_in_startup():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, STARTUP_REG_KEY,
            0, winreg.KEY_READ
        )
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except:
        return False

# =========================================================
# FIRST-RUN PERMISSION DIALOG (Custom UI)
# =========================================================

class PermissionDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.result = None

        self.overrideredirect(True)
        self.config(bg=BG_WIDGET)
        self.resizable(False, False)

        W, H = 520, 420
        self.update_idletasks()
        sx = (self.winfo_screenwidth()  - W) // 2
        sy = (self.winfo_screenheight() - H) // 2
        self.geometry(f"{W}x{H}+{sx}+{sy}")

        self.grab_set()
        self.lift()
        self._build()

    def _build(self):
        self._dx = self._dy = 0
        self.bind("<ButtonPress-1>",  self._drag_start)
        self.bind("<B1-Motion>",      self._drag_move)

        hdr = tk.Frame(self, bg=BG_ROOT, pady=18)
        hdr.pack(fill="x")
        hdr.bind("<ButtonPress-1>",  self._drag_start)
        hdr.bind("<B1-Motion>",      self._drag_move)

        tk.Label(hdr, text="📋", bg=BG_ROOT, fg=FG_TEXT, font=("Segoe UI Emoji", 26)).pack()
        tk.Label(hdr, text="Clipboard History Manager", bg=BG_ROOT, fg=FG_TEXT, font=("Consolas", 14, "bold")).pack()
        tk.Label(hdr, text="First-time setup", bg=BG_ROOT, fg=FG_DIM, font=("Consolas", 9)).pack()

        tk.Frame(self, bg=BG_ACCENT, height=2).pack(fill="x")

        body = tk.Frame(self, bg=BG_WIDGET, padx=30, pady=20)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Allow the following permissions to get started:", bg=BG_WIDGET, fg=FG_TEXT,
                 font=("Consolas", 10, "bold"), anchor="w").pack(fill="x", pady=(0, 16))

        self._bg_var = tk.BooleanVar(value=True)
        self._make_checkbox(body, var=self._bg_var, icon="👁", title="Run in background",
                            subtitle="Monitor clipboard even when the window is closed.\nAccess it anytime from the system tray.")

        tk.Frame(body, bg=BG_ACCENT, height=1).pack(fill="x", pady=10)

        self._su_var = tk.BooleanVar(value=True)
        self._make_checkbox(body, var=self._su_var, icon="🚀", title="Start automatically with Windows",
                            subtitle="Launch silently at login so your clipboard\nhistory is always available.")

        tk.Frame(self, bg=BG_ACCENT, height=2).pack(fill="x")
        btn_row = tk.Frame(self, bg=BG_WIDGET, pady=14)
        btn_row.pack(fill="x")

        deny = tk.Button(btn_row, text="Deny All", font=("Consolas", 10), bg=BG_ROOT, fg=FG_DIM,
                         activebackground=BG_ROOT, activeforeground=FG_TEXT, relief="flat", bd=0, cursor="hand2", padx=20, pady=8, command=self._deny)
        deny.pack(side=tk.LEFT, padx=(30, 0))

        allow = tk.Button(btn_row, text="Allow & Continue  →", font=("Consolas", 11, "bold"), bg=BG_ACCENT, fg=FG_TEXT,
                          activebackground=BG_ROOT, activeforeground=FG_TEXT, relief="flat", bd=0, cursor="hand2", padx=24, pady=8, command=self._allow)
        allow.pack(side=tk.RIGHT, padx=(0, 30))
        allow.bind("<Enter>", lambda e: allow.config(bg=BG_ROOT))
        allow.bind("<Leave>", lambda e: allow.config(bg=BG_ACCENT))

    def _make_checkbox(self, parent, var, icon, title, subtitle):
        row = tk.Frame(parent, bg=BG_WIDGET)
        row.pack(fill="x", pady=4)

        cb_canvas = tk.Canvas(row, width=22, height=22, bg=BG_WIDGET, highlightthickness=0, bd=0)
        cb_canvas.pack(side=tk.LEFT, padx=(0, 12), anchor="n", pady=2)

        def _draw(checked):
            cb_canvas.delete("all")
            fill = BG_ACCENT if checked else BG_ROOT
            cb_canvas.create_rounded_rectangle = lambda *a, **k: None 
            cb_canvas.create_rectangle(0, 0, 22, 22, fill=fill, outline=BG_ACCENT, width=2)
            if checked:
                cb_canvas.create_line(4, 11, 9, 17, fill=FG_TEXT, width=2)
                cb_canvas.create_line(9, 17, 18, 5, fill=FG_TEXT, width=2)

        _draw(var.get())

        def _toggle(_event=None):
            var.set(not var.get())
            _draw(var.get())

        cb_canvas.bind("<Button-1>", _toggle)

        text_col = tk.Frame(row, bg=BG_WIDGET)
        text_col.pack(side=tk.LEFT, fill="x", expand=True)

        title_row = tk.Frame(text_col, bg=BG_WIDGET)
        title_row.pack(fill="x")

        tk.Label(title_row, text=icon, bg=BG_WIDGET, fg=FG_TEXT, font=("Segoe UI Emoji", 12)).pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(title_row, text=title, bg=BG_WIDGET, fg=FG_TEXT, font=("Consolas", 10, "bold")).pack(side=tk.LEFT)
        tk.Label(text_col, text=subtitle, bg=BG_WIDGET, fg=FG_DIM, font=("Consolas", 8), justify="left", anchor="w").pack(fill="x", padx=(32, 0))

        for w in text_col.winfo_children():
            w.bind("<Button-1>", _toggle)

    def _drag_start(self, event):
        self._dx = event.x_root - self.winfo_x()
        self._dy = event.y_root - self.winfo_y()

    def _drag_move(self, event):
        self.geometry(f"+{event.x_root - self._dx}+{event.y_root - self._dy}")

    def _allow(self):
        self.result = {"background": self._bg_var.get(), "startup": self._su_var.get()}
        self.destroy()

    def _deny(self):
        self.result = {"background": False, "startup": False}
        self.destroy()

def run_first_time_setup(app):
    cfg = load_config()
    if cfg.get("setup_done"):
        if cfg.get("startup") and not is_in_startup():
            add_to_startup()
        return cfg

    dlg = PermissionDialog(app)
    app.wait_window(dlg)

    result = dlg.result or {"background": False, "startup": False}
    if result["startup"]:
        add_to_startup()
    else:
        remove_from_startup()

    cfg.update({
        "setup_done":  True,
        "background":  result["background"],
        "startup":     result["startup"],
    })
    save_config(cfg)
    return cfg

# =========================================================
# DATA MANAGEMENT
# =========================================================

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def remove_expired_data(data):
    now = datetime.now()
    out = []
    for item in data:
        try:
            if now < datetime.strptime(item["expires_at"], "%Y-%m-%d %H:%M:%S"):
                out.append(item)
        except:
            pass
    return out

def get_remaining_time(expires_at):
    try:
        rem = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S") - datetime.now()
        if rem.total_seconds() <= 0:
            return "Expired"
        return f"{rem.days}d {rem.seconds // 3600}h {(rem.seconds % 3600) // 60}m"
    except:
        return "Unknown"

# =========================================================
# CLIPBOARD LOGIC
# =========================================================

def save_clipboard_text(text):
    text = text.strip()
    if not text:
        return
    data = remove_expired_data(load_data())
    if data and data[-1]["text"] == text:
        return
    now = datetime.now()
    data.append({
        "text":       text,
        "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "expires_at": (now + timedelta(days=DELETE_AFTER_DAYS)).strftime("%Y-%m-%d %H:%M:%S"),
    })
    if len(data) > MAX_CLIPBOARD_ITEMS:
        data.pop(0)
    save_data(data)

def refresh_listbox(listbox, preview_box):
    listbox.delete(0, tk.END)
    data = remove_expired_data(load_data())
    save_data(data)
    for item in reversed(data):
        short = item["text"][:50].replace("\n", " ")
        listbox.insert(tk.END, f"  {short}  |  ⏳ {get_remaining_time(item['expires_at'])}")
    preview_box.config(state="normal")
    preview_box.delete(1.0, tk.END)
    preview_box.config(state="disabled")

def show_selected_clipboard(event, listbox, preview_box):
    sel = listbox.curselection()
    if not sel:
        return
    data = list(reversed(remove_expired_data(load_data())))
    item = data[sel[0]]
    preview_box.config(state="normal")
    preview_box.delete(1.0, tk.END)
    preview_box.insert(tk.END, f"📅 Created:    {item['created_at']}\n")
    preview_box.insert(tk.END, f"⏳ Expires In: {get_remaining_time(item['expires_at'])}\n")
    preview_box.insert(tk.END, "─" * 52 + "\n\n")
    preview_box.insert(tk.END, item["text"])
    preview_box.config(state="disabled")

def copy_selected_clipboard(listbox):
    sel = listbox.curselection()
    if not sel:
        return
    data = list(reversed(remove_expired_data(load_data())))
    pyperclip.copy(data[sel[0]]["text"])
    messagebox.showinfo("Copied", "Clipboard item copied successfully.")

def delete_selected_clipboard(listbox, preview_box):
    sel = listbox.curselection()
    if not sel:
        messagebox.showwarning("No Selection", "Please select a clipboard item first.")
        return
    if not messagebox.askyesno("Delete", "Delete this clipboard item?"):
        return
    data = list(reversed(remove_expired_data(load_data())))
    data.pop(sel[0])
    save_data(list(reversed(data)))
    refresh_listbox(listbox, preview_box)

def monitor_clipboard(app, listbox, preview_box):
    last = ""
    while True:
        try:
            cur = pyperclip.paste()
            if isinstance(cur, str):
                cur = cur.strip()
                if cur and cur != last:
                    last = cur
                    save_clipboard_text(cur)
                    app.after(0, refresh_listbox, listbox, preview_box)
        except:
            pass
        time.sleep(CHECK_INTERVAL)

# =========================================================
# SYSTEM TRAY & GLOBAL HOTKEY
# =========================================================

def make_tray_image():
    size = 64
    img  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    dc   = ImageDraw.Draw(img)
    dc.rounded_rectangle([2, 2, size-2, size-2], radius=10, fill="#697565")
    dc.rounded_rectangle([14, 18, 50, 56], radius=4, fill="#ECDFCC")
    dc.rounded_rectangle([22, 12, 42, 24], radius=4, fill="#3C3D37")
    for y in (30, 37, 44):
        dc.rectangle([20, y, 44, y+2], fill="#697565")
    return img

class TrayManager:
    def __init__(self, app):
        self._app  = app
        self._icon = None

    def show_icon(self):
        img  = make_tray_image()
        menu = pystray.Menu(
            pystray.MenuItem("Show",  self._on_show, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit",  self._on_quit),
        )
        self._icon = pystray.Icon(APP_NAME, img, "Clipboard History Manager", menu)
        threading.Thread(target=self._icon.run, daemon=True).start()

    def hide_icon(self):
        if self._icon:
            self._icon.stop()
            self._icon = None

    def _on_show(self, icon=None, item=None):
        self._app.after(0, self._restore)

    def _restore(self):
        self.hide_icon()
        self._app.deiconify()
        self._app.lift()
        self._app.focus_force()

    def _on_quit(self, icon=None, item=None):
        self.hide_icon()
        self._app.after(0, self._app.destroy)

def setup_hotkey(app, tray):
    def toggle_window():
        try:
            if not app.winfo_viewable():
                tray.hide_icon()
                app.deiconify()
                app.lift()
                app.focus_force()
            else:
                app.withdraw()
                tray.show_icon()
        except:
            pass
    keyboard.add_hotkey("windows+alt+c", lambda: app.after(0, toggle_window))

# =========================================================
# UI COMPONENTS
# =========================================================

class DarkScrollbar(tk.Canvas):
    TRACK = BG_ROOT; THUMB = BG_ACCENT; THUMB_HOVER = FG_DIM; W = 10
    def __init__(self, parent, command=None, **kw):
        kw.setdefault("width", self.W); kw.setdefault("bg", self.TRACK)
        kw.setdefault("highlightthickness", 0); kw.setdefault("bd", 0)
        super().__init__(parent, **kw)
        self._command = command
        self._first = 0.0; self._last = 1.0
        self._drag_y = None; self._drag_pos = None; self._hover = False
        self.bind("<Configure>",       self._redraw)
        self.bind("<ButtonPress-1>",   self._press)
        self.bind("<B1-Motion>",       self._drag)
        self.bind("<ButtonRelease-1>", lambda e: setattr(self, "_drag_y", None))
        self.bind("<MouseWheel>",      self._wheel)
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))

    def set(self, first, last):
        self._first = float(first); self._last = float(last); self._redraw()

    def _redraw(self, *_):
        self.delete("all")
        h = self.winfo_height()
        if h < 2: return
        c  = self.THUMB_HOVER if self._hover else self.THUMB
        y0 = int(self._first * h); y1 = max(int(self._last * h), y0 + 20)
        r  = self.W // 2 - 1
        x0, x1 = 1, self.W - 1
        self.create_arc(x0,     y0,     x0+2*r, y0+2*r, start=90,  extent=90,  fill=c, outline=c)
        self.create_arc(x1-2*r, y0,     x1,     y0+2*r, start=0,   extent=90,  fill=c, outline=c)
        self.create_arc(x0,     y1-2*r, x0+2*r, y1,     start=180, extent=90,  fill=c, outline=c)
        self.create_arc(x1-2*r, y1-2*r, x1,     y1,     start=270, extent=90,  fill=c, outline=c)
        self.create_rectangle(x0+r, y0,   x1-r, y1,   fill=c, outline=c)
        self.create_rectangle(x0,   y0+r, x1,   y1-r, fill=c, outline=c)

    def _set_hover(self, v): self._hover = v; self._redraw()

    def _press(self, event):
        self._drag_y = event.y; self._drag_pos = self._first

    def _drag(self, event):
        if self._drag_y is None: return
        h = self.winfo_height()
        p = max(0.0, min(1.0 - (self._last - self._first), self._drag_pos + (event.y - self._drag_y) / h))
        if self._command: self._command("moveto", p)

    def _wheel(self, event):
        if self._command:
            self._command("scroll", -1 if event.delta > 0 else 1, "units")

class CustomTitleBar(tk.Frame):
    def __init__(self, parent, win, tray, title="App", **kw):
        kw.setdefault("bg", BG_WIDGET); kw.setdefault("height", 44)
        super().__init__(parent, **kw)
        self._win = win; self._tray = tray
        self._maximized = False; self._pre_max = None; self._dx = self._dy = 0

        icon_lbl  = tk.Label(self, text="📋", bg=BG_WIDGET, fg=FG_TEXT, font=("Segoe UI Emoji", 14))
        icon_lbl.pack(side=tk.LEFT, padx=(14, 4))

        title_lbl = tk.Label(self, text=title, bg=BG_WIDGET, fg=FG_TEXT, font=("Consolas", 13, "bold"))
        title_lbl.pack(side=tk.LEFT)

        sub_lbl   = tk.Label(self, text="auto-saves · 30-day expiry · 1 000 items", bg=BG_WIDGET, fg=FG_DIM, font=("Consolas", 8))
        sub_lbl.pack(side=tk.LEFT, padx=14)

        btn_kw = dict(bg=BG_WIDGET, fg=FG_TEXT, activeforeground=FG_TEXT, bd=0, relief="flat", font=("Consolas", 12), width=3, cursor="hand2")

        # Explicit: Close button destroys the app
        self._cb = tk.Button(self, text="✕", activebackground=CLR_CLOSE, command=self._close, **btn_kw)
        self._cb.pack(side=tk.RIGHT, ipady=8, ipadx=2)
        self._cb.bind("<Enter>", lambda e: self._cb.config(bg=CLR_CLOSE))
        self._cb.bind("<Leave>", lambda e: self._cb.config(bg=BG_WIDGET))

        self._mb = tk.Button(self, text="⬜", activebackground=BG_ACCENT, command=self._toggle_max, **btn_kw)
        self._mb.pack(side=tk.RIGHT, ipady=8, ipadx=2)
        self._mb.bind("<Enter>", lambda e: self._mb.config(bg=BG_ACCENT))
        self._mb.bind("<Leave>", lambda e: self._mb.config(bg=BG_WIDGET))

        # Explicit: Minimize button sends to tray
        self._nb = tk.Button(self, text="─", activebackground=BG_ACCENT, command=self._minimise, **btn_kw)
        self._nb.pack(side=tk.RIGHT, ipady=8, ipadx=2)
        self._nb.bind("<Enter>", lambda e: self._nb.config(bg=BG_ACCENT))
        self._nb.bind("<Leave>", lambda e: self._nb.config(bg=BG_WIDGET))

        for w in (self, icon_lbl, title_lbl, sub_lbl):
            w.bind("<ButtonPress-1>", self._drag_start)
            w.bind("<B1-Motion>",     self._drag_move)

    def _close(self):
        self._win.destroy()

    def _minimise(self):
        self._win.withdraw()
        self._tray.show_icon()

    def _toggle_max(self):
        if self._maximized:
            self._win.geometry(self._pre_max)
            self._mb.config(text="⬜")
            self._maximized = False
        else:
            self._pre_max = self._win.geometry()
            sw = self._win.winfo_screenwidth(); sh = self._win.winfo_screenheight()
            self._win.geometry(f"{sw}x{sh}+0+0")
            self._mb.config(text="❐")
            self._maximized = True

    def _drag_start(self, event):
        if self._maximized: return
        self._dx = event.x_root - self._win.winfo_x()
        self._dy = event.y_root - self._win.winfo_y()

    def _drag_move(self, event):
        if self._maximized: return
        self._win.geometry(f"+{event.x_root - self._dx}+{event.y_root - self._dy}")

def make_button(parent, text, command):
    btn = tk.Button(parent, text=text, command=command, font=("Consolas", 11, "bold"), width=16, height=2,
                    bg=BG_ACCENT, fg=FG_TEXT, activebackground=BG_WIDGET, activeforeground=FG_TEXT, relief="flat", bd=0, cursor="hand2")
    btn.bind("<Enter>", lambda e: btn.config(bg=BG_WIDGET))
    btn.bind("<Leave>", lambda e: btn.config(bg=BG_ACCENT))
    return btn

def create_ui(app, tray):
    CustomTitleBar(app, app, tray, title="Clipboard History Manager").pack(fill="x")
    tk.Frame(app, bg=BG_ACCENT, height=2).pack(fill="x")

    main_frame = tk.Frame(app, bg=BG_ROOT)
    main_frame.pack(fill="both", expand=True, padx=16, pady=16)

    # LEFT
    left = tk.Frame(main_frame, bg=BG_ROOT)
    left.pack(side=tk.LEFT, fill="both", expand=False)
    tk.Label(left, text="HISTORY", bg=BG_ROOT, fg=FG_DIM, font=("Consolas", 9, "bold"), anchor="w").pack(fill="x", padx=4, pady=(0,4))

    lb_border = tk.Frame(left, bg=BG_ACCENT, padx=1, pady=1)
    lb_border.pack(fill="both", expand=True)

    listbox = tk.Listbox(lb_border, width=56, height=30, bg=BG_WIDGET, fg=FG_TEXT, font=("Consolas", 10),
                         selectbackground=BG_SELECT, selectforeground=FG_SELECT, activestyle="none", relief="flat", bd=0, highlightthickness=0)
    listbox.pack(side=tk.LEFT, fill="both", expand=True)

    sb = DarkScrollbar(lb_border, command=listbox.yview)
    sb.pack(side=tk.RIGHT, fill=tk.Y, padx=(2,0))
    listbox.config(yscrollcommand=sb.set)
    listbox.bind("<MouseWheel>", lambda e: listbox.yview_scroll(-1 if e.delta > 0 else 1, "units"))

    # RIGHT
    right = tk.Frame(main_frame, bg=BG_ROOT)
    right.pack(side=tk.RIGHT, fill="both", expand=True, padx=(16,0))
    tk.Label(right, text="PREVIEW", bg=BG_ROOT, fg=FG_DIM, font=("Consolas", 9, "bold"), anchor="w").pack(fill="x", padx=4, pady=(0,4))

    pb_border = tk.Frame(right, bg=BG_ACCENT, padx=1, pady=1)
    pb_border.pack(fill="both", expand=True)

    preview_box = tk.Text(pb_border, bg=BG_WIDGET, fg=FG_TEXT, insertbackground=FG_TEXT, font=("Consolas", 11),
                          wrap="word", state="disabled", relief="flat", bd=0, highlightthickness=0, padx=12, pady=12)
    preview_box.pack(fill="both", expand=True)

    btn_frame = tk.Frame(right, bg=BG_ROOT)
    btn_frame.pack(pady=(12,0), fill="x")
    make_button(btn_frame, "📋  Copy Again", lambda: copy_selected_clipboard(listbox)).pack(side=tk.LEFT, padx=(0,8))
    make_button(btn_frame, "🗑  Delete", lambda: delete_selected_clipboard(listbox, preview_box)).pack(side=tk.LEFT, padx=(0,8))
    make_button(btn_frame, "🔄  Refresh", lambda: refresh_listbox(listbox, preview_box)).pack(side=tk.LEFT)

    tk.Frame(app, bg=BG_ACCENT, height=2).pack(fill="x")
    status = tk.Frame(app, bg=BG_WIDGET, pady=6)
    status.pack(fill="x")
    tk.Label(status, text="●  Monitoring clipboard [Win+Alt+C to Toggle]", bg=BG_WIDGET, fg=BG_ACCENT, font=("Consolas", 9)).pack(side=tk.LEFT, padx=12)

    listbox.bind("<<ListboxSelect>>", lambda e: show_selected_clipboard(e, listbox, preview_box))
    return listbox, preview_box

# =========================================================
# MAIN
# =========================================================

def main():
    app = tk.Tk()
    app.overrideredirect(True)
    app.config(bg=BG_ROOT)
    app.withdraw()

    app.update_idletasks()
    W, H = 1200, 720
    sx = (app.winfo_screenwidth()  - W) // 2
    sy = (app.winfo_screenheight() - H) // 2
    app.geometry(f"{W}x{H}+{sx}+{sy}")
    app.minsize(900, 600)

    # Setup Check
    run_first_time_setup(app)

    # Show App
    app.deiconify()
    tray = TrayManager(app)
    setup_hotkey(app, tray)

    listbox, preview_box = create_ui(app, tray)
    refresh_listbox(listbox, preview_box)

    threading.Thread(target=monitor_clipboard, args=(app, listbox, preview_box), daemon=True).start()

    app.mainloop()

if __name__ == "__main__":
    main()