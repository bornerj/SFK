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
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, font as tkfont, messagebox, ttk

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

    SPACE_XS = 4
    SPACE_SM = 8
    SPACE_MD = 16
    SPACE_LG = 24
    SPACE_XL = 32


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
        cls.title = resolve_font(root, UI_FONT_CANDIDATES, 22, "bold")
        cls.h1 = resolve_font(root, UI_FONT_CANDIDATES, 15, "bold")
        cls.h2 = resolve_font(root, UI_FONT_CANDIDATES, 12, "bold")
        cls.body = resolve_font(root, UI_FONT_CANDIDATES, 11, "normal")
        cls.body_bold = resolve_font(root, UI_FONT_CANDIDATES, 11, "bold")
        cls.small = resolve_font(root, UI_FONT_CANDIDATES, 9, "normal")
        cls.mono = resolve_font(root, MONO_FONT_CANDIDATES, 10, "normal")


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

    RADIUS = 14

    def __init__(self, parent, icon: str, title: str, subtitle: str, command, **kw):
        super().__init__(parent, bg=Theme.BG, highlightthickness=0, height=92, **kw)
        self._command = command
        self._hover = False
        self.bind("<Configure>", self._redraw)
        self.bind("<Button-1>", lambda _e: self._command())
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.configure(cursor="hand2")
        self._icon, self._title, self._subtitle = icon, title, subtitle

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
        h = self.winfo_height() or 92
        fill = Theme.CARD_HOVER if self._hover else Theme.CARD_BG
        border = Theme.ACCENT if self._hover else Theme.CARD_BORDER
        self._rounded_rect(2, 2, w - 2, h - 2, self.RADIUS, fill=fill, outline=border, width=1.5)
        self.create_text(28, h / 2, text=self._icon, font=("", 26), anchor="w", fill=Theme.ACCENT)
        self.create_text(76, h / 2 - 12, text=self._title, font=Fonts.h1, anchor="w", fill=Theme.TEXT)
        self.create_text(76, h / 2 + 12, text=self._subtitle, font=Fonts.body, anchor="w", fill=Theme.TEXT_MUTED,
                          width=w - 100)


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
        SecondaryButton(self, "📁  Procurar…", self._browse).pack(side="left")

    def _browse(self) -> None:
        path = filedialog.askdirectory(title="Escolha a pasta", mustexist=False)
        if path:
            self.var.set(path)

    def get(self) -> str:
        return self.var.get().strip()


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
        if on_back:
            SecondaryButton(row, "←  Início", on_back).pack(side="left", padx=(0, Theme.SPACE_MD))
        text_col = tk.Frame(row, bg=Theme.BG)
        text_col.pack(side="left", fill="x", expand=True)
        tk.Label(text_col, text=title, font=Fonts.title, fg=Theme.TEXT, bg=Theme.BG).pack(anchor="w")
        tk.Label(text_col, text=subtitle, font=Fonts.body, fg=Theme.TEXT_MUTED, bg=Theme.BG).pack(anchor="w")
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=Theme.SPACE_XL, pady=(Theme.SPACE_SM, 0))


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
            SecondaryButton(self._action_slot, "📂  Abrir pasta", on_open_folder).pack()
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


class HomeView(BaseView):
    ACTIONS = [
        ("🌱", "Criar um projeto novo",
         "Começar do zero com o SFK já instalado.", "new_project"),
        ("➕", "Adicionar o SFK a um projeto que já existe",
         "Instalar o SFK sobre um código existente, sem tocar nele.", "add_existing"),
        ("⬆️", "Atualizar o SFK de um projeto",
         "Trazer a versão mais nova (migra layout antigo automaticamente).", "update_project"),
        ("🧩", "Skills — importar ou atualizar",
         "Adicionar conhecimento novo ao SFK ou sincronizar o existente.", "skills"),
        ("🔎", "Checar um projeto",
         "Ver o que mudaria, sem alterar nada (pré-visualização).", "check_project"),
    ]

    def __init__(self, app: "App"):
        super().__init__(app)
        tk.Label(
            self, text="SFK Launcher", font=Fonts.title, fg=Theme.TEXT, bg=Theme.BG,
        ).pack(anchor="w", padx=Theme.SPACE_XL, pady=(Theme.SPACE_XL, 0))
        tk.Label(
            self, text="O que você quer fazer?", font=Fonts.body, fg=Theme.TEXT_MUTED, bg=Theme.BG,
        ).pack(anchor="w", padx=Theme.SPACE_XL, pady=(0, Theme.SPACE_LG))

        cards = tk.Frame(self, bg=Theme.BG)
        cards.pack(fill="both", expand=True, padx=Theme.SPACE_XL, pady=(0, Theme.SPACE_XL))
        for icon, title, subtitle, route in self.ACTIONS:
            card = ActionCard(
                cards, icon, title, subtitle,
                command=lambda r=route: self.app.show(r),
            )
            card.pack(fill="x", pady=Theme.SPACE_SM)


class CheckProjectView(BaseView):
    """Read-only preview: wraps `sfk_updater.py --dry-run`. Fully functional —
    validates the whole subprocess/console pipeline safely (no writes)."""

    def __init__(self, app: "App"):
        super().__init__(app)
        Header(
            self, "Checar um projeto", "Mostra o que mudaria — não altera nada no disco.",
            on_back=lambda: self.app.show("home"),
        ).pack(fill="x")

        body = tk.Frame(self, bg=Theme.BG)
        body.pack(fill="both", expand=True, padx=Theme.SPACE_XL, pady=Theme.SPACE_MD)

        tk.Label(body, text="Pasta do projeto", font=Fonts.h2, fg=Theme.TEXT, bg=Theme.BG).pack(anchor="w")
        self.picker = PathPicker(body)
        self.picker.pack(fill="x", pady=(Theme.SPACE_XS, Theme.SPACE_MD))

        actions = tk.Frame(body, bg=Theme.BG)
        actions.pack(fill="x", pady=(0, Theme.SPACE_MD))
        self.run_btn = PrimaryButton(actions, "🔎  Checar agora", self._run)
        self.run_btn.pack(side="left")

        tk.Label(body, text="Saída", font=Fonts.h2, fg=Theme.TEXT, bg=Theme.BG).pack(anchor="w")
        self.console = ConsolePanel(body)
        self.console.pack(fill="both", expand=True, pady=(Theme.SPACE_XS, 0))

        self.runner: ProcessRunner | None = None

    def _run(self) -> None:
        target = self.picker.get()
        if not target:
            self.console.clear()
            self.console.append("⚠️  Escolha uma pasta primeiro.", "error")
            return
        self.console.clear()
        self.console.append(f"Checando: {target}", "muted")
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
            self.console.append("✅  Verificação concluída.", "accent")
        else:
            self.console.append("", None)
            self.console.append(f"❌  Terminou com erro (código {code}).", "error")


class NewProjectView(BaseView):
    """Wraps `bin/lib/jb_kit_turbo.py` — scaffolds a brand-new SFK project."""

    def __init__(self, app: "App"):
        super().__init__(app)
        Header(
            self, "Criar um projeto novo", "Começar do zero, com o SFK já instalado e organizado.",
            on_back=lambda: self.app.show("home"),
        ).pack(fill="x")

        body = tk.Frame(self, bg=Theme.BG)
        body.pack(fill="both", expand=True, padx=Theme.SPACE_XL, pady=Theme.SPACE_MD)

        self.banner = ResultBanner(body)  # stays hidden until show_success/show_error

        self._anchor = tk.Label(body, text="Onde criar o projeto", font=Fonts.h2, fg=Theme.TEXT, bg=Theme.BG)
        self._anchor.pack(anchor="w")
        tk.Label(
            body, text="Escolha a pasta que vai CONTER a pasta do novo projeto.",
            font=Fonts.small, fg=Theme.TEXT_MUTED, bg=Theme.BG,
        ).pack(anchor="w", pady=(0, Theme.SPACE_XS))
        self.parent_picker = PathPicker(body)
        self.parent_picker.pack(fill="x", pady=(0, Theme.SPACE_MD))

        tk.Label(body, text="Nome do projeto", font=Fonts.h2, fg=Theme.TEXT, bg=Theme.BG).pack(anchor="w")
        self.name_var = tk.StringVar()
        name_entry = tk.Entry(
            body, textvariable=self.name_var, font=Fonts.body, fg=Theme.TEXT, bg="white",
            relief="flat", highlightthickness=1, highlightbackground=Theme.BORDER,
            highlightcolor=Theme.ACCENT, insertbackground=Theme.TEXT,
        )
        name_entry.pack(fill="x", ipady=6, pady=(Theme.SPACE_XS, Theme.SPACE_XS))
        tk.Label(
            body, text="Vira o nome da pasta e o nome do projeto dentro dos arquivos de configuração.",
            font=Fonts.small, fg=Theme.TEXT_MUTED, bg=Theme.BG,
        ).pack(anchor="w", pady=(0, Theme.SPACE_MD))

        options = tk.Frame(body, bg=Theme.BG)
        options.pack(fill="x", pady=(0, Theme.SPACE_MD))
        self.init_git_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options, text="Iniciar controle de versão (git) e ativar a proteção automática de memória",
            variable=self.init_git_var, font=Fonts.body, fg=Theme.TEXT, bg=Theme.BG,
            selectcolor="white", activebackground=Theme.BG,
        ).pack(anchor="w")
        self.force_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            options, text="Permitir criar dentro de uma pasta que já existe e não está vazia",
            variable=self.force_var, font=Fonts.body, fg=Theme.TEXT, bg=Theme.BG,
            selectcolor="white", activebackground=Theme.BG,
        ).pack(anchor="w")

        actions = tk.Frame(body, bg=Theme.BG)
        actions.pack(fill="x", pady=(0, Theme.SPACE_MD))
        self.run_btn = PrimaryButton(actions, "🌱  Criar projeto", self._run)
        self.run_btn.pack(side="left")

        tk.Label(body, text="Saída", font=Fonts.h2, fg=Theme.TEXT, bg=Theme.BG).pack(anchor="w")
        self.console = ConsolePanel(body)
        self.console.pack(fill="both", expand=True, pady=(Theme.SPACE_XS, 0))

        self.runner: ProcessRunner | None = None
        self._target: str = ""

    def _validate(self) -> str | None:
        """Returns an error message, or None if inputs are usable."""
        parent = self.parent_picker.get()
        name = self.name_var.get().strip()
        if not parent:
            return "Escolha onde criar o projeto primeiro."
        if not os.path.isdir(parent):
            return "A pasta escolhida não existe mais — escolha novamente."
        if not name:
            return "Dê um nome ao projeto."
        if os.sep in name or (os.altsep and os.altsep in name) or name in {".", ".."}:
            return "O nome não pode conter barras nem ser '.' ou '..'."
        target = str(Path(parent) / name)
        if os.path.isdir(target) and os.listdir(target) and not self.force_var.get():
            return f"A pasta '{name}' já existe e não está vazia. Marque a opção de permitir, se tiver certeza."
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
        self.console.append(f"Criando projeto em: {self._target}", "muted")
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
            self.console.append("✅  Projeto criado com sucesso.", "accent")
            self.banner.show_success(
                f"Projeto criado em: {self._target}",
                on_open_folder=lambda: open_folder(self._target),
                before=self._anchor,
            )
        else:
            self.console.append("", None)
            self.console.append(f"❌  Terminou com erro (código {code}).", "error")
            self.banner.show_error("Não foi possível criar o projeto — veja a saída acima.", before=self._anchor)


class UpdateProjectView(BaseView):
    """Wraps `bin/lib/sfk_updater.py` — adds SFK to an existing project, updates
    an SFK project to the latest engine, or migrates a legacy layout. Preview
    (dry-run) is the primary action; Apply requires a same-path preview first
    plus an explicit confirmation, since it writes to disk."""

    def __init__(self, app: "App", title: str, subtitle: str):
        super().__init__(app)
        Header(self, title, subtitle, on_back=lambda: self.app.show("home")).pack(fill="x")

        body = tk.Frame(self, bg=Theme.BG)
        body.pack(fill="both", expand=True, padx=Theme.SPACE_XL, pady=Theme.SPACE_MD)

        self.banner = ResultBanner(body)

        self._anchor = tk.Label(body, text="Pasta do projeto", font=Fonts.h2, fg=Theme.TEXT, bg=Theme.BG)
        self._anchor.pack(anchor="w")
        self.picker = PathPicker(body)
        self.picker.pack(fill="x", pady=(Theme.SPACE_XS, Theme.SPACE_MD))
        self.picker.var.trace_add("write", lambda *_: self._on_path_changed())

        self.skip_backup_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            body, text="Pular o backup automático antes de migrar (não recomendado)",
            variable=self.skip_backup_var, font=Fonts.body, fg=Theme.TEXT, bg=Theme.BG,
            selectcolor="white", activebackground=Theme.BG,
        ).pack(anchor="w", pady=(0, Theme.SPACE_MD))

        actions = tk.Frame(body, bg=Theme.BG)
        actions.pack(fill="x", pady=(0, Theme.SPACE_MD))
        self.preview_btn = PrimaryButton(actions, "🔎  Pré-visualizar (não altera nada)", self._run_preview)
        self.preview_btn.pack(side="left", padx=(0, Theme.SPACE_SM))
        self.apply_btn = PrimaryButton(actions, "✅  Aplicar alterações", self._run_apply, danger=True)
        self.apply_btn.pack(side="left")

        tk.Label(body, text="Saída", font=Fonts.h2, fg=Theme.TEXT, bg=Theme.BG).pack(anchor="w")
        self.console = ConsolePanel(body)
        self.console.pack(fill="both", expand=True, pady=(Theme.SPACE_XS, 0))

        self.runner: ProcessRunner | None = None
        self._mode: str = ""
        self._last_previewed_target: str | None = None

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
            self.console.append("⚠️  Escolha uma pasta de projeto existente primeiro.", "error")
            return
        self.banner.hide()
        self.console.clear()
        self.console.append(f"Pré-visualizando: {target}", "muted")
        self._mode = "preview"
        self._set_buttons_enabled(False)
        self.runner = ProcessRunner(on_line=lambda line: self.console.append(line), on_done=self._on_done)
        self.runner.run([PYTHON, str(UPDATER), target, "--dry-run"])

    def _run_apply(self) -> None:
        target = self.picker.get()
        if not target or not os.path.isdir(target):
            self.console.clear()
            self.console.append("⚠️  Escolha uma pasta de projeto existente primeiro.", "error")
            return
        if target != self._last_previewed_target:
            self.banner.show_error(
                "Pré-visualize esta pasta primeiro (botão acima) antes de aplicar.",
                before=self._anchor,
            )
            return
        proceed = messagebox.askyesno(
            "Confirmar alterações",
            "Isso vai instalar/atualizar o SFK nesta pasta de verdade.\n\n"
            f"Pasta: {target}\n\n"
            "Você já viu a pré-visualização acima. Continuar?",
        )
        if not proceed:
            return

        self.banner.hide()
        self.console.clear()
        self.console.append(f"Aplicando em: {target}", "muted")
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
                self.console.append("✅  Pré-visualização concluída. Nada foi alterado.", "accent")
            else:
                self.console.append("✅  Alterações aplicadas com sucesso.", "accent")
                self.banner.show_success(
                    f"SFK instalado/atualizado em: {target}",
                    on_open_folder=lambda: open_folder(target),
                    before=self._anchor,
                )
        else:
            self.console.append("", None)
            self.console.append(f"❌  Terminou com erro (código {code}).", "error")
            self.banner.show_error("Algo deu errado — veja a saída acima.", before=self._anchor)


class ComingSoonView(BaseView):
    """Placeholder for panels landing in later phases (F2/F3/F4)."""

    def __init__(self, app: "App", title: str, phase_note: str):
        super().__init__(app)
        Header(self, title, phase_note, on_back=lambda: self.app.show("home")).pack(fill="x")
        tk.Label(
            self, text="🚧  Em construção nesta fase do plano.", font=Fonts.h1,
            fg=Theme.TEXT_MUTED, bg=Theme.BG,
        ).pack(expand=True)


# ---------------------------------------------------------------------------
# App shell
# ---------------------------------------------------------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        global _GLOBAL_ROOT
        _GLOBAL_ROOT = self

        self.title("SFK Launcher")
        self.geometry("880x620")
        self.minsize(720, 520)
        self.configure(bg=Theme.BG)

        Fonts.load(self)
        self._style_ttk()

        self._container = tk.Frame(self, bg=Theme.BG)
        self._container.pack(fill="both", expand=True)

        self._views: dict[str, BaseView] = {}
        self._add_view("home", HomeView(self))
        self._add_view("check_project", CheckProjectView(self))
        self._add_view("new_project", NewProjectView(self))
        self._add_view("add_existing", UpdateProjectView(
            self, "Adicionar o SFK a um projeto existente",
            "Instala o SFK sobre um código existente, sem tocar no seu código.",
        ))
        self._add_view("update_project", UpdateProjectView(
            self, "Atualizar o SFK de um projeto",
            "Traz a versão mais nova. Migra automaticamente projetos com layout antigo.",
        ))
        self._add_view("skills", ComingSoonView(self, "Skills", "Chega na Fase 4."))

        self.show("home")

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
        self._views[name].tkraise()


def main() -> int:
    app = App()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
