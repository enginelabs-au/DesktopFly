#!/bin/sh
# Owner-run repair for git-safety protected files.
# Usage:
#   bash docs/handover/apply-git-safety.sh
#   bash docs/handover/apply-git-safety.sh /path/to/agent-instructions
set -eu

SOURCE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
TARGET_ROOT=${1:-$SOURCE_ROOT}
PAYLOAD="$SOURCE_ROOT/.cursor/skills/git-safety/payloads"

write_file() {
  src=$1
  dest=$2
  mkdir -p "$(dirname -- "$dest")"
  cat "$src" > "$dest"
  printf 'wrote: %s\n' "$dest"
}

copy_tree() {
  src=$1
  dest=$2
  mkdir -p "$dest"
  tar -C "$src" -cf - . | tar -C "$dest" -xf -
}

if [ ! -d "$PAYLOAD" ]; then
  printf 'missing payloads: %s\n' "$PAYLOAD" >&2
  exit 1
fi

mkdir -p "$TARGET_ROOT/.cursor/skills"
copy_tree "$SOURCE_ROOT/.cursor/skills/git-safety" "$TARGET_ROOT/.cursor/skills/git-safety"
copy_tree "$SOURCE_ROOT/.githooks" "$TARGET_ROOT/.githooks"
chmod +x "$TARGET_ROOT/.githooks/pre-commit" "$TARGET_ROOT/.githooks/commit-msg" "$TARGET_ROOT/.githooks/pre-push"

write_file "$PAYLOAD/policy.mjs" "$TARGET_ROOT/.cursor/hooks/policy.mjs"
write_file "$PAYLOAD/policy.test.mjs" "$TARGET_ROOT/.cursor/hooks/policy.test.mjs"
write_file "$PAYLOAD/git-privacy-and-secrets.mdc" "$TARGET_ROOT/.cursor/rules/git-privacy-and-secrets.mdc"
write_file "$PAYLOAD/bootstrap.sh" "$TARGET_ROOT/.cursor/scripts/bootstrap.sh"
write_file "$PAYLOAD/validate-agent-config.mjs" "$TARGET_ROOT/.cursor/scripts/validate-agent-config.mjs"
write_file "$PAYLOAD/cli.json" "$TARGET_ROOT/.cursor/cli.json"
chmod +x "$TARGET_ROOT/.cursor/hooks/policy.mjs" "$TARGET_ROOT/.cursor/scripts/bootstrap.sh"

if [ -f "$TARGET_ROOT/.github/workflows/agent-governance.yml" ] || [ "$TARGET_ROOT" = "$SOURCE_ROOT" ]; then
  write_file "$PAYLOAD/agent-governance.yml" "$TARGET_ROOT/.github/workflows/agent-governance.yml"
fi

if [ -d "$TARGET_ROOT/.git" ]; then
  mkdir -p "$TARGET_ROOT/.git/hooks"
  for hook in pre-commit commit-msg pre-push; do
    cat "$TARGET_ROOT/.githooks/$hook" > "$TARGET_ROOT/.git/hooks/$hook"
    chmod +x "$TARGET_ROOT/.git/hooks/$hook"
  done
fi

printf 'git-safety protected files applied: %s\n' "$TARGET_ROOT"
