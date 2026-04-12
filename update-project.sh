#!/usr/bin/env bash
# SFK — update-project.sh
# Updates an existing SFK project with the latest kernel files from this template.
# Usage: bash update-project.sh [target] [--yes] [--dry-run]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UPDATER="$SCRIPT_DIR/tools/sfk_updater.py"
LOG_FILE="$SCRIPT_DIR/update-project.log"

# --- logging setup ---
log() {
    local msg="[$(date +'%Y-%m-%d %H:%M:%S')] $1"
    echo "$msg" >> "$LOG_FILE"
    echo "$1"
}

# Start log entry
echo "" >> "$LOG_FILE"
echo "--- SFK Update Project Session Start: $(date) ---" >> "$LOG_FILE"

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

if [ ! -f "$UPDATER" ]; then
    log "ERROR: Updater engine not found at '$UPDATER'." >&2
    exit 1
fi

# --- parse arguments ---
TARGET=""
YES_FLAG=""
DRY_RUN_FLAG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --yes|-y)     YES_FLAG="--yes";     shift ;;
        --dry-run|-n) DRY_RUN_FLAG="--dry-run"; shift ;;
        -*)  echo "Unknown option: $1"; exit 1 ;;
        *)   TARGET="$1"; shift ;;
    esac
done

# --- interactive wizard if no target given ---
if [ -z "$TARGET" ]; then
    echo ""
    echo "=== SFK — Update Project Wizard ==="
    echo ""
    while [ -z "$TARGET" ]; do
        read -rp "Path to the existing project to update: " TARGET
    done
fi

# Resolve to absolute path
if [[ ! "$TARGET" =~ ^/ ]]; then
    TARGET_ABS="$(cd "$(dirname "$TARGET")" 2>/dev/null && pwd)/$(basename "$TARGET")"
else
    TARGET_ABS="$TARGET"
fi

log "Updating project: $TARGET_ABS"
[ -n "$DRY_RUN_FLAG" ] && log "Mode: dry-run (no files will be written)"

# Build args
ARGS=("$UPDATER" "$TARGET_ABS")
[ -n "$YES_FLAG" ]     && ARGS+=("$YES_FLAG")
[ -n "$DRY_RUN_FLAG" ] && ARGS+=("$DRY_RUN_FLAG")

log "Running updater..."
if "$PYTHON" "${ARGS[@]}" 2>&1 | tee -a "$LOG_FILE"; then
    log "Update complete!"
else
    log "ERROR: Update failed. Check $LOG_FILE for details."
    exit 1
fi
