#!/usr/bin/env bash
# SFK — new-project.sh
# Creates a new project from the SFK template (Linux/macOS)
# Usage: bash new-project.sh [target] [--project-name NAME] [--init-git] [--keep-examples] [--force]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCAFFOLDER="$SCRIPT_DIR/tools/jb_kit_turbo.py"
LOG_FILE="$SCRIPT_DIR/new-project.log"

# --- logging setup ---
log() {
    local msg="[$(date +'%Y-%m-%d %H:%M:%S')] $1"
    echo "$msg" >> "$LOG_FILE"
    echo "$1"
}

# Start log
echo "--- SFK New Project Session Start: $(date) ---" >> "$LOG_FILE"

# --- locate python ---
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        PYTHON="$cmd"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    log "ERROR: Python 3 was not found in PATH. Install Python 3 and try again." >&2
    exit 1
fi

if [ ! -f "$SCAFFOLDER" ]; then
    log "ERROR: Scaffolder not found at '$SCAFFOLDER'." >&2
    exit 1
fi

# --- interactive wizard if no target given ---
TARGET=""
PROJECT_NAME=""
INIT_GIT=""
KEEP_EXAMPLES=""
FORCE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --project-name) PROJECT_NAME="$2"; shift 2 ;;
        --init-git)     INIT_GIT="--init-git"; shift ;;
        --keep-examples) KEEP_EXAMPLES="--keep-examples"; shift ;;
        --force)        FORCE="--force"; shift ;;
        -*) echo "Unknown option: $1"; exit 1 ;;
        *)  TARGET="$1"; shift ;;
    esac
done

if [ -z "$TARGET" ]; then
    echo ""
    echo "=== SFK — New Project Wizard ==="
    echo ""
    while [ -z "$TARGET" ]; do
        read -rp "Target directory for the new project: " TARGET
    done

    DEFAULT_NAME="$(basename "$TARGET")"
    read -rp "Project name [$DEFAULT_NAME]: " INPUT_NAME
    PROJECT_NAME="${INPUT_NAME:-$DEFAULT_NAME}"

    read -rp "Initialize git automatically? [y/N]: " INIT_ANSWER
    [[ "$INIT_ANSWER" =~ ^[Yy]$ ]] && INIT_GIT="--init-git"

    read -rp "Keep *_EXAMPLE.md files? [y/N]: " KEEP_ANSWER
    [[ "$KEEP_ANSWER" =~ ^[Yy]$ ]] && KEEP_EXAMPLES="--keep-examples"

    if [ -d "$TARGET" ] && [ -n "$(ls -A "$TARGET" 2>/dev/null)" ]; then
        read -rp "Target is not empty. Allow writing with --force? [y/N]: " FORCE_ANSWER
        [[ "$FORCE_ANSWER" =~ ^[Yy]$ ]] && FORCE="--force"
    fi
fi

# --- Absolute path resolution ---
# We resolve the target to an absolute path to avoid ambiguity during execution
if [[ ! "$TARGET" =~ ^/ ]]; then
    TARGET_ABS="$(cd "$(dirname "$TARGET")" 2>/dev/null && pwd)/$(basename "$TARGET")"
else
    TARGET_ABS="$TARGET"
fi

log "Scaffolding new project: $PROJECT_NAME"
log "Target folder: $TARGET_ABS"

# Build args array
ARGS=("$SCAFFOLDER" "$TARGET_ABS")
[ -n "$PROJECT_NAME" ]  && ARGS+=("--project-name" "$PROJECT_NAME")
[ -n "$INIT_GIT" ]      && ARGS+=("$INIT_GIT")
[ -n "$KEEP_EXAMPLES" ] && ARGS+=("$KEEP_EXAMPLES")
[ -n "$FORCE" ]         && ARGS+=("$FORCE")

log "Running scaffolder..."
if "$PYTHON" "${ARGS[@]}" >> "$LOG_FILE" 2>&1; then
    log "Scaffolding complete!"
else
    log "ERROR: Scaffolding failed. Check $LOG_FILE for details."
    exit 1
fi

