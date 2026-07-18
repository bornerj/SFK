#!/usr/bin/env python3
"""
SFK Launcher GUI — translation strings (PT/EN) and language preference.

Zero-install: pure stdlib, no gettext/Babel. Every user-facing string in
bin/sfk_gui.py has a key here; widgets that need to update on a language
switch keep a reference to themselves and re-read Lang.t(key) — see
`retranslate()` methods in bin/sfk_gui.py.
"""

from __future__ import annotations

from pathlib import Path

PREF_FILE = Path.home() / ".sfk_launcher_lang"
DEFAULT_LANG = "pt"
LANGUAGES = ("pt", "en")

STRINGS: dict[str, dict[str, str]] = {
    "pt": {
        "app.title": "SFK Launcher",
        "common.back": "←  Início",
        "common.browse": "\U0001F4C1  Procurar…",
        "common.choose_folder_dialog": "Escolha a pasta",
        "common.open_folder": "\U0001F4C2  Abrir pasta",
        "common.output": "Saída",
        "common.error_done": "❌  Terminou com erro (código {code}).",
        "common.lang_pt": "PT",
        "common.lang_en": "EN",

        "home.title": "SFK Launcher",
        "home.subtitle": "O que você quer fazer?",
        "home.action.new_project.title": "Criar um projeto novo",
        "home.action.new_project.subtitle": "Começar do zero com o SFK já instalado.",
        "home.action.add_existing.title": "Adicionar o SFK a um projeto que já existe",
        "home.action.add_existing.subtitle": "Instalar o SFK sobre um código existente, sem tocar nele.",
        "home.action.update_project.title": "Atualizar o SFK de um projeto",
        "home.action.update_project.subtitle": "Trazer a versão mais nova (migra layout antigo automaticamente).",
        "home.action.skills.title": "Skills — importar ou atualizar",
        "home.action.skills.subtitle": "Adicionar conhecimento novo ao SFK ou sincronizar o existente.",
        "home.action.check_project.title": "Checar um projeto",
        "home.action.check_project.subtitle": "Ver o que mudaria, sem alterar nada (pré-visualização).",

        "check.header_title": "Checar um projeto",
        "check.header_subtitle": "Mostra o que mudaria — não altera nada no disco.",
        "check.folder_label": "Pasta do projeto",
        "check.run_button": "\U0001F50E  Checar agora",
        "check.err_no_folder": "⚠️  Escolha uma pasta primeiro.",
        "check.checking": "Checando: {target}",
        "check.done_ok": "✅  Verificação concluída.",

        "new.header_title": "Criar um projeto novo",
        "new.header_subtitle": "Começar do zero, com o SFK já instalado e organizado.",
        "new.anchor_label": "Onde criar o projeto",
        "new.anchor_hint": "Escolha a pasta que vai CONTER a pasta do novo projeto.",
        "new.name_label": "Nome do projeto",
        "new.name_hint": "Vira o nome da pasta e o nome do projeto dentro dos arquivos de configuração.",
        "new.checkbox_git": "Iniciar controle de versão (git) e ativar a proteção automática de memória",
        "new.checkbox_force": "Permitir criar dentro de uma pasta que já existe e não está vazia",
        "new.run_button": "\U0001F331  Criar projeto",
        "new.err_no_parent": "Escolha onde criar o projeto primeiro.",
        "new.err_parent_missing": "A pasta escolhida não existe mais — escolha novamente.",
        "new.err_no_name": "Dê um nome ao projeto.",
        "new.err_bad_name": "O nome não pode conter barras nem ser '.' ou '..'.",
        "new.err_target_exists": "A pasta '{name}' já existe e não está vazia. Marque a opção de permitir, se tiver certeza.",
        "new.creating": "Criando projeto em: {target}",
        "new.created_ok": "✅  Projeto criado com sucesso.",
        "new.created_banner": "Projeto criado em: {target}",
        "new.failed_banner": "Não foi possível criar o projeto — veja a saída acima.",

        "update.route.add_existing.title": "Adicionar o SFK a um projeto existente",
        "update.route.add_existing.subtitle": "Instala o SFK sobre um código existente, sem tocar no seu código.",
        "update.route.update_project.title": "Atualizar o SFK de um projeto",
        "update.route.update_project.subtitle": "Traz a versão mais nova. Migra automaticamente projetos com layout antigo.",
        "update.anchor_label": "Pasta do projeto",
        "update.checkbox_skip_backup": "Pular o backup automático antes de migrar (não recomendado)",
        "update.preview_button": "\U0001F50E  Pré-visualizar (não altera nada)",
        "update.apply_button": "✅  Aplicar alterações",
        "update.err_no_folder": "⚠️  Escolha uma pasta de projeto existente primeiro.",
        "update.previewing": "Pré-visualizando: {target}",
        "update.preview_required": "Pré-visualize esta pasta primeiro (botão acima) antes de aplicar.",
        "update.apply_confirm_title": "Confirmar alterações",
        "update.apply_confirm_message": "Isso vai instalar/atualizar o SFK nesta pasta de verdade.\n\nPasta: {target}\n\nVocê já viu a pré-visualização acima. Continuar?",
        "update.applying": "Aplicando em: {target}",
        "update.preview_done": "✅  Pré-visualização concluída. Nada foi alterado.",
        "update.apply_done": "✅  Alterações aplicadas com sucesso.",
        "update.applied_banner": "SFK instalado/atualizado em: {target}",
        "update.failed_banner": "Algo deu errado — veja a saída acima.",

        "skills.header_title": "Skills",
        "skills.header_subtitle": "Adicionar conhecimento novo ao SFK ou sincronizar o existente.",
        "skills.import_anchor": "Importar uma skill nova",
        "skills.import_hint": "Escolha a pasta da skill (deve conter um SKILL.md).",
        "skills.import_button": "\U0001F9E9  Importar skill",
        "skills.sync_title": "Atualizar as skills de um projeto",
        "skills.sync_hint": "Skills fazem parte do motor do SFK — sincronizadas junto com o resto do engine.",
        "skills.sync_button": "⬆️  Ir para Atualizar/Adicionar",
        "skills.installed_title": "Skills já instaladas neste SFK",
        "skills.overwrite_confirm_title": "Sobrescrever skill?",
        "skills.overwrite_confirm_message": "A skill '{skill_name}' já existe neste SFK.\nDeseja sobrescrevê-la?",
        "skills.err_no_folder": "Escolha a pasta de uma skill existente primeiro.",
        "skills.imported_ok": "Skill '{skill_name}' importada com sucesso.",
        "skills.import_failed": "Não foi possível importar '{skill_name}'.\n{detail}",

        "comingsoon.note": "\U0001F6A7  Em construção nesta fase do plano.",
    },
    "en": {
        "app.title": "SFK Launcher",
        "common.back": "←  Home",
        "common.browse": "\U0001F4C1  Browse…",
        "common.choose_folder_dialog": "Choose the folder",
        "common.open_folder": "\U0001F4C2  Open folder",
        "common.output": "Output",
        "common.error_done": "❌  Finished with an error (code {code}).",
        "common.lang_pt": "PT",
        "common.lang_en": "EN",

        "home.title": "SFK Launcher",
        "home.subtitle": "What do you want to do?",
        "home.action.new_project.title": "Create a new project",
        "home.action.new_project.subtitle": "Start from scratch with SFK already installed.",
        "home.action.add_existing.title": "Add SFK to an existing project",
        "home.action.add_existing.subtitle": "Install SFK on top of existing code, without touching it.",
        "home.action.update_project.title": "Update SFK on a project",
        "home.action.update_project.subtitle": "Bring the latest version (auto-migrates old layouts).",
        "home.action.skills.title": "Skills — import or update",
        "home.action.skills.subtitle": "Add new knowledge to SFK or sync what's already there.",
        "home.action.check_project.title": "Check a project",
        "home.action.check_project.subtitle": "See what would change, without altering anything (preview).",

        "check.header_title": "Check a project",
        "check.header_subtitle": "Shows what would change — nothing on disk is altered.",
        "check.folder_label": "Project folder",
        "check.run_button": "\U0001F50E  Check now",
        "check.err_no_folder": "⚠️  Choose a folder first.",
        "check.checking": "Checking: {target}",
        "check.done_ok": "✅  Check complete.",

        "new.header_title": "Create a new project",
        "new.header_subtitle": "Start from scratch, with SFK already installed and organized.",
        "new.anchor_label": "Where to create the project",
        "new.anchor_hint": "Choose the folder that will CONTAIN the new project's folder.",
        "new.name_label": "Project name",
        "new.name_hint": "Becomes the folder name and the project name inside the config files.",
        "new.checkbox_git": "Initialize version control (git) and enable automatic memory protection",
        "new.checkbox_force": "Allow creating inside a folder that already exists and isn't empty",
        "new.run_button": "\U0001F331  Create project",
        "new.err_no_parent": "Choose where to create the project first.",
        "new.err_parent_missing": "The chosen folder no longer exists — choose again.",
        "new.err_no_name": "Give the project a name.",
        "new.err_bad_name": "The name can't contain slashes or be '.' or '..'.",
        "new.err_target_exists": "The folder '{name}' already exists and isn't empty. Check the allow option if you're sure.",
        "new.creating": "Creating project at: {target}",
        "new.created_ok": "✅  Project created successfully.",
        "new.created_banner": "Project created at: {target}",
        "new.failed_banner": "Could not create the project — see the output above.",

        "update.route.add_existing.title": "Add SFK to an existing project",
        "update.route.add_existing.subtitle": "Installs SFK on top of existing code, without touching your code.",
        "update.route.update_project.title": "Update SFK on a project",
        "update.route.update_project.subtitle": "Brings the latest version. Automatically migrates projects with an old layout.",
        "update.anchor_label": "Project folder",
        "update.checkbox_skip_backup": "Skip the automatic backup before migrating (not recommended)",
        "update.preview_button": "\U0001F50E  Preview (changes nothing)",
        "update.apply_button": "✅  Apply changes",
        "update.err_no_folder": "⚠️  Choose an existing project folder first.",
        "update.previewing": "Previewing: {target}",
        "update.preview_required": "Preview this folder first (button above) before applying.",
        "update.apply_confirm_title": "Confirm changes",
        "update.apply_confirm_message": "This will actually install/update SFK in this folder.\n\nFolder: {target}\n\nYou've already seen the preview above. Continue?",
        "update.applying": "Applying to: {target}",
        "update.preview_done": "✅  Preview complete. Nothing was changed.",
        "update.apply_done": "✅  Changes applied successfully.",
        "update.applied_banner": "SFK installed/updated at: {target}",
        "update.failed_banner": "Something went wrong — see the output above.",

        "skills.header_title": "Skills",
        "skills.header_subtitle": "Add new knowledge to SFK or sync what's already there.",
        "skills.import_anchor": "Import a new skill",
        "skills.import_hint": "Choose the skill's folder (must contain a SKILL.md).",
        "skills.import_button": "\U0001F9E9  Import skill",
        "skills.sync_title": "Update a project's skills",
        "skills.sync_hint": "Skills are part of the SFK engine — synced together with the rest of it.",
        "skills.sync_button": "⬆️  Go to Update/Add",
        "skills.installed_title": "Skills already installed in this SFK",
        "skills.overwrite_confirm_title": "Overwrite skill?",
        "skills.overwrite_confirm_message": "The skill '{skill_name}' already exists in this SFK.\nOverwrite it?",
        "skills.err_no_folder": "Choose an existing skill folder first.",
        "skills.imported_ok": "Skill '{skill_name}' imported successfully.",
        "skills.import_failed": "Could not import '{skill_name}'.\n{detail}",

        "comingsoon.note": "\U0001F6A7  Under construction in this phase of the plan.",
    },
}


class Lang:
    """Tiny language-state singleton — mirrors the existing `Fonts`/`Theme`
    module-level-class pattern already used in sfk_gui.py."""

    current: str = DEFAULT_LANG
    _listeners: list = []

    @classmethod
    def t(cls, key: str) -> str:
        return STRINGS[cls.current][key]

    @classmethod
    def load(cls) -> None:
        try:
            value = PREF_FILE.read_text(encoding="utf-8").strip()
        except OSError:
            value = ""
        cls.current = value if value in LANGUAGES else DEFAULT_LANG

    @classmethod
    def save(cls) -> None:
        try:
            PREF_FILE.write_text(cls.current, encoding="utf-8")
        except OSError:
            pass  # best-effort preference persistence; never worth crashing over

    @classmethod
    def on_change(cls, callback) -> None:
        """Register a no-arg callback invoked after `set()` switches language."""
        cls._listeners.append(callback)

    @classmethod
    def set(cls, lang: str) -> None:
        if lang not in LANGUAGES or lang == cls.current:
            return
        cls.current = lang
        cls.save()
        for callback in cls._listeners:
            callback()
