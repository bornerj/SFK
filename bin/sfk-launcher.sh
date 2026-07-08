#!/usr/bin/env bash
# SFK Launcher — double-click entry point (Linux/macOS)
# Usage:
#   bash sfk-launcher.sh                 # opens the GUI
#   bash sfk-launcher.sh --install-desktop  # adds a menu shortcut (Linux)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUI="$SCRIPT_DIR/sfk_gui.py"

PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        PYTHON="$cmd"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERRO: Python 3 não encontrado no PATH. Instale o Python 3 e tente de novo." >&2
    exit 1
fi

if [ "${1:-}" = "--install-desktop" ]; then
    APPS_DIR="$HOME/.local/share/applications"
    mkdir -p "$APPS_DIR"
    DESKTOP_FILE="$APPS_DIR/sfk-launcher.desktop"
    cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=SFK Launcher
Comment=Interface gráfica para o SFK — Structured Framework Kit
Exec=bash "$SCRIPT_DIR/sfk-launcher.sh"
Icon=$SCRIPT_DIR/sfk-launcher.png
Terminal=false
Categories=Development;
EOF
    chmod +x "$DESKTOP_FILE"
    echo "✅ Atalho instalado em: $DESKTOP_FILE"
    echo "   Ele deve aparecer no menu de aplicativos em alguns segundos."
    exit 0
fi

exec "$PYTHON" "$GUI"
