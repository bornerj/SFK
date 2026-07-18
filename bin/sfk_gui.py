#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFK Launcher — standalone GUI for the Structured Framework Kit.

Zero-install: pure Python standard library (Tkinter). No pip packages.
A thin shell over the existing, tested tools:
  - bin/lib/jb_kit_turbo.py      (scaffolder — new project)
  - bin/lib/sfk_updater.py       (add-to-existing / update / migrate)
  - .sfk/kernel/scripts/import_skill.py (import a new skill)

Run:
    python3 bin/sfk_gui.py
"""

from __future__ import annotations

import os
import queue
import subprocess
import sys
import threading
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import filedialog, font as tkfont, messagebox, ttk
except ModuleNotFoundError:
    print(
        "\nERRO: o Tkinter não está instalado neste Python.\n"
        "O SFK Launcher precisa dele para abrir a janela (é uma peça padrão do\n"
        "Python, mas algumas distros Linux a distribuem separadamente).\n\n"
        "Instale com um dos comandos abaixo, conforme seu sistema, e tente de novo:\n"
        "  Debian/Ubuntu/Zorin/Mint:  sudo apt install python3-tk\n"
        "  Fedora/RHEL:               sudo dnf install python3-tkinter\n"
        "  Arch/Manjaro:              sudo pacman -S tk\n"
        "  macOS (via Homebrew):      brew install python-tk\n",
        file=sys.stderr,
    )
    raise SystemExit(1)

# ---------------------------------------------------------------------------
# Paths — locate the SFK repo from this file's location
# ---------------------------------------------------------------------------

BIN_DIR = Path(__file__).resolve().parent
SFK_ROOT = BIN_DIR.parent
SCAFFOLDER = BIN_DIR / "lib" / "jb_kit_turbo.py"
UPDATER = BIN_DIR / "lib" / "sfk_updater.py"
SKILL_IMPORTER = SFK_ROOT / ".sfk" / "kernel" / "scripts" / "import_skill.py"
SKILLS_DIR = SFK_ROOT / ".sfk" / "kernel" / "skills"

PYTHON = sys.executable or "python3"

sys.path.insert(0, str(BIN_DIR / "lib"))
from gui_i18n import Lang  # noqa: E402 — needs BIN_DIR/lib on sys.path first


def open_folder(path: str) -> None:
    """Open a folder in the OS's file manager, cross-platform."""
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception:
        pass  # best-effort convenience action; never worth crashing over


# ---------------------------------------------------------------------------
# Design system — sober, high-contrast, warm-neutral base + teal accent.
# Deliberately not dark+neon, not purple: a trustworthy utility tone.
# The console panel is the one dark surface in the app (signature moment).
# ---------------------------------------------------------------------------

class Theme:
    BG = "#F7F5F0"            # warm off-white app background
    CARD_BG = "#FFFFFF"
    CARD_BORDER = "#E1DCCF"
    CARD_HOVER = "#EFF7F4"
    TEXT = "#1C2422"          # near-black warm ink
    TEXT_MUTED = "#5B6663"
    ACCENT = "#0F6B5C"        # deep teal — trust + growth
    ACCENT_HOVER = "#0B5347"
    ACCENT_SOFT = "#E4F0ED"
    DANGER = "#B3401F"        # warm terracotta, not pure red
    DANGER_SOFT = "#F5E7E1"
    BORDER = "#DDD8CC"
    CONSOLE_BG = "#12211D"
    CONSOLE_FG = "#D9F2EA"
    CONSOLE_MUTED = "#7FA79A"
    CONSOLE_ACCENT = "#59D9B3"
    CONSOLE_ERROR = "#F2A28A"

    SPACE_XS = 3
    SPACE_SM = 6
    SPACE_MD = 12
    SPACE_LG = 18
    SPACE_XL = 24


def resolve_font(root: tk.Tk, candidates: list[str], size: int, weight: str = "normal") -> tkfont.Font:
    """Pick the first available font family from candidates, else fall back
    to the platform default. Keeps a native, trustworthy feel without
    bundling font files (stays zero-install)."""
    available = set(tkfont.families(root))
    for name in candidates:
        if name in available:
            return tkfont.Font(family=name, size=size, weight=weight)
    return tkfont.Font(family=tkfont.nametofont("TkDefaultFont").actual("family"), size=size, weight=weight)


UI_FONT_CANDIDATES = ["Segoe UI", "Ubuntu", "Cantarell", "SF Pro Text", "Helvetica Neue", "DejaVu Sans"]
MONO_FONT_CANDIDATES = ["Cascadia Mono", "JetBrains Mono", "Consolas", "DejaVu Sans Mono", "Menlo", "Courier New"]


class Fonts:
    """Populated once the root window exists (font.families needs a Tk instance)."""
    title: tkfont.Font
    h1: tkfont.Font
    h2: tkfont.Font
    body: tkfont.Font
    body_bold: tkfont.Font
    small: tkfont.Font
    mono: tkfont.Font

    @classmethod
    def load(cls, root: tk.Tk) -> None:
        cls.title = resolve_font(root, UI_FONT_CANDIDATES, 18, "bold")
        cls.h1 = resolve_font(root, UI_FONT_CANDIDATES, 13, "bold")
        cls.h2 = resolve_font(root, UI_FONT_CANDIDATES, 11, "bold")
        cls.body = resolve_font(root, UI_FONT_CANDIDATES, 10, "normal")
        cls.body_bold = resolve_font(root, UI_FONT_CANDIDATES, 10, "bold")
        cls.small = resolve_font(root, UI_FONT_CANDIDATES, 8, "normal")
        cls.mono = resolve_font(root, MONO_FONT_CANDIDATES, 9, "normal")


# ---------------------------------------------------------------------------
# Process runner — runs a script in a background thread, streams output
# through a queue so the UI thread can poll it via `after()` without blocking.
# ---------------------------------------------------------------------------

class ProcessRunner:
    def __init__(self, on_line, on_done):
        self.on_line = on_line
        self.on_done = on_done
        self._proc: subprocess.Popen | None = None
        self._queue: queue.Queue[str | None] = queue.Queue()
        self._thread: threading.Thread | None = None

    def run(self, args: list[str]) -> None:
        self._thread = threading.Thread(target=self._worker, args=(args,), daemon=True)
        self._thread.start()
        self._poll()

    def _worker(self, args: list[str]) -> None:
        try:
            self._proc = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=str(SFK_ROOT),
            )
            assert self._proc.stdout is not None
            for line in self._proc.stdout:
                self._queue.put(line.rstrip("\n"))
            code = self._proc.wait()
            self._queue.put(None)
            self._queue.put(f"__EXIT__{code}")
        except Exception as exc:  # surfaced to the console panel
            self._queue.put(f"ERROR: {exc}")
            self._queue.put(None)
            self._queue.put("__EXIT__1")

    def _poll(self) -> None:
        try:
            while True:
                item = self._queue.get_nowait()
                if item is None:
                    continue
                if isinstance(item, str) and item.startswith("__EXIT__"):
                    code = int(item.replace("__EXIT__", "") or "1")
                    self.on_done(code)
                    return
                self.on_line(item)
        except queue.Empty:
            pass
        # Reschedule on the Tk main loop (caller owns a widget to schedule on).
        self._after_id = _GLOBAL_ROOT.after(80, self._poll)


_GLOBAL_ROOT: tk.Tk  # set in main(); used by ProcessRunner to reschedule polling


# ---------------------------------------------------------------------------
# Reusable widgets
# ---------------------------------------------------------------------------

class ActionCard(tk.Canvas):
    """A large, self-explanatory action card: icon + title + subtitle.
    Drawn on a Canvas (rounded rect) instead of a stock button — a small
    custom touch instead of an all-default look."""

    RADIUS = 12

    def __init__(self, parent, icon: str, title: str, subtitle: str, command, **kw):
        super().__init__(parent, bg=Theme.BG, highlightthickness=0, height=72, **kw)
        self._command = command
        self._hover = False
        self.bind("<Configure>", self._redraw)
        self.bind("<Button-1>", lambda _e: self._command())
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.configure(cursor="hand2")
        self._icon, self._title, self._subtitle = icon, title, subtitle

    def set_texts(self, title: str, subtitle: str) -> None:
        self._title, self._subtitle = title, subtitle
        self._redraw()

    def _on_enter(self, _e=None):
        self._hover = True
        self._redraw()

    def _on_leave(self, _e=None):
        self._hover = False
        self._redraw()

    def _rounded_rect(self, x1, y1, x2, y2, r, **kw):
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kw)

    def _redraw(self, _e=None):
        self.delete("all")
        w = self.winfo_width() or 400
        h = self.winfo_height() or 72
        fill = Theme.CARD_HOVER if self._hover else Theme.CARD_BG
        border = Theme.ACCENT if self._hover else Theme.CARD_BORDER
        self._rounded_rect(2, 2, w - 2, h - 2, self.RADIUS, fill=fill, outline=border, width=1.5)
        self.create_text(24, h / 2, text=self._icon, font=("", 20), anchor="w", fill=Theme.ACCENT)
        self.create_text(64, h / 2 - 9, text=self._title, font=Fonts.h1, anchor="w", fill=Theme.TEXT)
        self.create_text(64, h / 2 + 9, text=self._subtitle, font=Fonts.body, anchor="w", fill=Theme.TEXT_MUTED,
                          width=w - 88)


class PrimaryButton(tk.Label):
    """Solid accent button (Label-based for full color control on all platforms)."""

    def __init__(self, parent, text, command, danger=False, enabled=True, **kw):
        self._bg = Theme.DANGER if danger else Theme.ACCENT
        self._bg_hover = "#8C3117" if danger else Theme.ACCENT_HOVER
        self._command = command
        self._enabled = enabled
        super().__init__(
            parent, text=f"  {text}  ", font=Fonts.body_bold, fg="white",
            bg=self._bg if enabled else Theme.BORDER, padx=Theme.SPACE_SM, pady=Theme.SPACE_XS,
            cursor="hand2" if enabled else "arrow", **kw,
        )
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        self.configure(bg=self._bg if enabled else Theme.BORDER, cursor="hand2" if enabled else "arrow")

    def set_text(self, text: str) -> None:
        self.configure(text=f"  {text}  ")

    def _on_click(self, _e=None):
        if self._enabled:
            self._command()

    def _on_enter(self, _e=None):
        if self._enabled:
            self.configure(bg=self._bg_hover)

    def _on_leave(self, _e=None):
        if self._enabled:
            self.configure(bg=self._bg)


class SecondaryButton(tk.Label):
    def __init__(self, parent, text, command, **kw):
        self._command = command
        super().__init__(
            parent, text=f"  {text}  ", font=Fonts.body, fg=Theme.TEXT, bg=Theme.BG,
            padx=Theme.SPACE_SM, pady=Theme.SPACE_XS, cursor="hand2",
            highlightbackground=Theme.BORDER, highlightthickness=1, **kw,
        )
        self.bind("<Button-1>", lambda _e: self._command())
        self.bind("<Enter>", lambda _e: self.configure(bg=Theme.CARD_HOVER))
        self.bind("<Leave>", lambda _e: self.configure(bg=Theme.BG))

    def set_text(self, text: str) -> None:
        self.configure(text=f"  {text}  ")


class PathPicker(tk.Frame):
    """Entry + 'Procurar…' button — the user never types a path by hand."""

    def __init__(self, parent, initial: str = "", **kw):
        super().__init__(parent, bg=Theme.BG, **kw)
        self.var = tk.StringVar(value=initial)
        entry = tk.Entry(
            self, textvariable=self.var, font=Fonts.body, fg=Theme.TEXT, bg="white",
            relief="flat", highlightthickness=1, highlightbackground=Theme.BORDER,
            highlightcolor=Theme.ACCENT, insertbackground=Theme.TEXT,
        )
        entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, Theme.SPACE_SM))
        self.browse_btn = SecondaryButton(self, Lang.t("common.browse"), self._browse)
        self.browse_btn.pack(side="left")

    def _browse(self) -> None:
        path = filedialog.askdirectory(title=Lang.t("common.choose_folder_dialog"), mustexist=False)
        if path:
            self.var.set(path)

    def get(self) -> str:
        return self.var.get().strip()

    def retranslate(self) -> None:
        self.browse_btn.set_text(Lang.t("common.browse"))


class ConsolePanel(tk.Frame):
    """Read-only, live-updating console. The one dark surface in the app —
    gives real terminal output honest visibility (transparency by design)."""

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=Theme.CONSOLE_BG, **kw)
        self.text = tk.Text(
            self, bg=Theme.CONSOLE_BG, fg=Theme.CONSOLE_FG, font=Fonts.mono,
            relief="flat", wrap="word", state="disabled", padx=Theme.SPACE_MD, pady=Theme.SPACE_SM,
            insertbackground=Theme.CONSOLE_FG,
        )
        scroll = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=scroll.set)
        self.text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.text.tag_configure("muted", foreground=Theme.CONSOLE_MUTED)
        self.text.tag_configure("accent", foreground=Theme.CONSOLE_ACCENT)
        self.text.tag_configure("error", foreground=Theme.CONSOLE_ERROR)

    def clear(self) -> None:
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")

    def append(self, line: str, tag: str | None = None) -> None:
        self.text.configure(state="normal")
        self.text.insert("end", line + "\n", tag or ())
        self.text.see("end")
        self.text.configure(state="disabled")


class Header(tk.Frame):
    def __init__(self, parent, title: str, subtitle: str, on_back=None, **kw):
        super().__init__(parent, bg=Theme.BG, **kw)
        row = tk.Frame(self, bg=Theme.BG)
        row.pack(fill="x", padx=Theme.SPACE_XL, pady=(Theme.SPACE_LG, Theme.SPACE_SM))
        self.back_btn = None
        if on_back:
            self.back_btn = SecondaryButton(row, Lang.t("common.back"), on_back)
            self.back_btn.pack(side="left", padx=(0, Theme.SPACE_MD))
        text_col = tk.Frame(row, bg=Theme.BG)
        text_col.pack(side="left", fill="x", expand=True)
        self.title_label = tk.Label(text_col, text=title, font=Fonts.title, fg=Theme.TEXT, bg=Theme.BG)
        self.title_label.pack(anchor="w")
        self.subtitle_label = tk.Label(text_col, text=subtitle, font=Fonts.body, fg=Theme.TEXT_MUTED, bg=Theme.BG)
        self.subtitle_label.pack(anchor="w")
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=Theme.SPACE_XL, pady=(Theme.SPACE_SM, 0))

    def set_texts(self, title: str, subtitle: str) -> None:
        self.title_label.configure(text=title)
        self.subtitle_label.configure(text=subtitle)

    def retranslate(self) -> None:
        if self.back_btn:
            self.back_btn.set_text(Lang.t("common.back"))


class ResultBanner(tk.Frame):
    """Success/error banner shown after an action finishes, with an optional
    'Abrir pasta' shortcut — closes the loop from action to seeing the result."""

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=Theme.BG, **kw)
        self._strip = tk.Frame(self, bg=Theme.ACCENT, width=4)
        self._strip.pack(side="left", fill="y")
        self._content = tk.Frame(self, bg=Theme.ACCENT_SOFT)
        self._content.pack(side="left", fill="both", expand=True)
        self._label = tk.Label(
            self._content, text="", font=Fonts.body_bold, fg=Theme.TEXT, bg=Theme.ACCENT_SOFT,
            justify="left", anchor="w", wraplength=560,
        )
        self._label.pack(side="left", fill="x", expand=True, padx=Theme.SPACE_MD, pady=Theme.SPACE_SM)
        self._action_slot = tk.Frame(self._content, bg=Theme.ACCENT_SOFT)
        self._action_slot.pack(side="right", padx=Theme.SPACE_MD)
        self.pack_forget()

    def show_success(self, message: str, on_open_folder=None, before=None) -> None:
        self._render(message, ok=True, on_open_folder=on_open_folder, before=before)

    def show_error(self, message: str, before=None) -> None:
        self._render(message, ok=False, on_open_folder=None, before=before)

    def _render(self, message: str, ok: bool, on_open_folder, before=None) -> None:
        color = Theme.ACCENT if ok else Theme.DANGER
        soft = Theme.ACCENT_SOFT if ok else Theme.DANGER_SOFT
        self._strip.configure(bg=color)
        for child in self._action_slot.winfo_children():
            child.destroy()
        self._content.configure(bg=soft)
        self._action_slot.configure(bg=soft)
        self._label.configure(text=message, bg=soft, fg=Theme.TEXT)
        if on_open_folder:
            SecondaryButton(self._action_slot, Lang.t("common.open_folder"), on_open_folder).pack()
        pack_opts = {"fill": "x", "pady": (0, Theme.SPACE_MD)}
        if before is not None:
            pack_opts["before"] = before
        self.pack(**pack_opts)

    def hide(self) -> None:
        self.pack_forget()


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

class BaseView(tk.Frame):
    def __init__(self, app: "App"):
        super().__init__(app, bg=Theme.BG)
        self.app = app

    def on_show(self) -> None:
        """Optional hook: called every time this view becomes visible."""

    def retranslate(self) -> None:
        """Optional hook: called after the language switch, on every view
        already built — update any static widget text via Lang.t()."""


class HomeView(BaseView):
    ACTIONS = [
        ("🌱", "home.action.new_project", "new_project"),
        ("➕", "home.action.add_existing", "add_existing"),
        ("⬆️", "home.action.update_project", "update_project"),
        ("🧩", "home.action.skills", "skills"),
        ("🔎", "home.action.check_project", "check_project"),
    ]

    def __init__(self, app: "App"):
        super().__init__(app)
        self.title_label = tk.Label(self, text=Lang.t("home.title"), font=Fonts.title, fg=Theme.TEXT, bg=Theme.BG)
        self.title_label.pack(anchor="w", padx=Theme.SPACE_XL, pady=(Theme.SPACE_XL, 0))
        self.subtitle_label = tk.Label(
            self, text=Lang.t("home.subtitle"), font=Fonts.body, fg=Theme.TEXT_MUTED, bg=Theme.BG,
        )
        self.subtitle_label.pack(anchor="w", padx=Theme.SPACE_XL, pady=(0, Theme.SPACE_LG))

        cards = tk.Frame(self, bg=Theme.BG)
        cards.pack(fill="both", expand=True, padx=Theme.SPACE_XL, pady=(0, Theme.SPACE_XL))
        self.cards: list[ActionCard] = []
        for icon, key, route in self.ACTIONS:
            card = ActionCard(
                cards, icon, Lang.t(f"{key}.title"), Lang.t(f"{key}.subtitle"),
                command=lambda r=route: self.app.show(r),
            )
            card.pack(fill="x", pady=Theme.SPACE_SM)
            self.cards.append(card)

    def retranslate(self) -> None:
        self.title_label.configure(text=Lang.t("home.title"))
        self.subtitle_label.configure(text=Lang.t("home.subtitle"))
        for card, (_icon, key, _route) in zip(self.cards, self.ACTIONS):
            card.set_texts(Lang.t(f"{key}.title"), Lang.t(f"{key}.subtitle"))


class CheckProjectView(BaseView):
    """Read-only preview: wraps `sfk_updater.py --dry-run`. Fully functional —
    validates the whole subprocess/console pipeline safely (no writes)."""

    def __init__(self, app: "App"):
        super().__init__(app)
        self.header = Header(
            self, Lang.t("check.header_title"), Lang.t("check.header_subtitle"),
            on_back=lambda: self.app.show("home"),
        )
        self.header.pack(fill="x")

        body = tk.Frame(self, bg=Theme.BG)
        body.pack(fill="both", expand=True, padx=Theme.SPACE_XL, pady=Theme.SPACE_MD)

        self.folder_label = tk.Label(body, text=Lang.t("check.folder_label"), font=Fonts.h2, fg=Theme.TEXT, bg=Theme.BG)
        self.folder_label.pack(anchor="w")
        self.picker = PathPicker(body)
        self.picker.pack(fill="x", pady=(Theme.SPACE_XS, Theme.SPACE_MD))

        actions = tk.Frame(body, bg=Theme.BG)
        actions.pack(fill="x", pady=(0, Theme.SPACE_MD))
        self.run_btn = PrimaryButton(actions, Lang.t("check.run_button"), self._run)
        self.run_btn.pack(side="left")

        self.output_label = tk.Label(body, text=Lang.t("common.output"), font=Fonts.h2, fg=Theme.TEXT, bg=Theme.BG)
        self.output_label.pack(anchor="w")
        self.console = ConsolePanel(body)
        self.console.pack(fill="both", expand=True, pady=(Theme.SPACE_XS, 0))

        self.runner: ProcessRunner | None = None

    def retranslate(self) -> None:
        self.header.set_texts(Lang.t("check.header_title"), Lang.t("check.header_subtitle"))
        self.header.retranslate()
        self.folder_label.configure(text=Lang.t("check.folder_label"))
        self.picker.retranslate()
        self.run_btn.set_text(Lang.t("check.run_button"))
        self.output_label.configure(text=Lang.t("common.output"))

    def _run(self) -> None:
        target = self.picker.get()
        if not target:
            self.console.clear()
            self.console.append(Lang.t("check.err_no_folder"), "error")
            return
        self.console.clear()
        self.console.append(Lang.t("check.checking").format(target=target), "muted")
        self.run_btn.set_enabled(False)
        self.runner = ProcessRunner(
            on_line=lambda line: self.console.append(line),
            on_done=self._on_done,
        )
        self.runner.run([PYTHON, str(UPDATER), target, "--dry-run"])

    def _on_done(self, code: int) -> None:
        self.run_btn.set_enabled(True)
        if code == 0:
            self.console.append("", None)
            self.console.append(Lang.t("check.done_ok"), "accent")
        else:
            self.console.append("", None)
            self.console.append(Lang.t("common.error_done").format(code=code), "error")


class NewProjectView(BaseView):
    """Wraps `bin/lib/jb_kit_turbo.py` — scaffolds a brand-new SFK project."""

    def __init__(self, app: "App"):
        super().__init__(app)
        self.header = Header(
            self, Lang.t("new.header_title"), Lang.t("new.header_subtitle"),
            on_back=lambda: self.app.show("home"),
        )
        self.header.pack(fill="x")

        body = tk.Frame(self, bg=Theme.BG)
        body.pack(fill="both", expand=True, padx=Theme.SPACE_XL, pady=Theme.SPACE_MD)

        self.banner = ResultBanner(body)  # stays hidden until show_success/show_error

        self._anchor = tk.Label(body, text=Lang.t("new.anchor_label"), font=Fonts.h2, fg=Theme.TEXT, bg=Theme.BG)
        self._anchor.pack(anchor="w")
        self.anchor_hint = tk.Label(
            body, text=Lang.t("new.anchor_hint"),
            font=Fonts.small, fg=Theme.TEXT_MUTED, bg=Theme.BG,
        )
        self.anchor_hint.pack(anchor="w", pady=(0, Theme.SPACE_XS))
        self.parent_picker = PathPicker(body)
        self.parent_picker.pack(fill="x", pady=(0, Theme.SPACE_MD))

        self.name_label = tk.Label(body, text=Lang.t("new.name_label"), font=Fonts.h2, fg=Theme.TEXT, bg=Theme.BG)
        self.name_label.pack(anchor="w")
        self.name_var = tk.StringVar()
        name_entry = tk.Entry(
            body, textvariable=self.name_var, font=Fonts.body, fg=Theme.TEXT, bg="white",
            relief="flat", highlightthickness=1, highlightbackground=Theme.BORDER,
            highlightcolor=Theme.ACCENT, insertbackground=Theme.TEXT,
        )
        name_entry.pack(fill="x", ipady=6, pady=(Theme.SPACE_XS, Theme.SPACE_XS))
        self.name_hint = tk.Label(
            body, text=Lang.t("new.name_hint"),
            font=Fonts.small, fg=Theme.TEXT_MUTED, bg=Theme.BG,
        )
        self.name_hint.pack(anchor="w", pady=(0, Theme.SPACE_MD))

        options = tk.Frame(body, bg=Theme.BG)
        options.pack(fill="x", pady=(0, Theme.SPACE_MD))
        self.init_git_var = tk.BooleanVar(value=True)
        self.checkbox_git = tk.Checkbutton(
            options, text=Lang.t("new.checkbox_git"),
            variable=self.init_git_var, font=Fonts.body, fg=Theme.TEXT, bg=Theme.BG,
            selectcolor="white", activebackground=Theme.BG,
        )
        self.checkbox_git.pack(anchor="w")
        self.force_var = tk.BooleanVar(value=False)
        self.checkbox_force = tk.Checkbutton(
            options, text=Lang.t("new.checkbox_force"),
            variable=self.force_var, font=Fonts.body, fg=Theme.TEXT, bg=Theme.BG,
            selectcolor="white", activebackground=Theme.BG,
        )
        self.checkbox_force.pack(anchor="w")

        actions = tk.Frame(body, bg=Theme.BG)
        actions.pack(fill="x", pady=(0, Theme.SPACE_MD))
        self.run_btn = PrimaryButton(actions, Lang.t("new.run_button"), self._run)
        self.run_btn.pack(side="left")

        self.output_label = tk.Label(body, text=Lang.t("common.output"), font=Fonts.h2, fg=Theme.TEXT, bg=Theme.BG)
        self.output_label.pack(anchor="w")
        self.console = ConsolePanel(body)
        self.console.pack(fill="both", expand=True, pady=(Theme.SPACE_XS, 0))

        self.runner: ProcessRunner | None = None
        self._target: str = ""

    def retranslate(self) -> None:
        self.header.set_texts(Lang.t("new.header_title"), Lang.t("new.header_subtitle"))
        self.header.retranslate()
        self._anchor.configure(text=Lang.t("new.anchor_label"))
        self.anchor_hint.configure(text=Lang.t("new.anchor_hint"))
        self.parent_picker.retranslate()
        self.name_label.configure(text=Lang.t("new.name_label"))
        self.name_hint.configure(text=Lang.t("new.name_hint"))
        self.checkbox_git.configure(text=Lang.t("new.checkbox_git"))
        self.checkbox_force.configure(text=Lang.t("new.checkbox_force"))
        self.run_btn.set_text(Lang.t("new.run_button"))
        self.output_label.configure(text=Lang.t("common.output"))

    def _validate(self) -> str | None:
        """Returns an error message, or None if inputs are usable."""
        parent = self.parent_picker.get()
        name = self.name_var.get().strip()
        if not parent:
            return Lang.t("new.err_no_parent")
        if not os.path.isdir(parent):
            return Lang.t("new.err_parent_missing")
        if not name:
            return Lang.t("new.err_no_name")
        if os.sep in name or (os.altsep and os.altsep in name) or name in {".", ".."}:
            return Lang.t("new.err_bad_name")
        target = str(Path(parent) / name)
        if os.path.isdir(target) and os.listdir(target) and not self.force_var.get():
            return Lang.t("new.err_target_exists").format(name=name)
        self._target = target
        return None

    def _run(self) -> None:
        self.banner.hide()
        error = self._validate()
        if error:
            self.console.clear()
            self.console.append(f"⚠️  {error}", "error")
            return

        self.console.clear()
        self.console.append(Lang.t("new.creating").format(target=self._target), "muted")
        self.run_btn.set_enabled(False)

        args = [PYTHON, str(SCAFFOLDER), self._target, "--project-name", self.name_var.get().strip()]
        if self.init_git_var.get():
            args.append("--init-git")
        if self.force_var.get():
            args.append("--force")

        self.runner = ProcessRunner(on_line=lambda line: self.console.append(line), on_done=self._on_done)
        self.runner.run(args)

    def _on_done(self, code: int) -> None:
        self.run_btn.set_enabled(True)
        if code == 0:
            self.console.append("", None)
            self.console.append(Lang.t("new.created_ok"), "accent")
            self.banner.show_success(
                Lang.t("new.created_banner").format(target=self._target),
                on_open_folder=lambda: open_folder(self._target),
                before=self._anchor,
            )
        else:
            self.console.append("", None)
            self.console.append(Lang.t("common.error_done").format(code=code), "error")
            self.banner.show_error(Lang.t("new.failed_banner"), before=self._anchor)


class UpdateProjectView(BaseView):
    """Wraps `bin/lib/sfk_updater.py` — adds SFK to an existing project, updates
    an SFK project to the latest engine, or migrates a legacy layout. Preview
    (dry-run) is the primary action; Apply requires a same-path preview first
    plus an explicit confirmation, since it writes to disk."""

    def __init__(self, app: "App", title_key: str, subtitle_key: str):
        super().__init__(app)
        self._title_key = title_key
        self._subtitle_key = subtitle_key
        self.header = Header(
            self, Lang.t(title_key), Lang.t(subtitle_key), on_back=lambda: self.app.show("home"),
        )
        self.header.pack(fill="x")

        body = tk.Frame(self, bg=Theme.BG)
        body.pack(fill="both", expand=True, padx=Theme.SPACE_XL, pady=Theme.SPACE_MD)

        self.banner = ResultBanner(body)

        self._anchor = tk.Label(body, text=Lang.t("update.anchor_label"), font=Fonts.h2, fg=Theme.TEXT, bg=Theme.BG)
        self._anchor.pack(anchor="w")
        self.picker = PathPicker(body)
        self.picker.pack(fill="x", pady=(Theme.SPACE_XS, Theme.SPACE_MD))
        self.picker.var.trace_add("write", lambda *_: self._on_path_changed())

        self.skip_backup_var = tk.BooleanVar(value=False)
        self.checkbox_skip_backup = tk.Checkbutton(
            body, text=Lang.t("update.checkbox_skip_backup"),
            variable=self.skip_backup_var, font=Fonts.body, fg=Theme.TEXT, bg=Theme.BG,
            selectcolor="white", activebackground=Theme.BG,
        )
        self.checkbox_skip_backup.pack(anchor="w", pady=(0, Theme.SPACE_MD))

        actions = tk.Frame(body, bg=Theme.BG)
        actions.pack(fill="x", pady=(0, Theme.SPACE_MD))
        self.preview_btn = PrimaryButton(actions, Lang.t("update.preview_button"), self._run_preview)
        self.preview_btn.pack(side="left", padx=(0, Theme.SPACE_SM))
        self.apply_btn = PrimaryButton(actions, Lang.t("update.apply_button"), self._run_apply, danger=True)
        self.apply_btn.pack(side="left")

        self.output_label = tk.Label(body, text=Lang.t("common.output"), font=Fonts.h2, fg=Theme.TEXT, bg=Theme.BG)
        self.output_label.pack(anchor="w")
        self.console = ConsolePanel(body)
        self.console.pack(fill="both", expand=True, pady=(Theme.SPACE_XS, 0))

        self.runner: ProcessRunner | None = None
        self._mode: str = ""
        self._last_previewed_target: str | None = None

    def retranslate(self) -> None:
        self.header.set_texts(Lang.t(self._title_key), Lang.t(self._subtitle_key))
        self.header.retranslate()
        self._anchor.configure(text=Lang.t("update.anchor_label"))
        self.picker.retranslate()
        self.checkbox_skip_backup.configure(text=Lang.t("update.checkbox_skip_backup"))
        self.preview_btn.set_text(Lang.t("update.preview_button"))
        self.apply_btn.set_text(Lang.t("update.apply_button"))
        self.output_label.configure(text=Lang.t("common.output"))

    def _on_path_changed(self) -> None:
        # Changing the path invalidates any previous preview for a different folder.
        self.banner.hide()

    def _set_buttons_enabled(self, enabled: bool) -> None:
        self.preview_btn.set_enabled(enabled)
        self.apply_btn.set_enabled(enabled)

    def _run_preview(self) -> None:
        target = self.picker.get()
        if not target or not os.path.isdir(target):
            self.console.clear()
            self.console.append(Lang.t("update.err_no_folder"), "error")
            return
        self.banner.hide()
        self.console.clear()
        self.console.append(Lang.t("update.previewing").format(target=target), "muted")
        self._mode = "preview"
        self._set_buttons_enabled(False)
        self.runner = ProcessRunner(on_line=lambda line: self.console.append(line), on_done=self._on_done)
        self.runner.run([PYTHON, str(UPDATER), target, "--dry-run"])

    def _run_apply(self) -> None:
        target = self.picker.get()
        if not target or not os.path.isdir(target):
            self.console.clear()
            self.console.append(Lang.t("update.err_no_folder"), "error")
            return
        if target != self._last_previewed_target:
            self.banner.show_error(Lang.t("update.preview_required"), before=self._anchor)
            return
        proceed = messagebox.askyesno(
            Lang.t("update.apply_confirm_title"),
            Lang.t("update.apply_confirm_message").format(target=target),
        )
        if not proceed:
            return

        self.banner.hide()
        self.console.clear()
        self.console.append(Lang.t("update.applying").format(target=target), "muted")
        self._mode = "apply"
        self._set_buttons_enabled(False)
        args = [PYTHON, str(UPDATER), target, "--yes"]
        if self.skip_backup_var.get():
            args.append("--no-backup")
        self.runner = ProcessRunner(on_line=lambda line: self.console.append(line), on_done=self._on_done)
        self.runner.run(args)

    def _on_done(self, code: int) -> None:
        self._set_buttons_enabled(True)
        target = self.picker.get()
        if code == 0:
            self.console.append("", None)
            if self._mode == "preview":
                self._last_previewed_target = target
                self.console.append(Lang.t("update.preview_done"), "accent")
            else:
                self.console.append(Lang.t("update.apply_done"), "accent")
                self.banner.show_success(
                    Lang.t("update.applied_banner").format(target=target),
                    on_open_folder=lambda: open_folder(target),
                    before=self._anchor,
                )
        else:
            self.console.append("", None)
            self.console.append(Lang.t("common.error_done").format(code=code), "error")
            self.banner.show_error(Lang.t("update.failed_banner"), before=self._anchor)


class SkillsView(BaseView):
    """Import a new skill into this SFK installation (wraps import_skill.py),
    see what's already installed, and jump to the Update flow to sync skills
    into a project (skills are part of the engine, kept in one place: MANIFEST)."""

    def __init__(self, app: "App"):
        super().__init__(app)
        self.header = Header(
            self, Lang.t("skills.header_title"), Lang.t("skills.header_subtitle"),
            on_back=lambda: self.app.show("home"),
        )
        self.header.pack(fill="x")

        body = tk.Frame(self, bg=Theme.BG)
        body.pack(fill="both", expand=True, padx=Theme.SPACE_XL, pady=Theme.SPACE_MD)

        self.banner = ResultBanner(body)
        self._anchor = tk.Label(body, text=Lang.t("skills.import_anchor"), font=Fonts.h2, fg=Theme.TEXT, bg=Theme.BG)
        self._anchor.pack(anchor="w")
        self.import_hint = tk.Label(
            body, text=Lang.t("skills.import_hint"),
            font=Fonts.small, fg=Theme.TEXT_MUTED, bg=Theme.BG,
        )
        self.import_hint.pack(anchor="w", pady=(0, Theme.SPACE_XS))
        self.picker = PathPicker(body)
        self.picker.pack(fill="x", pady=(0, Theme.SPACE_SM))
        import_actions = tk.Frame(body, bg=Theme.BG)
        import_actions.pack(fill="x", pady=(0, Theme.SPACE_LG))
        self.import_btn = PrimaryButton(import_actions, Lang.t("skills.import_button"), self._run_import)
        self.import_btn.pack(side="left")

        ttk.Separator(body, orient="horizontal").pack(fill="x", pady=(0, Theme.SPACE_LG))

        self.sync_title = tk.Label(
            body, text=Lang.t("skills.sync_title"), font=Fonts.h2, fg=Theme.TEXT, bg=Theme.BG,
        )
        self.sync_title.pack(anchor="w")
        self.sync_hint = tk.Label(
            body, text=Lang.t("skills.sync_hint"),
            font=Fonts.small, fg=Theme.TEXT_MUTED, bg=Theme.BG,
        )
        self.sync_hint.pack(anchor="w", pady=(0, Theme.SPACE_SM))
        self.sync_btn = SecondaryButton(
            body, Lang.t("skills.sync_button"), lambda: self.app.show("update_project"),
        )
        self.sync_btn.pack(anchor="w", pady=(0, Theme.SPACE_LG))

        ttk.Separator(body, orient="horizontal").pack(fill="x", pady=(0, Theme.SPACE_SM))
        self.installed_title = tk.Label(
            body, text=Lang.t("skills.installed_title"), font=Fonts.h2, fg=Theme.TEXT, bg=Theme.BG,
        )
        self.installed_title.pack(anchor="w", pady=(Theme.SPACE_SM, Theme.SPACE_XS))
        list_frame = tk.Frame(body, bg=Theme.BG)
        list_frame.pack(fill="both", expand=True)
        list_scroll = ttk.Scrollbar(list_frame, orient="vertical")
        self.skills_list = tk.Listbox(
            list_frame, font=Fonts.body, fg=Theme.TEXT, bg="white", relief="flat",
            highlightthickness=1, highlightbackground=Theme.BORDER, yscrollcommand=list_scroll.set,
            selectbackground=Theme.ACCENT_SOFT, selectforeground=Theme.TEXT, activestyle="none",
        )
        list_scroll.configure(command=self.skills_list.yview)
        self.skills_list.pack(side="left", fill="both", expand=True)
        list_scroll.pack(side="right", fill="y")

        self.runner: ProcessRunner | None = None
        self._console_log: list[str] = []

    def retranslate(self) -> None:
        self.header.set_texts(Lang.t("skills.header_title"), Lang.t("skills.header_subtitle"))
        self.header.retranslate()
        self._anchor.configure(text=Lang.t("skills.import_anchor"))
        self.import_hint.configure(text=Lang.t("skills.import_hint"))
        self.picker.retranslate()
        self.import_btn.set_text(Lang.t("skills.import_button"))
        self.sync_title.configure(text=Lang.t("skills.sync_title"))
        self.sync_hint.configure(text=Lang.t("skills.sync_hint"))
        self.sync_btn.set_text(Lang.t("skills.sync_button"))
        self.installed_title.configure(text=Lang.t("skills.installed_title"))

    def on_show(self) -> None:
        self._refresh_skills_list()

    def _refresh_skills_list(self) -> None:
        self.skills_list.delete(0, "end")
        if SKILLS_DIR.exists():
            for entry in sorted(p.name for p in SKILLS_DIR.iterdir() if p.is_dir()):
                self.skills_list.insert("end", entry)

    def _run_import(self) -> None:
        source = self.picker.get()
        if not source or not os.path.isdir(source):
            self.banner.show_error(Lang.t("skills.err_no_folder"), before=self._anchor)
            return

        skill_name = Path(source).name
        dest = SKILLS_DIR / skill_name
        if dest.exists():
            proceed = messagebox.askyesno(
                Lang.t("skills.overwrite_confirm_title"),
                Lang.t("skills.overwrite_confirm_message").format(skill_name=skill_name),
            )
            if not proceed:
                return

        self.banner.hide()
        self.import_btn.set_enabled(False)
        self._console_log = []
        self.runner = ProcessRunner(on_line=self._console_log.append, on_done=lambda code: self._on_done(code, skill_name))
        self.runner.run([PYTHON, str(SKILL_IMPORTER), source, "--force"])

    def _on_done(self, code: int, skill_name: str) -> None:
        self.import_btn.set_enabled(True)
        if code == 0:
            self.banner.show_success(Lang.t("skills.imported_ok").format(skill_name=skill_name), before=self._anchor)
            self._refresh_skills_list()
        else:
            detail = "\n".join(self._console_log[-4:])
            self.banner.show_error(Lang.t("skills.import_failed").format(skill_name=skill_name, detail=detail), before=self._anchor)


class ComingSoonView(BaseView):
    """Placeholder for panels landing in later phases (F2/F3/F4)."""

    def __init__(self, app: "App", title: str, phase_note: str):
        super().__init__(app)
        self.header = Header(self, title, phase_note, on_back=lambda: self.app.show("home"))
        self.header.pack(fill="x")
        self.note_label = tk.Label(
            self, text=Lang.t("comingsoon.note"), font=Fonts.h1,
            fg=Theme.TEXT_MUTED, bg=Theme.BG,
        )
        self.note_label.pack(expand=True)

    def retranslate(self) -> None:
        self.header.retranslate()
        self.note_label.configure(text=Lang.t("comingsoon.note"))


def build_icon_image(root: tk.Misc, size: int = 64) -> tk.PhotoImage:
    """Draw the app icon procedurally — no external asset, no PIL dependency.
    Three stacked bars echo the app's own 3-zone architecture diagram; the
    middle bar in the console accent color ties the icon to the app's palette."""
    img = tk.PhotoImage(width=size, height=size, master=root)
    img.put(Theme.ACCENT, to=(0, 0, size, size))

    def bar(y0_ratio: float, y1_ratio: float, width_ratio: float, color: str) -> None:
        y0, y1 = int(size * y0_ratio), int(size * y1_ratio)
        w = int(size * width_ratio)
        x0 = (size - w) // 2
        img.put(color, to=(x0, y0, x0 + w, y1))

    bar(0.22, 0.34, 0.62, Theme.BG)
    bar(0.44, 0.56, 0.50, Theme.CONSOLE_ACCENT)
    bar(0.66, 0.78, 0.62, Theme.BG)
    return img


def export_icon(path: str) -> None:
    """Maintainer command: regenerate the static icon file used by the
    desktop entry / Windows shortcut (`python3 bin/sfk_gui.py --export-icon`)."""
    root = tk.Tk()
    root.withdraw()
    img = build_icon_image(root, size=64)
    img.write(path, format="png")
    root.destroy()
    print(f"Icon written to: {path}")


class LangSwitch(tk.Frame):
    """PT/EN toggle, always visible top-right on every screen — lives directly
    on the root window (not inside the swapped view container), so it survives
    `tkraise()` between views instead of being part of any single one.

    Drawn as a bordered chip (not bare text on the background) so it reads as
    a clickable control at a glance instead of blending into the app chrome."""

    def __init__(self, parent):
        super().__init__(parent, bg=Theme.CARD_BG, highlightthickness=1, highlightbackground=Theme.CARD_BORDER)
        self._pt = tk.Label(
            self, text=Lang.t("common.lang_pt"), font=Fonts.body_bold, bg=Theme.CARD_BG, cursor="hand2",
        )
        self._sep = tk.Label(self, text="/", font=Fonts.body, fg=Theme.BORDER, bg=Theme.CARD_BG)
        self._en = tk.Label(
            self, text=Lang.t("common.lang_en"), font=Fonts.body_bold, bg=Theme.CARD_BG, cursor="hand2",
        )
        self._pt.pack(side="left", padx=(Theme.SPACE_SM, Theme.SPACE_XS), pady=Theme.SPACE_XS)
        self._sep.pack(side="left")
        self._en.pack(side="left", padx=(Theme.SPACE_XS, Theme.SPACE_SM), pady=Theme.SPACE_XS)
        self._pt.bind("<Button-1>", lambda _e: Lang.set("pt"))
        self._en.bind("<Button-1>", lambda _e: Lang.set("en"))
        self.refresh()

    def refresh(self) -> None:
        self._pt.configure(fg=Theme.ACCENT if Lang.current == "pt" else Theme.TEXT_MUTED)
        self._en.configure(fg=Theme.ACCENT if Lang.current == "en" else Theme.TEXT_MUTED)


# ---------------------------------------------------------------------------
# App shell
# ---------------------------------------------------------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        global _GLOBAL_ROOT
        _GLOBAL_ROOT = self

        Lang.load()

        self.title(Lang.t("app.title"))
        self.geometry("760x580")
        self.minsize(680, 480)
        self.configure(bg=Theme.BG)

        Fonts.load(self)
        self._style_ttk()
        self._icon_img = build_icon_image(self, size=64)  # keep a reference — Tk drops GC'd images
        self.iconphoto(True, self._icon_img)

        self._container = tk.Frame(self, bg=Theme.BG)
        self._container.pack(fill="both", expand=True)

        self._views: dict[str, BaseView] = {}
        self._add_view("home", HomeView(self))
        self._add_view("check_project", CheckProjectView(self))
        self._add_view("new_project", NewProjectView(self))
        self._add_view("add_existing", UpdateProjectView(
            self, "update.route.add_existing.title", "update.route.add_existing.subtitle",
        ))
        self._add_view("update_project", UpdateProjectView(
            self, "update.route.update_project.title", "update.route.update_project.subtitle",
        ))
        self._add_view("skills", SkillsView(self))

        self._lang_switch = LangSwitch(self)
        self._lang_switch.place(relx=1.0, x=-Theme.SPACE_MD, y=Theme.SPACE_SM, anchor="ne")
        self._lang_switch.lift()
        Lang.on_change(self._on_lang_change)

        self.show("home")

    def _on_lang_change(self) -> None:
        self.title(Lang.t("app.title"))
        self._lang_switch.refresh()
        for view in self._views.values():
            view.retranslate()

    def _style_ttk(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TSeparator", background=Theme.BORDER)

    def _add_view(self, name: str, view: BaseView) -> None:
        self._views[name] = view
        view.place(x=0, y=0, relwidth=1, relheight=1)

    def show(self, name: str) -> None:
        view = self._views[name]
        view.tkraise()
        self._lang_switch.lift()  # defensive: some WMs re-stack siblings on tkraise()
        view.on_show()


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--export-icon":
        target = sys.argv[2] if len(sys.argv) > 2 else str(BIN_DIR / "sfk-launcher.png")
        export_icon(target)
        return 0
    app = App()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
