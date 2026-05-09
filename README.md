# 🚀 Clipboard History Manager

### Never Lose Copied Text Again

A lightweight and modern clipboard history manager built completely with **Python + Tkinter** that silently monitors, stores, organizes, and protects everything you copy.

Designed for:

* ⚡ Speed
* 🔒 Privacy
* 🧠 Productivity
* 🪶 Lightweight background usage

---

# 🌟 Why This Project Exists

Ever copied something important...

Then accidentally pressed:

```text
Ctrl + C
```

And everything disappeared forever.

Clipboard History Manager fixes that problem by continuously monitoring clipboard activity in the background and storing copied text safely inside a local database.

No cloud.
No tracking.
No internet dependency.

Just reliable clipboard history.

---

# ✨ Features

## 📋 Clipboard Features

* ✅ Real-time clipboard monitoring
* ✅ Automatic clipboard history saving
* ✅ One-click copy restore
* ✅ Delete clipboard entries
* ✅ Smart duplicate prevention
* ✅ Clipboard history viewer
* ✅ Recent clipboard preview

---

## ⏳ Expiration System

* ✅ Auto-delete entries after 30 days
* ✅ Live expiration countdown
* ✅ Automatic cleanup system
* ✅ Supports up to 1000 clipboard entries

---

## 🖥 Desktop Utility Features

* ✅ Fully Python-powered
* ✅ Built using Tkinter GUI
* ✅ Dark modern interface
* ✅ Background monitoring
* ✅ Thread-safe UI updates
* ✅ Startup-ready architecture
* ✅ PyInstaller executable support
* ✅ Lightweight memory usage

---

# 🪟 Windows Integration

Clipboard History Manager behaves like a native Windows utility.

Includes:

* 🔄 Background clipboard monitoring
* 🚀 Auto-start with Windows
* 📌 System tray integration
* 📉 Minimize-to-tray support
* ⚙ Windows startup integration
* 🧠 Persistent local configuration

Because productivity software should quietly help instead of becoming the problem itself.

---

# 🧠 How It Works

```text
Copy Text
    ↓
Clipboard Detected
    ↓
Saved Into Local JSON Database
    ↓
Displayed Inside App
    ↓
Auto Removed After Expiration
```

Each entry stores:

* Clipboard text
* Creation timestamp
* Expiration timestamp

---

# 🔒 Privacy

All clipboard history is stored locally on your computer.

No:

* ❌ Cloud upload
* ❌ Tracking
* ❌ Telemetry
* ❌ Online storage

Stored locally inside:

```text
C:\clipboardmenu\
```

Files:

```text
clipboard_data.json
config.json
```

Your clipboard stays yours. Revolutionary concept in 2026 software.

---

# ⚙ Tech Stack

| Technology | Purpose               |
| ---------- | --------------------- |
| Python     | Core Application      |
| Tkinter    | Desktop GUI           |
| Threading  | Background Monitoring |
| JSON       | Local Storage         |
| Pyperclip  | Clipboard Access      |
| Pillow     | Tray Icon             |
| Pystray    | System Tray           |
| Winreg     | Windows Startup       |
| Datetime   | Expiration System     |

---

# 📂 Project Structure

```text
ClipboardHistoryManager/
│
├── clipboard_data.json
├── config.json
├── main.py
├── requirements.txt
└── README.md
```

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/ABSMPSOM/clip-board-menu.git
```

## Open Folder

```bash
cd clip-board-menu
```

## Install Requirements

```bash
pip install -r requirements.txt
```

## Run Application

```bash
python main.py
```

---

# 🛠 Export as EXE

```bash
pyinstaller --onefile --windowed main.py
```

Creates a standalone Windows executable.

---

# 🌱 Future Roadmap

* ✅ Clipboard search
* ✅ Pin/Favorite entries
* ✅ Image clipboard support
* ✅ Password-protected history
* ✅ Clipboard categories
* ✅ Export/import support
* ✅ OCR text extraction
* ✅ AI clipboard categorization
* ✅ Cross-device synchronization

---

# ❤️ Built For Productivity

Perfect for:

* 💻 Developers
* 📝 Students
* 📚 Researchers
* ⚡ Productivity users
* 🔐 Anyone tired of losing copied text

---

# 📜 License

MIT License

---

# 👨‍💻 Author

Soumen Sadhukhan

Built with Python because operating systems still somehow treat clipboard history like temporary hallucinations.
