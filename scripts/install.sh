#!/usr/bin/env bash
# Install ygg-build skills into ~/.claude (global) or ./.claude (local)
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MODE="${1:-local}"

case "$MODE" in
  global)
    TARGET="$HOME/.claude"
    ;;
  local)
    TARGET="$(pwd)/.claude"
    ;;
  *)
    echo "Usage: $0 [global|local]" >&2
    echo "  global — installs to ~/.claude (available in all projects)" >&2
    echo "  local  — installs to ./.claude (available in this project only)" >&2
    exit 1
    ;;
esac

echo "Installing ygg-build skills to $TARGET ..."

mkdir -p "$TARGET/skills/ygg-build/references"
mkdir -p "$TARGET/commands/ygg-build"

cp -r "$REPO_DIR/.claude/skills/ygg-build/"  "$TARGET/skills/ygg-build/"
cp -r "$REPO_DIR/.claude/commands/ygg-build/" "$TARGET/commands/ygg-build/"

echo "✓ Claude Code skill installed."
echo "  Try: /ygg-build \"Build a research assistant that searches the web and summarizes results\""
echo ""
echo "  Commands available:"
echo "    /ygg-build <description>     — full build"
echo "    /ygg-build:preview <desc>    — blueprint only"
echo "    /ygg-build:improve <file>    — re-run improvement loop"
