import importlib
import sys
import os

class I18nManager:
    def __init__(self, language: str):
        self.language = language.lower()
        self.texts = {}

        # 🔥 明示的に i18n モジュールのあるパスを sys.path に追加
        base_path = os.path.dirname(os.path.abspath(__file__))
        i18n_path = os.path.join(base_path, "..", "translates")
        abs_i18n_path = os.path.abspath(i18n_path)

        if abs_i18n_path not in sys.path:
            sys.path.insert(0, abs_i18n_path)
            print("[DEBUG] i18n path added to sys.path:", abs_i18n_path)

    def load(self):
        try:
            module = importlib.import_module(f"i18n.{self.language}")
            self.texts = module.texts
            print("[DEBUG] i18n 読み込み成功:", self.language)
            print("[DEBUG] texts =", self.texts)
        except Exception as e:
            print("[DEBUG] i18n 読み込み失敗:", e)
            self.texts = {}

    def t(self, key: str) -> str:
        return self.texts.get(key, key)
