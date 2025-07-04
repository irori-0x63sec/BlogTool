## 📘 Specification Overview (v1.3.1)

BlogTool is a lightweight, cross-platform Markdown blog editor and analytics tool.  
It currently supports mock posting for Qiita and Note, with a plugin architecture for easy platform extension.

### 🖥 GUI Layout
- Main Window: 1000x700px
- Tabs: Editor / Analyze
- Editor Panel:
  - Title: QLineEdit
  - Tags: QLineEdit
  - Markdown Editor: QPlainTextEdit (auto-preview with markdown2)
  - HTML Preview: QLabel (RichText)
- Footer: Open / Save / Post buttons

### ⚙ Preferences
- Path: `~/.BlogTool/Config/preferences.ini`
- Dark mode toggle / Markdown autocompletion toggle
- Stored via `QSettings` in INI format

### 📝 Markdown Processing
- Library: `markdown2`
- Auto-preview triggered after 1s pause in input
- RichText rendering with word wrap

### 💾 Save & Load
- Save format: `.md`
  - 1st line: `# Title`
  - 2nd line: `<!-- Tags: tag1, tag2 -->`
  - Body: Markdown text
- Load parses each section into fields

### 🚀 Posting Architecture
- Plugin-based system via `plugin_loader.py`
- Each platform must define:
```python
def get_publisher() -> BasePublisher
```
- Post action calls .post() on publisher instance
- Example: platforms/qiita/plugin.py, platforms/note/plugin.py

### 📂 Folder Structure
```bash
install_src/
├─ main.py
├─ gui/
│   └─ main_window.py
├─ platforms/
│   ├─ qiita/plugin.py
│   ├─ note/plugin.py
│   └─ base/publisher.py
├─ utils/plugin_loader.py
├─ config/preferences.ini
├─ requirements.txt
```
