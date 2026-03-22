#!/bin/bash
# Optional helper — user can also just git clone directly.
# Usage:
#   ./setup.sh --project   installs into current project .claude/
#   ./setup.sh --global    installs into ~/.claude/
#   ./setup.sh --remove    removes from current project

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ "$1" = "--project" ]; then
    mkdir -p .claude/agents .claude/skills
    cp -r "$REPO_DIR/agents/"* .claude/agents/
    cp -r "$REPO_DIR/skills/"* .claude/skills/
    cp "$REPO_DIR/CLAUDE.md" .claude/
    echo "Done. Agents and skills installed into .claude/"
    echo "Restart Claude Code to load agents."

elif [ "$1" = "--global" ]; then
    mkdir -p ~/.claude/agents ~/.claude/skills
    cp -r "$REPO_DIR/agents/"* ~/.claude/agents/
    cp -r "$REPO_DIR/skills/"* ~/.claude/skills/
    cp "$REPO_DIR/CLAUDE.md" ~/.claude/
    echo "Done. Installed globally into ~/.claude/"
    echo "Restart Claude Code to load agents."

elif [ "$1" = "--remove" ]; then
    rm -rf .claude/agents .claude/skills .claude/CLAUDE.md
    echo "Removed from current project."

else
    echo "Usage: ./setup.sh --project | --global | --remove"
fi
