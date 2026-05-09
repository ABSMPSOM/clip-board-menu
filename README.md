# 🚀 Clipboard History Manager

### *Never Lose Copied Text Again*

### ⚡ Your Clipboard. Supercharged.

A modern **fully Python-powered** clipboard history manager built with **Tkinter** that silently monitors, saves, organizes, and protects everything you copy.

Designed as a lightweight Windows desktop utility focused on:
**speed · stability · privacy · productivity**

---

# 🌟 Why This Project Exists

Ever copied something important...

Then accidentally pressed:

```text
Ctrl + C
```

💀 Gone forever.

Clipboard History Manager fixes that.

The application continuously runs in the background, monitors clipboard activity in real time, stores copied text safely inside a local JSON database, and gives instant access to clipboard history whenever needed.

Minimal. Fast. Reliable. Built for real productivity.

---

# ✨ Core Features

## 📋 Clipboard Management

✅ Real-time clipboard monitoring
✅ Automatic clipboard history saving
✅ Copy clipboard again instantly
✅ Delete selected clipboard items
✅ Smart duplicate prevention system
✅ Full clipboard history viewer
✅ Recent clipboard preview panel

---

## ⏳ Expiration & Cleanup

✅ Live expiration countdown timers
✅ Auto-delete clipboard entries after 30 days
✅ Lightweight automatic cleanup system
✅ Stores up to **1000 clipboard entries**

---

## 🖥 Desktop Utility Features

✅ Fully Python-based desktop application
✅ Built completely with Tkinter GUI
✅ Custom dark-themed modern interface
✅ Background tray-style utility architecture
✅ Multi-threaded background monitoring
✅ Safe threaded UI updates using `root.after()`
✅ Startup-ready Windows utility structure
✅ PyInstaller-ready executable architecture

---

# 🪟 Native Windows Integration

Clipboard History Manager behaves like a real Windows productivity utility.

### Includes:

* 🔄 Silent background monitoring
* 🚀 Auto-start with Windows
* 📌 System tray integration
* 🖱 Custom draggable title bar
* 📉 Minimize-to-tray support
* ⚙ Windows registry startup integration
* 🧠 Persistent configuration management

Designed for long-term background execution with minimal resource usage.

Because software should quietly help instead of screaming for attention every six seconds.

---

# 🖥 Application Preview

```text
📋 Clipboard Captured Successfully
──────────────────────────────────────
> print("Hello World")
> API_KEY=xxxxxxxx
> Meeting Notes...
> Temporary Password...
──────────────────────────────────────
✅ Saved Securely
```

---

# 🧠 How It Works

```text
Copy Text
    ↓
Clipboard Detected
    ↓
Saved Into JSON Database
    ↓
Displayed Inside App
    ↓
Auto Removed After 30 Days
```

Each clipboard entry stores:

* Clipboard text
* Creation timestamp
* Expiry timestamp

The application safely refreshes the UI using thread-safe Tkinter architecture for long-term stability.

---

# 🔒 Privacy & Local Storage

All clipboard history is stored locally on the user's machine.

### No:

❌ Cloud services
❌ Tracking
❌ Telemetry
❌ Internet dependency

Clipboard data is stored inside:

```text
C:\clipboardmenu\
```

Including:

```text
clipboard_data.json
config.json
```

Your copied text stays on your computer.

Radical concept in modern software development.

---

# ⚙ Tech Stack

| Technology | Purpose                     |
| ---------- | --------------------------- |
| Python     | Core Application            |
| Tkinter    | Desktop GUI                 |
| Threading  | Background Monitoring       |
| JSON       | Local Storage               |
| Pyperclip  | Clipboard Access            |
| Pillow     | Tray Icon Rendering         |
| Pystray    | System Tray Support         |
| Winreg     | Windows Startup Integration |
| Datetime   | Expiration System           |

---

# 🚀 Perfect For

💻 Developers storing code snippets
📝 Students saving notes quickly
📚 Researchers collecting references
⚡ Productivity enthusiasts
🔐 Users who hate losing copied text
📋 Anyone who uses Ctrl+C daily

---

# 📂 Project Architecture

```text
ClipboardHistoryManager/
│
├── clipboard_data.json
├── config.json
├── main.py
```

---

# 🚀 Export as Standalone EXE

The project supports exporting into a standalone Windows executable using:

```bash
pyinstaller --onefile --windowed main.py
```

This allows the application to:

✅ Run without Python installed
✅ Auto-launch on startup
✅ Monitor clipboard in background
✅ Behave like a native desktop utility

---

# 🌱 Future Roadmap

* ✅ Clipboard search engine
* ✅ Clipboard pin/favorite system
* ✅ Image clipboard support
* ✅ Password-protected history
* ✅ Clipboard categories & tags
* ✅ Export/import clipboard history
* ✅ Cloud synchronization
* ✅ Cross-device clipboard sync
* ✅ OCR text extraction
* ✅ AI-powered clipboard categorization

---

# 🌱 Contributing

Contributions are welcome.

If you want to improve this project:

⭐ Star the repository
🍴 Fork the project
🐛 Report bugs
🚀 Submit pull requests
💡 Suggest new features

Let’s build smarter desktop productivity tools together.

---

# ❤️ Final Note

Built for everyone who has ever lost important copied text after one accidental `Ctrl + C`.

Because clipboard history should not disappear into the void after a single mistake.

Modern operating systems somehow still haven’t solved this properly. So Python had to step in and parent the clipboard system itself.
