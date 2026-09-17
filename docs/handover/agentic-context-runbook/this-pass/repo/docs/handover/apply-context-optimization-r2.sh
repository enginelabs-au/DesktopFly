#!/bin/sh
# Owner-authorized apply for context-optimization R1+R2 protected files.
# Usage:
#   bash docs/handover/apply-context-optimization-r2.sh
#   bash docs/handover/apply-context-optimization-r2.sh /path/to/repo
set -eu

SOURCE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
TARGET_ROOT=${1:-$SOURCE_ROOT}
PAYLOAD="$SOURCE_ROOT/docs/handover/context-optimization-r2-payloads"

write_file() {
  src=$1
  dest=$2
  mkdir -p "$(dirname -- "$dest")"
  cat "$src" > "$dest"
  printf 'wrote: %s\n' "$dest"
}

if [ ! -d "$PAYLOAD" ]; then
  printf 'missing payloads: %s\n' "$PAYLOAD" >&2
  exit 1
fi

write_file "$PAYLOAD/AGENTS.md" "$TARGET_ROOT/AGENTS.md"
write_file "$PAYLOAD/.cursorignore" "$TARGET_ROOT/.cursorignore"
write_file "$PAYLOAD/.cursor/AGENTS.md" "$TARGET_ROOT/.cursor/AGENTS.md"
write_file "$PAYLOAD/.cursor/INSTRUCTIONS.md" "$TARGET_ROOT/.cursor/INSTRUCTIONS.md"
write_file "$PAYLOAD/.cursor/instructions/ROLES.md" "$TARGET_ROOT/.cursor/instructions/ROLES.md"
write_file "$PAYLOAD/.cursor/scripts/bootstrap.sh" "$TARGET_ROOT/.cursor/scripts/bootstrap.sh"
write_file "$PAYLOAD/.cursor/scripts/validate-agent-config.mjs" "$TARGET_ROOT/.cursor/scripts/validate-agent-config.mjs"
chmod +x "$TARGET_ROOT/.cursor/scripts/bootstrap.sh"

mkdir -p "$TARGET_ROOT/.cursor/agents" "$TARGET_ROOT/.cursor/rules"

for src in "$PAYLOAD/.cursor/agents/"*.md; do
  write_file "$src" "$TARGET_ROOT/.cursor/agents/$(basename -- "$src")"
done

for src in "$PAYLOAD/.cursor/rules/"*.mdc; do
  write_file "$src" "$TARGET_ROOT/.cursor/rules/$(basename -- "$src")"
done

# Retired always-on routing rules; content now lives in 00-core-routing.mdc.
for retired in \
  00-read-agent-context-first.mdc \
  core-operating-context.mdc \
  instruction-routing.mdc \
  root-canonical.mdc \
  tools-file.mdc \
  skills-file.mdc \
  working-memory.mdc \
  state-and-compactification.mdc
do
  path="$TARGET_ROOT/.cursor/rules/$retired"
  if [ -e "$path" ]; then
    rm -- "$path"
    printf 'removed: %s\n' "$path"
  fi
done

printf 'context-optimization R2 protected files applied: %s\n' "$TARGET_ROOT"
