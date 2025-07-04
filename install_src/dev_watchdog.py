import time
import subprocess
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 修正済み：監視対象ディレクトリと起動対象スクリプト
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WATCHED_DIRS = [
    os.path.join(BASE_DIR, "install_src", "gui"),
    os.path.join(BASE_DIR, "install_src", "core"),
    os.path.join(BASE_DIR, "install_src", "platforms"),
]
TARGET_SCRIPT = os.path.join(BASE_DIR, "install_src", "main.py")

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, launch_process_func):
        self.launch_process_func = launch_process_func
        self.process = None
        self.restart()

    def restart(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
        print("[Watchdog] 再起動します...")
        self.process = self.launch_process_func()

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".py"):
            print(f"[Watchdog] 変更検知: {event.src_path}")
            self.restart()

def launch_blogtool():
    return subprocess.Popen(["python", TARGET_SCRIPT])

def main():
    observer = Observer()
    handler = ReloadHandler(launch_blogtool)

    for path in WATCHED_DIRS:
        if os.path.exists(path):
            observer.schedule(handler, path=path, recursive=True)
            print(f"[Watchdog] 監視中: {path}")
        else:
            print(f"[Watchdog] パスが存在しません: {path}")

    observer.start()
    print("[Watchdog] 起動完了。Ctrl+C で終了。")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[Watchdog] 終了中...")
        observer.stop()
        handler.process.terminate()

    observer.join()

if __name__ == "__main__":
    main()
