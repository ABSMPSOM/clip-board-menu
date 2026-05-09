# =========================================================
# CLIPBOARD HISTORY MANAGER
# Production Ready Version
# =========================================================

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
# STORAGE PATH
# =========================================================

APP_FOLDER = r"C:\clipboardmenu"

os.makedirs(APP_FOLDER, exist_ok=True)

DATA_FILE = os.path.join(
    APP_FOLDER,
    "clipboard_data.json"
)

CONFIG_FILE = os.path.join(
    APP_FOLDER,
    "config.json"
)

# =========================================================
# SETTINGS
# =========================================================

MAX_CLIPBOARD_ITEMS = 1000

DELETE_AFTER_DAYS = 30

CHECK_INTERVAL = 1

APP_NAME = "ClipboardHistoryManager"

STARTUP_REG_KEY = (
    r"Software\Microsoft\Windows\CurrentVersion\Run"
)

# =========================================================
# CONFIG
# =========================================================

def load_config():

    try:

        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except:

        return {}

def save_config(config):

    with open(
        CONFIG_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            config,
            file,
            indent=4
        )

# =========================================================
# STARTUP REGISTRY
# =========================================================

def get_executable_path():

    if getattr(sys, "frozen", False):

        return sys.executable

    return f'"{sys.executable}" "{os.path.abspath(__file__)}"'

def add_to_startup():

    try:

        key = winreg.OpenKey(

            winreg.HKEY_CURRENT_USER,

            STARTUP_REG_KEY,

            0,

            winreg.KEY_SET_VALUE
        )

        winreg.SetValueEx(

            key,

            APP_NAME,

            0,

            winreg.REG_SZ,

            get_executable_path()
        )

        winreg.CloseKey(key)

        return True

    except:

        return False

def remove_from_startup():

    try:

        key = winreg.OpenKey(

            winreg.HKEY_CURRENT_USER,

            STARTUP_REG_KEY,

            0,

            winreg.KEY_SET_VALUE
        )

        winreg.DeleteValue(
            key,
            APP_NAME
        )

        winreg.CloseKey(key)

    except:

        pass

def is_in_startup():

    try:

        key = winreg.OpenKey(

            winreg.HKEY_CURRENT_USER,

            STARTUP_REG_KEY,

            0,

            winreg.KEY_READ
        )

        winreg.QueryValueEx(
            key,
            APP_NAME
        )

        winreg.CloseKey(key)

        return True

    except:

        return False

# =========================================================
# FIRST RUN SETUP
# =========================================================

def first_run_setup():

    config = load_config()

    if config.get("setup_done"):

        return

    permission = messagebox.askyesno(

        "Startup Permission",

        "Do you want Clipboard History Manager\n"
        "to automatically start with Windows?"
    )

    if permission:

        add_to_startup()

    config["setup_done"] = True

    config["startup_enabled"] = permission

    save_config(config)

# =========================================================
# DATA MANAGEMENT
# =========================================================

def load_data():

    if not os.path.exists(DATA_FILE):

        return []

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except:

        return []

def save_data(data):

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

# =========================================================
# REMOVE EXPIRED DATA
# =========================================================

def remove_expired_data(data):

    current_time = datetime.now()

    updated = []

    for item in data:

        try:

            expire_time = datetime.strptime(

                item["expires_at"],

                "%Y-%m-%d %H:%M:%S"
            )

            if current_time < expire_time:

                updated.append(item)

        except:

            pass

    return updated

# =========================================================
# TIMER
# =========================================================

def get_remaining_time(expires_at):

    try:

        expire_time = datetime.strptime(

            expires_at,

            "%Y-%m-%d %H:%M:%S"
        )

        remaining = expire_time - datetime.now()

        if remaining.total_seconds() <= 0:

            return "Expired"

        days = remaining.days

        hours = remaining.seconds // 3600

        minutes = (
            remaining.seconds % 3600
        ) // 60

        return f"{days}d {hours}h {minutes}m"

    except:

        return "Unknown"

# =========================================================
# SAVE CLIPBOARD
# =========================================================

def save_clipboard_text(text):

    text = text.strip()

    if not text:

        return

    data = remove_expired_data(
        load_data()
    )

    # Prevent duplicate consecutive clips
    if data:

        if data[-1]["text"] == text:

            return

    current_time = datetime.now()

    expire_time = current_time + timedelta(
        days=DELETE_AFTER_DAYS
    )

    data.append({

        "text": text,

        "created_at": current_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "expires_at": expire_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    })

    if len(data) > MAX_CLIPBOARD_ITEMS:

        data.pop(0)

    save_data(data)

# =========================================================
# REFRESH LISTBOX
# =========================================================

def refresh_listbox(listbox, preview_box):

    listbox.delete(0, tk.END)

    data = remove_expired_data(
        load_data()
    )

    save_data(data)

    for item in reversed(data):

        short_text = item["text"][:50]

        short_text = short_text.replace(
            "\n",
            " "
        )

        listbox.insert(

            tk.END,

            f"  {short_text}  |  "
            f"⏳ {get_remaining_time(item['expires_at'])}"
        )

    preview_box.config(state="normal")

    preview_box.delete(1.0, tk.END)

    preview_box.config(state="disabled")

# =========================================================
# SHOW SELECTED
# =========================================================

def show_selected_clipboard(

    event,

    listbox,

    preview_box
):

    selected = listbox.curselection()

    if not selected:

        return

    data = list(

        reversed(

            remove_expired_data(
                load_data()
            )
        )
    )

    item = data[selected[0]]

    preview_box.config(state="normal")

    preview_box.delete(1.0, tk.END)

    preview_box.insert(

        tk.END,

        f"📅 Created: "
        f"{item['created_at']}\n"
    )

    preview_box.insert(

        tk.END,

        f"⏳ Expires In: "
        f"{get_remaining_time(item['expires_at'])}\n"
    )

    preview_box.insert(

        tk.END,

        "─" * 60 + "\n\n"
    )

    preview_box.insert(

        tk.END,

        item["text"]
    )

    preview_box.config(state="disabled")

# =========================================================
# COPY CLIPBOARD
# =========================================================

def copy_selected_clipboard(listbox):

    selected = listbox.curselection()

    if not selected:

        return

    data = list(

        reversed(

            remove_expired_data(
                load_data()
            )
        )
    )

    pyperclip.copy(
        data[selected[0]]["text"]
    )

    messagebox.showinfo(

        "Copied",

        "Clipboard copied successfully."
    )

# =========================================================
# DELETE CLIPBOARD
# =========================================================

def delete_selected_clipboard(

    listbox,

    preview_box
):

    selected = listbox.curselection()

    if not selected:

        messagebox.showwarning(

            "No Selection",

            "Please select a clipboard item."
        )

        return

    confirm = messagebox.askyesno(

        "Delete Clipboard",

        "Delete selected clipboard item?"
    )

    if not confirm:

        return

    data = list(

        reversed(

            remove_expired_data(
                load_data()
            )
        )
    )

    data.pop(selected[0])

    save_data(
        list(reversed(data))
    )

    refresh_listbox(
        listbox,
        preview_box
    )

# =========================================================
# MONITOR CLIPBOARD
# =========================================================

def monitor_clipboard(

    app,

    listbox,

    preview_box
):

    last_text = ""

    while True:

        try:

            current_text = pyperclip.paste()

            if isinstance(current_text, str):

                current_text = current_text.strip()

                if current_text:

                    if current_text != last_text:

                        last_text = current_text

                        save_clipboard_text(
                            current_text
                        )

                        app.after(

                            0,

                            refresh_listbox,

                            listbox,

                            preview_box
                        )

        except:

            pass

        time.sleep(CHECK_INTERVAL)

# =========================================================
# TRAY IMAGE
# =========================================================

def create_tray_image():

    image = Image.new(
        "RGB",
        (64, 64),
        BG_ACCENT
    )

    draw = ImageDraw.Draw(image)

    draw.rectangle(
        (16, 16, 48, 48),
        fill=FG_TEXT
    )

    return image

# =========================================================
# TRAY MANAGER
# =========================================================

class TrayManager:

    def __init__(self, app):

        self.app = app

        self.icon = None

    def show_icon(self):

        image = create_tray_image()

        menu = pystray.Menu(

            pystray.MenuItem(
                "Open",
                self.restore_window
            ),

            pystray.MenuItem(
                "Quit",
                self.quit_app
            )
        )

        self.icon = pystray.Icon(

            APP_NAME,

            image,

            APP_NAME,

            menu
        )

        threading.Thread(

            target=self.icon.run,

            daemon=True
        ).start()

    def hide_icon(self):

        if self.icon:

            self.icon.stop()

            self.icon = None

    def restore_window(

        self,

        icon=None,

        item=None
    ):

        self.app.after(

            0,

            self.restore
        )

    def restore(self):

        self.hide_icon()

        self.app.deiconify()

        self.app.lift()

        self.app.focus_force()

    def quit_app(

        self,

        icon=None,

        item=None
    ):

        self.hide_icon()

        self.app.after(
            0,
            self.app.destroy
        )

# =========================================================
# HOTKEY
# =========================================================

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

    keyboard.add_hotkey(

        "windows+alt+c",

        lambda: app.after(
            0,
            toggle_window
        )
    )

# =========================================================
# BUTTON
# =========================================================

def make_button(

    parent,

    text,

    command
):

    button = tk.Button(

        parent,

        text=text,

        command=command,

        font=("Consolas", 11, "bold"),

        width=16,

        height=2,

        bg=BG_ACCENT,

        fg=FG_TEXT,

        activebackground=BG_WIDGET,

        activeforeground=FG_TEXT,

        relief="flat",

        bd=0,

        cursor="hand2"
    )

    return button

# =========================================================
# UI
# =========================================================

def create_ui(app, tray):

    title = tk.Label(

        app,

        text="📋 Clipboard History Manager",

        bg=BG_ROOT,

        fg=FG_TEXT,

        font=("Consolas", 18, "bold")
    )

    title.pack(pady=15)

    main_frame = tk.Frame(
        app,
        bg=BG_ROOT
    )

    main_frame.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=15
    )

    # LEFT
    left = tk.Frame(
        main_frame,
        bg=BG_ROOT
    )

    left.pack(
        side=tk.LEFT,
        fill="both"
    )

    listbox = tk.Listbox(

        left,

        width=55,

        bg=BG_WIDGET,

        fg=FG_TEXT,

        font=("Consolas", 10),

        selectbackground=BG_SELECT,

        selectforeground=FG_SELECT,

        activestyle="none",

        relief="flat",

        bd=0
    )

    listbox.pack(
        fill="both",
        expand=True
    )

    # RIGHT
    right = tk.Frame(
        main_frame,
        bg=BG_ROOT
    )

    right.pack(
        side=tk.RIGHT,
        fill="both",
        expand=True,
        padx=(15, 0)
    )

    preview_box = tk.Text(

        right,

        bg=BG_WIDGET,

        fg=FG_TEXT,

        insertbackground=FG_TEXT,

        font=("Consolas", 11),

        wrap="word",

        state="disabled",

        relief="flat",

        bd=0
    )

    preview_box.pack(
        fill="both",
        expand=True
    )

    # BUTTONS
    button_frame = tk.Frame(
        right,
        bg=BG_ROOT
    )

    button_frame.pack(
        pady=10
    )

    make_button(

        button_frame,

        "📋 Copy Again",

        lambda:
        copy_selected_clipboard(
            listbox
        )
    ).pack(
        side=tk.LEFT,
        padx=5
    )

    make_button(

        button_frame,

        "🗑 Delete",

        lambda:
        delete_selected_clipboard(
            listbox,
            preview_box
        )
    ).pack(
        side=tk.LEFT,
        padx=5
    )

    make_button(

        button_frame,

        "🔄 Refresh",

        lambda:
        refresh_listbox(
            listbox,
            preview_box
        )
    ).pack(
        side=tk.LEFT,
        padx=5
    )

    listbox.bind(

        "<<ListboxSelect>>",

        lambda event:
        show_selected_clipboard(

            event,

            listbox,

            preview_box
        )
    )

    return listbox, preview_box

# =========================================================
# MAIN
# =========================================================

def main():

    app = tk.Tk()

    app.title(APP_NAME)

    app.geometry("1200x700")

    app.minsize(900, 600)

    app.configure(bg=BG_ROOT)

    # First setup
    first_run_setup()

    # Tray
    tray = TrayManager(app)

    # Hotkey
    setup_hotkey(app, tray)

    # UI
    listbox, preview_box = create_ui(
        app,
        tray
    )

    # Initial refresh
    refresh_listbox(
        listbox,
        preview_box
    )

    # Clipboard monitor
    threading.Thread(

        target=monitor_clipboard,

        args=(
            app,
            listbox,
            preview_box
        ),

        daemon=True
    ).start()

    # Minimize to tray
    app.protocol(

        "WM_DELETE_WINDOW",

        lambda: [
            app.withdraw(),
            tray.show_icon()
        ]
    )

    app.mainloop()

# =========================================================
# ENTRY
# =========================================================

if __name__ == "__main__":

    main()