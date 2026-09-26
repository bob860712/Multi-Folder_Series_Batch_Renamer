import functools
import json
import os
import platform
import re
import threading
import tkinter as tk
from tkinter import messagebox, ttk
import winreg

# 啟用 Windows 高解析度 DPI 支援
try:
  if platform.system() == "Windows":
    import ctypes

    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
  pass

CONFIG_FILE = "Multi-Folder_Series_Batch_Renamer_config.json"

VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".m4v", ".webm"}
SUB_EXTS = {".srt", ".ass", ".sub", ".ssa"}

# 內建多國語言字典
TEXTS = {
    "繁體中文": {
        "title": "多資料夾影集批次重命名工具",
        "lang_label": "語言選擇:",
        "theme_dark": "☀️",
        "theme_light": "🌙",
        "browser_frame": (
            " 1. 內建資料夾樹狀瀏覽器 (雙擊左鍵/右鍵/Enter 可直接匯入) "
        ),
        "col_browser_tree": "資料夾瀏覽器",
        "btn_add_single": "加入選定資料夾",
        "btn_scan_sub": "自動掃描此資料夾下所有子影集",
        "batch_frame": (
            " 2. 已匯入的影集資料夾清單"
            " (雙擊左鍵/右鍵/F2/Enter 可直接修改表格內容) "
        ),
        "btn_remove": "移除選定資料夾",
        "btn_remove_all": "移除所有資料夾",
        "col_folder": "資料夾名稱",
        "col_show": "影集名稱",
        "col_season": "季數",
        "col_count": "檔案數",
        "col_start_ep": "開始集數",
        "col_suffix": "自訂結尾字元",
        "col_path": "路徑",
        "format_frame": " 3. 全局命名格式與自訂字元設定 ",
        "global_suffix_hint": (
            "💡"
            " 提醒：此處的「自訂結尾字元」會作為預設值套用到所有未設定專屬結尾的檔案與資料夾。"
        ),
        "omit_season": "全域省略季數 (例如僅顯示 E01)",
        "omit_e": "全域省略集數前的 'E' 字元 (例如 S0101)",
        "sep_label": "全域分隔符號格式:",
        "sep_choices": {
            "- (緊湊短橫線，前後無空格)": "-",
            " - (標準間距，前後各一空格)": " - ",
            "  -  (寬間距，前後各兩空格)": "  -  ",
            "— (中文破折號)": "—",
            "(僅單一空白字元)": " ",
            "(無分隔符號，直接相連)": "none",
        },
        "sep_default": " - (標準間距，前後各一空格)",
        "suffix_label": "全域自訂結尾字元 (副檔名前):",
        "suffix_hint": "（例如： [1080p] 或 10bit）",
        "preview_frame": " 4. 單一資料夾檔案預覽 ",
        "col_old": "原檔名 (Original)",
        "col_new": "新檔名",
        "btn_execute_all": "開始執行",
        "status_ready": "準備就緒。已自動載入上次路徑與排版習慣。",
        "status_scanned": "成功匯入 {count} 個資料夾。",
        "status_done": "全部重新命名完畢！",
        "err_no_folder": "請先匯入至少一個資料夾！",
    },
    "简体中文": {
        "title": "多文件夹剧集批量重命名工具",
        "lang_label": "语言选择:",
        "theme_dark": "☀️",
        "theme_light": "🌙",
        "browser_frame": (
            " 1. 内置文件夹树状浏览器 (双击左键/右键/Enter 可直接导入) "
        ),
        "col_browser_tree": "文件夹浏览器",
        "btn_add_single": "添加选定文件夹",
        "btn_scan_sub": "自动扫描此文件夹下所有子剧集",
        "batch_frame": (
            " 2. 已导入的剧集文件夹列表"
            " (双击左键/右键/F2/Enter 可修改表格内容) "
        ),
        "btn_remove": "移除选中文件夹",
        "btn_remove_all": "移除所有文件夹",
        "col_folder": "文件夹名称",
        "col_show": "剧集名称",
        "col_season": "季数",
        "col_count": "文件数",
        "col_start_ep": "开始集数",
        "col_suffix": "自定义结尾字符",
        "col_path": "路径",
        "format_frame": " 3. 全局命名格式与自定义字符设置 ",
        "global_suffix_hint": (
            "💡"
            " 提醒：此处的“自定义结尾字符”作为默认值套用到所有未单独设置结尾的文件夹。"
        ),
        "omit_season": "全局省略季数 (例如仅显示 E01)",
        "omit_e": "全局省略集数前的 'E' 字符 (例如 S0101)",
        "sep_label": "全局分隔符格式:",
        "sep_choices": {
            "- (紧凑短横线，前后无空格)": "-",
            " - (标准间距，前后各一空格)": " - ",
            "  -  (宽间距，前后各两空格)": "  -  ",
            "— (中文破折号)": "—",
            "(仅单一空格字符)": " ",
            "(无分隔符，直接相连)": "none",
        },
        "sep_default": " - (标准间距，前后各一空格)",
        "suffix_label": "全局自定义结尾字符 (扩展名前):",
        "suffix_hint": "（例如： [1080p] 或 10bit）",
        "preview_frame": " 4. 单一文件夹文件预览 ",
        "col_old": "原文件名 (Original)",
        "col_new": "新文件名",
        "btn_execute_all": "开始执行",
        "status_ready": "准备就绪。已自动加载上次路径与排版习惯。",
        "status_scanned": "成功导入 {count} 个文件夹。",
        "status_done": "全部重命名完毕！",
        "err_no_folder": "请先导入至少一个文件夹！",
    },
    "English": {
        "title": "Multi-Folder Series Batch Renamer",
        "lang_label": "Language:",
        "theme_dark": "☀️",
        "theme_light": "🌙",
        "browser_frame": (
            " 1. Built-in Folder Browser (Double-click/Right-click/Enter to"
            " import) "
        ),
        "col_browser_tree": "Folder Browser",
        "btn_add_single": "Add Selected Folder",
        "btn_scan_sub": "Auto-scan All Subfolders",
        "batch_frame": (
            " 2. Imported Folder List (Double-click/Right-click/F2/Enter to"
            " edit) "
        ),
        "btn_remove": "Remove Selected",
        "btn_remove_all": "Remove All Folders",
        "col_folder": "Folder Name",
        "col_show": "Show Name",
        "col_season": "Season",
        "col_count": "Files",
        "col_start_ep": "Start Ep",
        "col_suffix": "Custom Suffix",
        "col_path": "Path",
        "format_frame": " 3. Global Format & Custom Suffix ",
        "global_suffix_hint": (
            "💡 Notice: The global suffix applies to folders without"
            " individual custom suffixes."
        ),
        "omit_season": "Globally omit season (e.g., E01 only)",
        "omit_e": "Globally omit 'E' before episode (e.g., S0101)",
        "sep_label": "Global Separator Style:",
        "sep_choices": {
            "- (No spaces around hyphen)": "-",
            " - (Standard space around hyphen)": " - ",
            "  -  (Wide spaces around hyphen)": "  -  ",
            "— (Em dash)": "—",
            "(Single space only)": " ",
            "(None - directly attached)": "none",
        },
        "sep_default": " - (Standard space around hyphen)",
        "suffix_label": "Global Custom Suffix (Before ext):",
        "suffix_hint": "(e.g., [1080p] or 10bit)",
        "preview_frame": " 4. File Preview ",
        "col_old": "Original Name",
        "col_new": "New Name",
        "btn_execute_all": "Start Execution",
        "status_ready": "Ready. Last path and layout restored.",
        "status_scanned": "Successfully imported {count} folders.",
        "status_done": "All renames completed!",
        "err_no_folder": "Please import at least one folder first!",
    },
    "日本語": {
        "title": "複数フォルダ一括アニメ・ドラマリネーマー",
        "lang_label": "言語選択:",
        "theme_dark": "☀️",
        "theme_light": "🌙",
        "browser_frame": (
            " 1. フォルダツリーブラウザ"
            " (ダブルクリック/右クリック/Enterでインポート) "
        ),
        "col_browser_tree": "フォルダブラウザ",
        "btn_add_single": "選択したフォルダを追加",
        "btn_scan_sub": "サブフォルダを自動スキャン",
        "batch_frame": (
            " 2. インポートされたフォルダリスト"
            " (ダブルクリック/右クリック/F2/Enterで編集) "
        ),
        "btn_remove": "選択項目を削除",
        "btn_remove_all": "すべてのフォルダを削除",
        "col_folder": "フォルダ名",
        "col_show": "作品名",
        "col_season": "シーズン",
        "col_count": "ファイル数",
        "col_start_ep": "開始話数",
        "col_suffix": "カスタム接尾辞",
        "col_path": "パス",
        "format_frame": " 3. グローバル命名フォーマット設定 ",
        "global_suffix_hint": (
            "💡 注意：カスタム接尾辞は個別に設定されていないフォルダに適用されます。"
        ),
        "omit_season": "シーズンを省略する (例: E01 のみ)",
        "omit_e": "話数前の 'E' を省略する (例: S0101)",
        "sep_label": "グローバル区切り文字スタイル:",
        "sep_choices": {
            "- (スペースなし)": "-",
            " - (標準スペース)": " - ",
            "  -  (広いスペース)": "  -  ",
            "— (ダッシュ)": "—",
            "(半角スペースのみ)": " ",
            "(なし・直接結合)": "none",
        },
        "sep_default": " - (標準スペース)",
        "suffix_label": "グローバル接尾辞 (拡張子の前):",
        "suffix_hint": "(例: [1080p] や 10bit)",
        "preview_frame": " 4. ファイル名プレビュー ",
        "col_old": "変更前 (Original)",
        "col_new": "変更後 (New)",
        "btn_execute_all": "実行開始",
        "status_ready": "準備完了。前回の設定とパスを復元しました。",
        "status_scanned": "{count} 個のフォルダをインポートしました。",
        "status_done": "全てのリネームが完了しました！",
        "err_no_folder": (
            "先に少なくとも1つのフォルダをインポートしてください！"
        ),
    },
    "한국어": {
        "title": "다중 폴더 시리즈 일괄 이름 변경 도구",
        "lang_label": "언어 선택:",
        "theme_dark": "☀️",
        "theme_light": "🌙",
        "browser_frame": (
            " 1. 폴더 트리 브라우저 (더블 클릭/우클릭/Enter로 가져오기) "
        ),
        "col_browser_tree": "폴더 브라우저",
        "btn_add_single": "선택한 폴더 추가",
        "btn_scan_sub": "하위 폴더 자동 스캔",
        "batch_frame": (
            " 2. 가져온 폴더 목록 (더블 클릭/우클릭/F2/Enter로 편집) "
        ),
        "btn_remove": "선택한 폴더 제거",
        "btn_remove_all": "모든 폴더 제거",
        "col_folder": "폴더 이름",
        "col_show": "작품명",
        "col_season": "시즌",
        "col_count": "파일 수",
        "col_start_ep": "시작 화수",
        "col_suffix": "사용자 지정 접미사",
        "col_path": "경로",
        "format_frame": " 3. 전역 명명 형식 및 접미사 설정 ",
        "global_suffix_hint": (
            "💡 알림: 사용자 지정 접미사는 개별 설정이 없는 폴더에 기본값으로 적용됩니다."
        ),
        "omit_season": "시즌 생략 (예: E01만 표시)",
        "omit_e": "화수 앞의 'E' 문자 생략 (예: S0101)",
        "sep_label": "전역 구분자 형식:",
        "sep_choices": {
            "- (좌우 공백 없음)": "-",
            " - (표준 공백)": " - ",
            "  -  (넓은 공백)": "  -  ",
            "— (줄표)": "—",
            "(단일 공백)": " ",
            "(구분자 없음)": "none",
        },
        "sep_default": " - (표준 공백)",
        "suffix_label": "전역 접미사 (확장자 앞):",
        "suffix_hint": "(예: [1080p] 또는 10bit)",
        "preview_frame": " 4. 파일 이름 미리보기 ",
        "col_old": "원본 이름 (Original)",
        "col_new": "새 이름",
        "btn_execute_all": "실행 시작",
        "status_ready": "준비 완료. 이전 경로 및 레이아웃이 복원되었습니다.",
        "status_scanned": "{count}개의 폴더를 가져왔습니다.",
        "status_done": "모든 이름 변경이 완료되었습니다!",
        "err_no_folder": "먼저 하나 이상의 폴더를 가져와주세요!",
    },
}


def is_system_dark_mode():
  try:
    if platform.system() == "Windows":
      key = winreg.OpenKey(
          winreg.HKEY_CURRENT_USER,
          r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
      )
      value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
      winreg.CloseKey(key)
      return value == 0
    elif platform.system() == "Darwin":
      import subprocess

      res = subprocess.run(
          ["defaults", "read", "-g", "AppleInterfaceStyle"],
          capture_output=True,
          text=True,
      )
      return "Dark" in res.stdout
  except Exception:
    pass
  return False


@functools.lru_cache(maxsize=4096)
def natural_sort_key(s):
  return [
      int(text) if text.isdigit() else text.lower()
      for text in re.split(r"(\d+)", str(s))
  ]


def scan_folder_files(folder_path):
  video_files, sub_files = [], []
  try:
    with os.scandir(folder_path) as entries:
      for entry in entries:
        if entry.is_file():
          ext = os.path.splitext(entry.name)[1].lower()
          if ext in VIDEO_EXTS:
            video_files.append(entry.name)
          elif ext in SUB_EXTS:
            sub_files.append(entry.name)
  except Exception:
    pass
  return sorted(video_files, key=natural_sort_key), sorted(
      sub_files, key=natural_sort_key
  )


class MultiFolderRenamerApp:

  def __init__(self, root):
    self.root = root
    self.root.title("多資料夾影集批次重命名工具")
    self.root.geometry("1100x820")
    self.root.minsize(900, 600)
    self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    self.folders_data = []
    self.selected_folder_index = None
    self.active_entry = None
    self._debounce_timer = None

    self.config = self.load_config()
    self.current_lang = self.config.get("language", "繁體中文")
    self.is_dark_mode = self.config.get("dark_mode", is_system_dark_mode())

    self.create_widgets()
    self.update_texts()
    self.apply_config_values()
    self.apply_theme(self.is_dark_mode)

  def load_config(self):
    if os.path.exists(CONFIG_FILE):
      try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
          return json.load(f)
      except Exception:
        pass
    return {}

  def save_config(self):
    cfg = {
        "language": self.current_lang,
        "omit_season": self.omit_season_var.get(),
        "omit_e": self.omit_e_var.get(),
        "separator": self.sep_combo.get(),
        "suffix": self.suffix_entry.get(),
        "dark_mode": self.is_dark_mode,
        "last_path": getattr(self, "current_browser_path", ""),
    }
    try:
      with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=4)
    except Exception:
      pass

  def on_closing(self):
    self.save_config()
    self.root.destroy()

  def apply_theme(self, dark_mode):
    style = ttk.Style(self.root)
    style.theme_use("clam")

    font_main = ("Microsoft JhengHei", 10)
    font_bold = ("Microsoft JhengHei", 10, "bold")
    font_hint = ("Microsoft JhengHei", 9)
    font_exec = ("Microsoft JhengHei", 11, "bold")

    p = (
        {
            "bg": "#1e1e1e",
            "fg": "#e0e0e0",
            "hint": "#858585",
            "title": "#4fc1ff",
            "btn_bg": "#333333",
            "btn_act": "#404040",
            "field_bg": "#2d2d2d",
            "sel_bg": "#007acc",
            "tree_bg": "#252526",
            "tree_fg": "#d4d4d4",
        }
        if dark_mode
        else {
            "bg": "#f5f5f7",
            "fg": "#1d1d1f",
            "hint": "#6e6e73",
            "title": "#0066cc",
            "btn_bg": "#e4e4e7",
            "btn_act": "#d4d4d8",
            "field_bg": "#ffffff",
            "sel_bg": "#007aff",
            "tree_bg": "#ffffff",
            "tree_fg": "#1d1d1f",
        }
    )

    self.root.configure(bg=p["bg"])
    style.configure(".", background=p["bg"], foreground=p["fg"], font=font_main)
    style.configure("TFrame", background=p["bg"])
    style.configure("TLabel", background=p["bg"], foreground=p["fg"])
    style.configure(
        "Hint.TLabel", background=p["bg"], foreground=p["hint"], font=font_hint
    )
    style.configure("TLabelframe", background=p["bg"], foreground=p["fg"])
    style.configure(
        "TLabelframe.Label", background=p["bg"], foreground=p["title"]
    )

    style.configure("TButton", background=p["btn_bg"], foreground=p["fg"])
    style.map("TButton", background=[("active", p["btn_act"])])

    style.configure("Exec.TButton", font=font_exec)

    style.configure("TCheckbutton", background=p["bg"], foreground=p["fg"])
    style.map("TCheckbutton", background=[("active", p["bg"])])

    for widget in ("TEntry", "TCombobox"):
      style.configure(
          widget,
          fieldbackground=p["field_bg"],
          foreground=p["fg"],
          selectbackground=p["sel_bg"],
      )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", p["field_bg"])],
        foreground=[("readonly", p["fg"])],
        selectbackground=[("readonly", p["sel_bg"])],
        selectforeground=[("readonly", "#ffffff")],
    )

    style.configure(
        "Treeview",
        background=p["tree_bg"],
        fieldbackground=p["tree_bg"],
        foreground=p["tree_fg"],
        rowheight=26,
        font=font_main,
    )
    style.configure(
        "Treeview.Heading",
        background=p["btn_bg"],
        foreground=p["fg"],
        font=font_bold,
    )

    style.map(
        "Treeview",
        background=[("selected", p["sel_bg"])],
        foreground=[("selected", "#ffffff")],
    )

  def toggle_theme(self):
    self.is_dark_mode = not self.is_dark_mode
    self.apply_theme(self.is_dark_mode)
    self.update_theme_button_text()
    self.save_config()

  def update_theme_button_text(self):
    t = TEXTS[self.current_lang]
    self.btn_theme.config(
        text=t["theme_dark"] if self.is_dark_mode else t["theme_light"]
    )

  def close_active_inline_edit(self):
    if self.active_entry:
      entry = self.active_entry
      self.active_entry = None
      try:
        entry.event_generate("<FocusOut>")
      except Exception:
        pass
      try:
        entry.destroy()
      except Exception:
        pass

  def create_widgets(self):
    lang_frame = ttk.Frame(self.root, padding=5)
    lang_frame.pack(fill="x", padx=10, pady=(5, 0))

    self.lang_label_widget = ttk.Label(lang_frame, text="")
    self.lang_label_widget.pack(side="left", padx=5)

    self.lang_combo = ttk.Combobox(
        lang_frame, values=list(TEXTS.keys()), state="readonly", width=12
    )
    self.lang_combo.set(self.current_lang)
    self.lang_combo.pack(side="left", padx=5)
    self.lang_combo.bind("<<ComboboxSelected>>", self.change_language)

    self.status_label = ttk.Label(
        lang_frame, text="", foreground="#007acc", font=("Microsoft JhengHei", 9)
    )
    self.status_label.pack(side="left", padx=15)

    self.btn_theme = ttk.Button(lang_frame, text="", command=self.toggle_theme, width=3)
    self.btn_theme.pack(side="right", padx=5)

    self.btn_execute_all = ttk.Button(
        lang_frame, text="", command=self.execute_all_rename_async, style="Exec.TButton"
    )
    self.btn_execute_all.pack(side="right", padx=5)

    self.main_pane = ttk.PanedWindow(self.root, orient="vertical")
    self.main_pane.pack(fill="both", expand=True, padx=10, pady=5)

    self.browser_frame = ttk.LabelFrame(self.main_pane, padding=5)
    self.main_pane.add(self.browser_frame, weight=1)

    browser_top_box = ttk.Frame(self.browser_frame)
    browser_top_box.pack(fill="x", pady=(0, 3))

    btn_box = ttk.Frame(browser_top_box)
    btn_box.pack(side="left")

    self.btn_add_single = ttk.Button(
        btn_box, text="", command=self.add_selected_browser_folder
    )
    self.btn_add_single.pack(side="left", padx=2)

    self.btn_scan_sub = ttk.Button(
        btn_box, text="", command=self.scan_selected_browser_subfolders
    )
    self.btn_scan_sub.pack(side="left", padx=5)

    tree_container = ttk.Frame(self.browser_frame)
    tree_container.pack(fill="both", expand=True)

    self.fs_tree = ttk.Treeview(
        tree_container, columns=("path",), show="tree", height=4
    )
    fs_scroll = ttk.Scrollbar(
        tree_container, orient="vertical", command=self.fs_tree.yview
    )
    self.fs_tree.configure(yscrollcommand=fs_scroll.set)
    self.fs_tree.pack(side="left", fill="both", expand=True)
    fs_scroll.pack(side="right", fill="y")

    self.fs_tree.bind("<<TreeviewOpen>>", self.on_tree_open)
    self.fs_tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    for ev in ["<Double-1>", "<Return>", "<space>", "<Button-2>", "<Button-3>"]:
      self.fs_tree.bind(ev, self.on_tree_action)

    self.batch_frame = ttk.LabelFrame(self.main_pane, padding=5)
    self.main_pane.add(self.batch_frame, weight=3)

    top_ctrl_box = ttk.Frame(self.batch_frame)
    top_ctrl_box.pack(fill="x", pady=(0, 3))

    self.btn_remove = ttk.Button(
        top_ctrl_box, text="", command=self.remove_selected_folder
    )
    self.btn_remove.pack(side="left", padx=2)

    self.btn_remove_all = ttk.Button(
        top_ctrl_box, text="", command=self.remove_all_folders
    )
    self.btn_remove_all.pack(side="left", padx=2)

    folder_cols = (
        "path",
        "folder_name",
        "show",
        "season",
        "start_ep",
        "suffix",
        "count",
    )
    self.folder_tree = ttk.Treeview(
        self.batch_frame,
        columns=folder_cols,
        show="headings",
        selectmode="extended",
        height=6,
    )

    col_settings = {
        "path": (80, True),
        "folder_name": (280, True),
        "show": (200, True),
        "season": (85, False),
        "start_ep": (110, False),
        "suffix": (140, True),
        "count": (90, False),
    }
    for col, (w, stretch_flag) in col_settings.items():
      self.folder_tree.column(
          col, width=w, minwidth=w if not stretch_flag else 50, stretch=stretch_flag
      )

    folder_scroll = ttk.Scrollbar(
        self.batch_frame, orient="vertical", command=self.folder_tree.yview
    )
    self.folder_tree.configure(yscrollcommand=folder_scroll.set)
    self.folder_tree.pack(side="left", fill="both", expand=True)
    folder_scroll.pack(side="right", fill="y")

    self.folder_tree.bind("<<TreeviewSelect>>", self.on_folder_select)
    self.folder_tree.bind("<Control-a>", self.select_all_folder_tree)
    self.folder_tree.bind("<Command-a>", self.select_all_folder_tree)
    self.folder_tree.bind(
        "<Button-1>", lambda e: self.on_tree_header_click_filter(e)
    )

    for ev in ["<Double-1>", "<Button-2>", "<Button-3>", "<F2>", "<Return>"]:
      self.folder_tree.bind(
          ev,
          lambda e: self.handle_tree_edit_event(
              e, self.folder_tree, [1, 2, 3, 4, 5], self.on_folder_inline_save
          ),
      )

    self.format_frame = ttk.LabelFrame(self.main_pane, padding=5)
    self.main_pane.add(self.format_frame, weight=1)

    self.lbl_global_suffix_hint = ttk.Label(
        self.format_frame, text="", style="Hint.TLabel", wraplength=800
    )
    self.lbl_global_suffix_hint.grid(
        row=0, column=0, columnspan=2, sticky="w", padx=5, pady=(0, 2)
    )

    self.omit_season_var = tk.BooleanVar(value=False)
    self.chk_omit_season = ttk.Checkbutton(
        self.format_frame,
        text="",
        variable=self.omit_season_var,
        command=self.on_setting_change,
    )
    self.chk_omit_season.grid(
        row=1, column=0, columnspan=2, sticky="w", padx=5, pady=1
    )

    self.omit_e_var = tk.BooleanVar(value=False)
    self.chk_omit_e = ttk.Checkbutton(
        self.format_frame,
        text="",
        variable=self.omit_e_var,
        command=self.on_setting_change,
    )
    self.chk_omit_e.grid(
        row=2, column=0, columnspan=2, sticky="w", padx=5, pady=1
    )

    self.lbl_sep = ttk.Label(self.format_frame, text="")
    self.lbl_sep.grid(row=3, column=0, sticky="w", padx=5, pady=1)
    self.sep_combo = ttk.Combobox(
        self.format_frame, state="readonly", width=35
    )
    self.sep_combo.grid(row=3, column=1, sticky="w", padx=5, pady=1)
    self.sep_combo.bind("<<ComboboxSelected>>", self.on_setting_change)

    self.lbl_suffix = ttk.Label(self.format_frame, text="")
    self.lbl_suffix.grid(row=4, column=0, sticky="w", padx=5, pady=1)

    suffix_box = ttk.Frame(self.format_frame)
    suffix_box.grid(row=4, column=1, sticky="w", padx=5, pady=1)
    self.suffix_entry = ttk.Entry(suffix_box, width=22)
    self.suffix_entry.pack(side="left", padx=(0, 5))
    self.suffix_entry.bind("<KeyRelease>", self.on_setting_change_debounced)
    self.lbl_suffix_hint = ttk.Label(
        suffix_box, text="", style="Hint.TLabel"
    )
    self.lbl_suffix_hint.pack(side="left")

    preview_container = ttk.Frame(self.main_pane)
    self.main_pane.add(preview_container, weight=4)

    self.preview_frame = ttk.LabelFrame(
        preview_container, text="", padding=5
    )
    self.preview_frame.pack(fill="both", expand=True, pady=(0, 2))

    preview_cols = ("old", "new")
    self.preview_tree = ttk.Treeview(
        self.preview_frame,
        columns=preview_cols,
        show="headings",
        selectmode="browse",
        height=8,
    )
    for col in preview_cols:
      self.preview_tree.column(col, width=300, stretch=True)

    preview_scroll = ttk.Scrollbar(
        self.preview_frame, orient="vertical", command=self.preview_tree.yview
    )
    self.preview_tree.configure(yscrollcommand=preview_scroll.set)
    self.preview_tree.pack(side="left", fill="both", expand=True)
    preview_scroll.pack(side="right", fill="y")

    self.preview_tree.bind(
        "<Button-1>", lambda e: self.on_tree_header_click_filter(e)
    )
    for ev in ["<Double-1>", "<Button-2>", "<Button-3>", "<F2>", "<Return>"]:
      self.preview_tree.bind(
          ev,
          lambda e: self.handle_tree_edit_event(
              e, self.preview_tree, [1], self.on_preview_inline_save
          ),
      )

    self.init_file_system_browser()

  def on_tree_header_click_filter(self, event):
    region = event.widget.identify_region(event.x, event.y)
    if region == "heading":
      return "break"

  def init_file_system_browser(self):
    self.fs_tree.delete(*self.fs_tree.get_children())
    if platform.system() == "Windows":
      import string

      drives = [
          f"{d}:\\"
          for d in string.ascii_uppercase
          if os.path.exists(f"{d}:\\")
      ]
      for drive in drives:
        node_id = self.fs_tree.insert(
            "", "end", text=drive, values=(drive,), open=False
        )
        self.fs_tree.insert(node_id, "end", text="dummy")
    else:
      node_id = self.fs_tree.insert(
          "", "end", text="/", values=("/",), open=False
      )
      self.fs_tree.insert(node_id, "end", text="dummy")

    last_path = self.config.get("last_path", "")
    if last_path and os.path.exists(last_path):
      self.expand_path_in_browser(last_path)

  def expand_path_in_browser(self, target_path):
    norm_target = os.path.normpath(target_path)
    parts = []
    curr = norm_target
    while True:
      head, tail = os.path.split(curr)
      if not tail:
        parts.append(curr)
        break
      parts.append(tail)
      curr = head
    parts.reverse()

    current_node = ""
    for part in parts:
      children = self.fs_tree.get_children(current_node)
      found = None
      for child in children:
        text = self.fs_tree.item(child, "text")
        vals = self.fs_tree.item(child, "values")
        val_path = vals[0] if vals else ""
        if (
            text.lower() == part.lower()
            or (val_path and os.path.normpath(val_path).lower() == norm_target.lower())
            or (val_path and os.path.normpath(val_path).lower() == os.path.normpath(part).lower())
        ):
          found = child
          break

      if found:
        current_node = found
        self.fs_tree.item(current_node, open=True)
        self.populate_tree_node(current_node)
      else:
        break

    if current_node:
      self.fs_tree.selection_set(current_node)
      self.fs_tree.focus(current_node)
      self.fs_tree.see(current_node)

  def populate_tree_node(self, node_id):
    children = self.fs_tree.get_children(node_id)
    if len(children) == 1 and self.fs_tree.item(children[0], "text") == "dummy":
      self.fs_tree.delete(children[0])
      vals = self.fs_tree.item(node_id, "values")
      if not vals:
        return
      dir_path = vals[0]
      try:
        subdirs = []
        with os.scandir(dir_path) as entries:
          for entry in entries:
            if entry.is_dir():
              subdirs.append(entry.name)
        subdirs.sort(key=natural_sort_key)

        for sub in subdirs:
          full_path = os.path.join(dir_path, sub)
          child_id = self.fs_tree.insert(
              node_id, "end", text=sub, values=(full_path,), open=False
          )
          try:
            with os.scandir(full_path) as sub_entries:
              if any(e.is_dir() for e in sub_entries):
                self.fs_tree.insert(child_id, "end", text="dummy")
          except Exception:
            pass
      except Exception:
        pass

  def on_tree_open(self, event):
    item = self.fs_tree.focus()
    if not item:
      selected = self.fs_tree.selection()
      if selected:
        item = selected[0]
    if item:
      self.populate_tree_node(item)

  def on_tree_select(self, event):
    selected = self.fs_tree.selection()
    if selected:
      vals = self.fs_tree.item(selected[0], "values")
      if vals:
        self.current_browser_path = vals[0]
        self.save_config()

  def on_tree_action(self, event):
    self.close_active_inline_edit()

    if hasattr(event, "x") and hasattr(event, "y"):
      row_id = self.fs_tree.identify_row(event.y)
      if row_id:
        self.fs_tree.selection_set(row_id)
        self.fs_tree.focus(row_id)

    self.add_selected_browser_folder()
    return "break"

  def add_selected_browser_folder(self):
    selected = self.fs_tree.selection()
    if not selected:
      return
    vals = self.fs_tree.item(selected[0], "values")
    if vals:
      self.process_and_add_folder(vals[0])

  def scan_selected_browser_subfolders(self):
    self.close_active_inline_edit()
    selected = self.fs_tree.selection()
    if not selected:
      return
    vals = self.fs_tree.item(selected[0], "values")
    if not vals:
      return
    self.status_label.config(text="正在背景掃描子資料夾...", foreground="#007acc")
    threading.Thread(
        target=self._scan_root_worker, args=(vals[0],), daemon=True
    ).start()

  def process_and_add_folder(self, folder_path):
    if not os.path.exists(folder_path):
      return
    self.status_label.config(
        text="正在背景匯入選定的資料夾...", foreground="#007acc"
    )
    threading.Thread(
        target=self._add_folders_worker, args=([folder_path],), daemon=True
    ).start()

  def _scan_root_worker(self, root_path):
    added_count = 0
    try:
      sub_dirs_raw = []
      with os.scandir(root_path) as entries:
        for e in entries:
          if e.is_dir():
            sub_dirs_raw.append(e.name)
      sub_dirs = [
          os.path.join(root_path, d)
          for d in sorted(sub_dirs_raw, key=natural_sort_key)
      ]
    except Exception:
      sub_dirs = []

    for dirpath in sub_dirs:
      video_files, sub_files = scan_folder_files(dirpath)
      if video_files:
        parent_path = os.path.dirname(dirpath)
        folder_name = os.path.basename(dirpath)

        if any(
            d["path"] == parent_path and d["folder_name"] == folder_name
            for d in self.folders_data
        ):
          continue

        show_name = self.smart_deduce_show_name(
            folder_name, video_files[0] if video_files else None
        )
        season_num = "1"
        s_match = re.search(r"(?:season|s|第)\s*(\d+)", folder_name, re.IGNORECASE)
        if s_match:
          season_num = str(int(s_match.group(1)))

        self.folders_data.append({
            "path": parent_path,
            "folder_name": folder_name,
            "original_folder_name": folder_name,
            "show_name": show_name,
            "season": season_num.zfill(2),
            "start_ep": "1",
            "suffix": "",
            "custom_renames": {},
            "video_files": video_files,
            "sub_files": sub_files,
        })
        added_count += 1

    self.folders_data.sort(
        key=lambda x: (x["path"], natural_sort_key(x["folder_name"]))
    )
    self.root.after(0, lambda: self._on_scan_complete(added_count))

  def _add_folders_worker(self, folders):
    new_items = []
    for folder in folders:
      video_files, sub_files = scan_folder_files(folder)
      parent_path = os.path.dirname(folder)
      folder_name = os.path.basename(folder)
      show_name = self.smart_deduce_show_name(
          folder_name, video_files[0] if video_files else None
      )

      season_num = "1"
      s_match = re.search(r"(?:season|s|第)\s*(\d+)", folder_name, re.IGNORECASE)
      if s_match:
        season_num = str(int(s_match.group(1)))

      new_items.append({
          "path": parent_path,
          "folder_name": folder_name,
          "original_folder_name": folder_name,
          "show_name": show_name,
          "season": season_num.zfill(2),
          "start_ep": "1",
          "suffix": "",
          "custom_renames": {},
          "video_files": video_files,
          "sub_files": sub_files,
      })

    self.root.after(0, lambda: self._on_add_folders_complete(new_items))

  def _on_scan_complete(self, added_count):
    self.refresh_folder_tree()
    children = self.folder_tree.get_children()
    if children:
      self.folder_tree.selection_set(children[-1])
      self.folder_tree.focus(children[-1])

    t = TEXTS[self.current_lang]
    self.status_label.config(
        text=t["status_scanned"].format(count=added_count), foreground="#28a745"
    )

  def _on_add_folders_complete(self, new_items):
    added_count = 0
    for item in new_items:
      if not any(
          d["path"] == item["path"] and d["folder_name"] == item["folder_name"]
          for d in self.folders_data
      ):
        self.folders_data.append(item)
        added_count += 1

    self.folders_data.sort(
        key=lambda x: (x["path"], natural_sort_key(x["folder_name"]))
    )
    self.refresh_folder_tree()
    children = self.folder_tree.get_children()
    if children:
      self.folder_tree.selection_set(children[-1])
      self.folder_tree.focus(children[-1])

    self.status_label.config(
        text=f"已成功新增 {added_count} 個資料夾。", foreground="#28a745"
    )

  def select_all_folder_tree(self, event=None):
    items = self.folder_tree.get_children()
    if items:
      self.folder_tree.selection_set(items)
    return "break"

  def remove_selected_folder(self):
    self.close_active_inline_edit()
    selected = self.folder_tree.selection()
    if not selected:
      return

    indices = sorted(
        [self.folder_tree.index(item_id) for item_id in selected], reverse=True
    )
    for index in indices:
      if 0 <= index < len(self.folders_data):
        del self.folders_data[index]

    self.refresh_folder_tree()
    for item in self.preview_tree.get_children():
      self.preview_tree.delete(item)
    self.selected_folder_index = None

  def remove_all_folders(self):
    self.close_active_inline_edit()
    if not self.folders_data:
      return
    self.folders_data.clear()
    self.refresh_folder_tree()
    for item in self.preview_tree.get_children():
      self.preview_tree.delete(item)
    self.selected_folder_index = None

  def refresh_folder_tree(self):
    for item in self.folder_tree.get_children():
      self.folder_tree.delete(item)

    for data in self.folders_data:
      total_files = len(data.get("video_files", [])) + len(
          data.get("sub_files", [])
      )
      self.folder_tree.insert(
          "",
          "end",
          values=(
              data["path"],
              data["folder_name"],
              data["show_name"],
              data["season"],
              data.get("start_ep", "1"),
              data.get("suffix", ""),
              f"{total_files} 檔案",
          ),
      )

  def change_language(self, event=None):
    self.current_lang = self.lang_combo.get()
    self.update_texts()
    self.save_config()
    self.update_preview()

  def update_texts(self):
    t = TEXTS[self.current_lang]
    self.root.title(t["title"])
    self.lang_label_widget.config(text=t["lang_label"])
    self.update_theme_button_text()

    self.browser_frame.config(text=t["browser_frame"])
    self.fs_tree.heading("#0", text=t["col_browser_tree"])
    self.btn_add_single.config(text=t["btn_add_single"])
    self.btn_scan_sub.config(text=t["btn_scan_sub"])

    self.batch_frame.config(text=t["batch_frame"])
    self.btn_remove.config(text=t["btn_remove"])
    self.btn_remove_all.config(text=t["btn_remove_all"])
    for col in (
        "path",
        "folder_name",
        "show",
        "season",
        "start_ep",
        "suffix",
        "count",
    ):
      self.folder_tree.heading(col, text=t.get(f"col_{col}", col))

    self.format_frame.config(text=t["format_frame"])
    self.lbl_global_suffix_hint.config(text=t["global_suffix_hint"])
    self.chk_omit_season.config(text=t["omit_season"])
    self.chk_omit_e.config(text=t["omit_e"])
    self.lbl_sep.config(text=t["sep_label"])
    self.lbl_suffix.config(text=t["suffix_label"])
    self.lbl_suffix_hint.config(text=t["suffix_hint"])

    choices = list(t["sep_choices"].keys())
    self.sep_combo["values"] = choices
    if self.sep_combo.get() not in choices:
      self.sep_combo.set(t["sep_default"])

    self.preview_frame.config(text=t["preview_frame"])
    self.preview_tree.heading("old", text=t["col_old"])
    self.preview_tree.heading("new", text=t["col_new"])

    self.btn_execute_all.config(text=t["btn_execute_all"])
    self.status_label.config(text=t["status_ready"])

  def apply_config_values(self):
    if "omit_season" in self.config:
      self.omit_season_var.set(self.config["omit_season"])
    if "omit_e" in self.config:
      self.omit_e_var.set(self.config["omit_e"])
    if "separator" in self.config and self.config["separator"]:
      self.sep_combo.set(self.config["separator"])
    if "suffix" in self.config:
      self.suffix_entry.insert(0, self.config["suffix"])

  def smart_deduce_show_name(self, folder_name, sample_file=None):
    clean_folder = re.sub(
        r"\s+",
        " ",
        re.sub(
            r"[\(\[\{].*?[\)\]\]\}]", " ", folder_name.replace(".", " ")
        ).strip(),
    )
    if sample_file:
      sample_base = os.path.splitext(sample_file)[0]
      clean_sample = re.sub(
          r"\s+",
          " ",
          re.sub(
              r"[\(\[\{].*?[\)\]\]\}]", " ", sample_base.replace(".", " ")
          ).strip(),
      )
      import difflib

      match = difflib.SequenceMatcher(
          None, clean_folder, clean_sample
      ).find_longest_match(0, len(clean_folder), 0, len(clean_sample))
      if match.size > 2:
        common = clean_folder[match.a : match.a + match.size].strip()
        if len(common) > 1:
          # 💡 增加清理原則：去除結尾多餘的獨立 "S"、"Season"、"Series" 或孤立符號
          common = re.sub(
              r"\s+(?:s|season|series)$", "", common, flags=re.IGNORECASE
          ).strip()
          return common

    # 若沒有 sample_file 或比對失敗的備用清理
    clean_folder = re.sub(
        r"\s+(?:season|s\d+|s|series).*$", "", clean_folder, flags=re.IGNORECASE
    ).strip()
    return clean_folder if clean_folder else folder_name

  def _start_inline_edit(self, tree, item_id, col_idx, current_val, on_save):
    self.close_active_inline_edit()

    tree.see(item_id)
    self.root.update_idletasks()
    bbox = tree.bbox(item_id, f"#{col_idx+1}")
    if not bbox:
      return

    x, y, width, height = bbox
    entry = ttk.Entry(tree, font=("Microsoft JhengHei", 10))
    entry.place(x=x, y=y, width=max(width, 120), height=height)
    entry.insert(0, current_val)
    entry.select_range(0, tk.END)
    entry.focus()
    self.active_entry = entry

    saved = False

    def save(event=None):
      nonlocal saved
      if saved:
        return "break"
      saved = True
      val = entry.get().strip()
      if self.active_entry == entry:
        self.active_entry = None
      try:
        entry.destroy()
      except Exception:
        pass
      on_save(val)
      return "break"

    entry.bind("<Return>", save)
    entry.bind("<FocusOut>", save)

  def handle_tree_edit_event(self, event, tree, allowed_cols, save_callback):
    self.close_active_inline_edit()

    item_id, col_idx = None, None
    if hasattr(event, "x") and hasattr(event, "y"):
      region = tree.identify("region", event.x, event.y)
      if region == "cell":
        item_id = tree.identify_row(event.y)
        col_str = tree.identify_column(event.x)
        if col_str:
          col_idx = int(col_str.replace("#", "")) - 1

    if item_id:
      tree.selection_set(item_id)
      tree.focus(item_id)
      if tree == self.folder_tree:
        self.selected_folder_index = tree.index(item_id)
        self.update_preview()
    else:
      selected = tree.selection()
      if selected:
        item_id = selected[0]
      else:
        return "break"

    if col_idx is None or col_idx not in allowed_cols:
      col_idx = allowed_cols[0]

    row_index = tree.index(item_id)
    if tree == self.folder_tree:
      keys = ["", "folder_name", "show_name", "season", "start_ep", "suffix"]
      current_val = self.folders_data[row_index].get(keys[col_idx], "")
    else:
      current_val = tree.item(item_id, "values")[1]

    self._start_inline_edit(
        tree,
        item_id,
        col_idx,
        current_val,
        lambda val: save_callback(row_index, col_idx, val, item_id),
    )
    return "break"

  def on_folder_inline_save(self, row_index, col_idx, new_val, item_id):
    keys = ["", "folder_name", "show_name", "season", "start_ep", "suffix"]
    if 0 <= row_index < len(self.folders_data) and col_idx < len(keys):
      self.folders_data[row_index][keys[col_idx]] = new_val

    if self.folder_tree.exists(item_id):
      data = self.folders_data[row_index]
      total_files = len(data.get("video_files", [])) + len(
          data.get("sub_files", [])
      )
      self.folder_tree.item(
          item_id,
          values=(
              data["path"],
              data["folder_name"],
              data["show_name"],
              data["season"],
              data.get("start_ep", "1"),
              data.get("suffix", ""),
              f"{total_files} 檔案",
          ),
      )
    self.update_preview()

  def on_preview_inline_save(self, row_index, col_idx, new_val, item_id):
    if new_val and self.selected_folder_index is not None:
      values = self.preview_tree.item(item_id, "values")
      old_name = values[0]
      data = self.folders_data[self.selected_folder_index]
      if "custom_renames" not in data:
        data["custom_renames"] = {}
      data["custom_renames"][old_name] = new_val

    self.update_preview()

  def on_folder_select(self, event):
    selected = self.folder_tree.selection()
    if selected:
      self.selected_folder_index = self.folder_tree.index(selected[0])
      self.update_preview()

  def on_setting_change(self, event=None):
    if self.selected_folder_index is not None:
      self.update_preview()

  def on_setting_change_debounced(self, event=None):
    if self._debounce_timer:
      self.root.after_cancel(self._debounce_timer)
    self._debounce_timer = self.root.after(150, self.on_setting_change)

  def compute_folder_plan(self, data):
    show_name = data["show_name"]
    season_num = data.get("season", "").strip()
    custom_renames = data.get("custom_renames", {})

    omit_season = self.omit_season_var.get()
    omit_e = self.omit_e_var.get()
    folder_suffix = data.get("suffix", "").strip()
    suffix = (
        folder_suffix
        if folder_suffix != ""
        else self.suffix_entry.get().strip()
    )

    t = TEXTS[self.current_lang]
    actual_sep = t["sep_choices"].get(self.sep_combo.get(), " - ")
    sep = "" if actual_sep == "none" else actual_sep

    video_files = data.get("video_files", [])
    sub_files = data.get("sub_files", [])

    start_ep_val = data.get("start_ep", "1").strip()
    num_match = re.search(r"\d+", start_ep_val)
    start_idx = int(num_match.group()) if num_match else 1
    user_len = len(num_match.group()) if num_match else 1

    pad_len = max(user_len, 3 if (start_idx + len(video_files)) >= 100 else 2)
    suffix_str = f" {suffix}" if suffix else ""

    season_prefix = (
        "" if omit_season else (f"S{season_num}" if season_num else "")
    )
    e_prefix = "" if omit_e else "E"

    plan = []
    video_plan = []

    for idx, filename in enumerate(video_files, start=start_idx):
      ext = os.path.splitext(filename)[1].lower()
      ep_num = str(idx).zfill(pad_len)
      base_name = os.path.splitext(filename)[0]

      new_filename = f"{show_name}{sep}{season_prefix}{e_prefix}{ep_num}{suffix_str}{ext}"
      final_filename = custom_renames.get(filename, new_filename)

      video_plan.append((filename, final_filename, base_name, ep_num))
      plan.append((filename, final_filename))

    for sub_f in sub_files:
      sub_ext = os.path.splitext(sub_f)[1].lower()
      sub_base = os.path.splitext(sub_f)[0]
      matched_ep_num = None

      for _, _, v_base, ep_n in video_plan:
        if sub_base == v_base:
          matched_ep_num = ep_n
          break

      if not matched_ep_num:
        ep_match = re.search(
            r"(?:第\s*(\d+)\s*話|第\s*(\d+)\s*集|[Ee]p?\.?\s*(\d+))", sub_base
        )
        if ep_match:
          groups = [g for g in ep_match.groups() if g is not None]
          if groups:
            target_num = int(groups[0])
            for _, _, _, ep_n in video_plan:
              if int(ep_n) == target_num:
                matched_ep_num = ep_n
                break

      if not matched_ep_num:
        matched_ep_num = str(start_idx).zfill(pad_len)

      new_sub_name = f"{show_name}{sep}{season_prefix}{e_prefix}{matched_ep_num}{suffix_str}{sub_ext}"
      final_sub_name = custom_renames.get(sub_f, new_sub_name)
      plan.append((sub_f, final_sub_name))

    return plan

  def update_preview(self):
    if (
        self.selected_folder_index is None
        or self.selected_folder_index >= len(self.folders_data)
    ):
      return

    self.save_config()
    data = self.folders_data[self.selected_folder_index]
    plan = self.compute_folder_plan(data)

    for item in self.preview_tree.get_children():
      self.preview_tree.delete(item)
    for i, (old_name, new_name) in enumerate(plan):
      self.preview_tree.insert("", "end", values=(old_name, new_name))

  def execute_all_rename_async(self):
    self.close_active_inline_edit()
    t = TEXTS[self.current_lang]
    if not self.folders_data:
      messagebox.showerror("Error", t["err_no_folder"])
      return

    self.save_config()
    total_plans_preview = 0
    all_computed_plans = []

    for data in self.folders_data:
      plan = self.compute_folder_plan(data)
      all_computed_plans.append((data, plan))
      total_plans_preview += len(plan)

    if total_plans_preview == 0:
      messagebox.showinfo("提示", "沒有找到任何需要更名的檔案。")
      return

    conflict_count = 0
    for data, plan in all_computed_plans:
      orig_folder_name = data.get(
          "original_folder_name", data.get("folder_name")
      )
      folder_path = os.path.join(data["path"], orig_folder_name)
      target_names_seen = set()
      for old_name, new_name in plan:
        if old_name == new_name:
          continue
        new_path = os.path.join(folder_path, new_name)
        old_path = os.path.join(folder_path, old_name)
        if (
            new_name in target_names_seen
            or os.path.exists(new_path)
            and os.path.normcase(new_path) != os.path.normcase(old_path)
        ):
          conflict_count += 1
        target_names_seen.add(new_name)

    if conflict_count > 0:
      if not messagebox.askyesno(
          "衝突警告",
          f"檢測到有 {conflict_count}"
          " 個檔案可能存在目標檔名衝突或重複。\n是否仍要繼續執行重新命名？",
      ):
        return

    if not messagebox.askyesno(
        "確認執行",
        f"確定要對全部 {len(self.folders_data)} 個資料夾、共 {total_plans_preview}"
        " 個檔案（含字幕）執行重新命名嗎？",
    ):
      return

    self.status_label.config(text="正在背景執行重新命名...", foreground="#007acc")
    threading.Thread(
        target=self._execute_rename_worker,
        args=(all_computed_plans,),
        daemon=True,
    ).start()

  def _execute_rename_worker(self, all_computed_plans):
    success_total, error_total = 0, 0

    for data, plan in all_computed_plans:
      parent_path = data["path"]
      orig_folder_name = data.get("original_folder_name", data["folder_name"])
      curr_folder_name = data["folder_name"]

      old_dir_path = os.path.join(parent_path, orig_folder_name)
      new_dir_path = os.path.join(parent_path, curr_folder_name)

      if orig_folder_name != curr_folder_name:
        try:
          if os.path.exists(old_dir_path) and not os.path.exists(new_dir_path):
            os.rename(old_dir_path, new_dir_path)
            data["original_folder_name"] = curr_folder_name
          elif os.path.exists(old_dir_path) and os.path.exists(new_dir_path):
            new_dir_path = old_dir_path
            data["folder_name"] = orig_folder_name
        except Exception:
          new_dir_path = old_dir_path

      folder_path = new_dir_path

      for old_name, new_name in plan:
        if old_name == new_name:
          continue
        old_path = os.path.join(folder_path, old_name)
        new_path = os.path.join(folder_path, new_name)
        try:
          if os.path.exists(new_path) and os.path.normcase(
              new_path
          ) != os.path.normcase(old_path):
            error_total += 1
            continue
          os.rename(old_path, new_path)
          success_total += 1
        except Exception:
          error_total += 1

      data["video_files"], data["sub_files"] = scan_folder_files(folder_path)

    self.root.after(
        0, lambda: self._on_rename_complete(success_total, error_total)
    )

  def _on_rename_complete(self, success_total, error_total):
    t = TEXTS[self.current_lang]
    messagebox.showinfo(
        "完成",
        f"全部重新命名完成！\n成功：{success_total} 個檔案\n失敗：{error_total}"
        " 個檔案",
    )
    self.status_label.config(
        text=f"{t['status_done']} (成功: {success_total})", foreground="#28a745"
    )
    self.refresh_folder_tree()
    self.update_preview()


if __name__ == "__main__":
  root = tk.Tk()
  app = MultiFolderRenamerApp(root)
  root.mainloop()