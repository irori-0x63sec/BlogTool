# utils/file_io.py
from PySide6.QtWidgets import QFileDialog

def save_markdown_file(title: str, tags: str, body: str):
    title = title.strip() or "Untitled"
    tags = tags.strip()
    body = body.strip()

    save_path, _ = QFileDialog.getSaveFileName(
        None, "Save Markdown", f"{title}.md",
        "Markdown Files (*.md);;All Files (*)"
    )

    if save_path:
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            if tags:
                f.write(f"<!-- Tags: {tags} -->\n\n")
            f.write(body)


def open_markdown_file():
    open_path, _ = QFileDialog.getOpenFileName(
        None, "Open Markdown File", "", "Markdown Files (*.md);;All Files (*)"
    )

    if not open_path:
        return None, None, None

    try:
        with open(open_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        title, tags, body = "", "", ""

        if lines and lines[0].startswith("# "):
            title = lines[0][2:].strip()
            lines = lines[1:]

        # 空行をスキップしながらタグ行を探す
        while lines and lines[0].strip() == "":
            lines = lines[1:]

        if lines and lines[0].strip().startswith("<!-- Tags:"):
            tag_line = lines[0].strip()
            tags = tag_line.replace("<!-- Tags:", "").replace("-->", "").strip()
            lines = lines[1:]

        body = "".join(lines).strip()

        print(f"[DEBUG] Opened file: {open_path}")
        print(f"[DEBUG] title = {title}")
        print(f"[DEBUG] tags = {tags}")
        print(f"[DEBUG] body preview = {body[:50]}...")

        return title, tags, body

    except Exception as e:
        print(f"[ERROR] Failed to open file: {e}")
        return None, None, None

