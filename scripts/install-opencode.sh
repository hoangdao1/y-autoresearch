#!/usr/bin/env bash
# Install ygg_build skills into .opencode (local to this project)
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="$(pwd)/.opencode"

echo "Installing ygg_build skills to $TARGET ..."

mkdir -p "$TARGET/skills/ygg_build/references"
mkdir -p "$TARGET/commands"

cp -r "$REPO_DIR/.opencode/skills/ygg_build/"  "$TARGET/skills/ygg_build/"
cp -r "$REPO_DIR/.opencode/commands/"*.md       "$TARGET/commands/"

echo "✓ OpenCode skill installed."
echo "  Try: /ygg_build Build a research assistant that searches the web and summarizes results"
echo ""
echo "  Commands available:"
echo "    /ygg_build <description>       — full build"
echo "    /ygg_build_preview <desc>      — blueprint only"
echo "    /ygg_build_improve <file>      — re-run improvement loop"
