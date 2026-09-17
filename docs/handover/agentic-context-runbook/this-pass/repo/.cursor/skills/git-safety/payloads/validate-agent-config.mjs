#!/usr/bin/env node

import {
  lstatSync,
  readdirSync,
  readFileSync,
  realpathSync,
  statSync,
} from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const configDir = resolve(scriptDir, "..");
const repoRoot = resolve(configDir, "..");
const errors = [];
const installMode = process.env.AGENT_CONFIG_INSTALLING === "1";
const installingFiles = new Map([
  [".cursor/hooks.json", ".cursor/hooks.json.installing"],
  [".cursor/cli.json", ".cursor/cli.json.installing"],
  [".cursor/permissions.json", ".cursor/permissions.json.installing"],
]);

const roleExpectations = new Map([
  ["product-manager-subagent", true],
  ["ui-ux-developer-subagent", true],
  ["software-engineer-subagent", false],
  ["security-engineer-subagent", true],
  ["growth-marketing-subagent", true],
  ["project-lead-subagent", true],
]);

const requiredFiles = [
  "AGENTS.md",
  ".cursorignore",
  "docs/README.md",
  "docs/workstreams/README.md",
  "docs/handover/agent-governance-operator-setup.md",
  ".githooks/pre-commit",
  ".githooks/commit-msg",
  ".githooks/pre-push",
  ".cursor/AGENTS.md",
  ".cursor/BOOTSTRAP.md",
  ".cursor/INSTRUCTIONS.md",
  ".cursor/STATE.md",
  ".cursor/SKILLS.md",
  ".cursor/TOOLS.md",
  ".cursor/USER.md",
  ".cursor/instructions/PROJECT_PLANNING.md",
  ".cursor/instructions/STRATEGY.md",
  ".cursor/instructions/SUBAGENTS.md",
  ".cursor/instructions/ROLES.md",
  ".cursor/instructions/LAUNCH.md",
  ".cursor/skills/launch-pipeline/SKILL.md",
  ".cursor/skills/git-safety/SKILL.md",
  ".cursor/skills/git-safety/scripts/git-safety.mjs",
  ".cursor/rules/git-privacy-and-secrets.mdc",
  ".cursor/hooks.json",
  ".cursor/hooks/policy.mjs",
  ".cursor/hooks/policy.test.mjs",
  ".cursor/cli.json",
  ".cursor/sandbox.json",
  ".cursor/permissions.json",
  ".cursor/templates/workstreams-readme.md",
  ".cursor/templates/workstream-manifest-template.md",
  ".cursor/templates/role-charter-template.md",
  ".cursor/templates/role-plan-template.md",
  ".cursor/templates/role-evidence-template.md",
  ".cursor/templates/role-handoff-template.md",
  ".cursor/templates/owner-handoff-template.md",
  ".github/workflows/agent-governance.yml",
];

function pathFor(relativePath) {
  const effectivePath =
    installMode && installingFiles.has(relativePath)
      ? installingFiles.get(relativePath)
      : relativePath;
  return resolve(repoRoot, effectivePath);
}

function read(relativePath) {
  return readFileSync(pathFor(relativePath), "utf8");
}

function expect(condition, message) {
  if (!condition) errors.push(message);
}

for (const relativePath of requiredFiles) {
  try {
    expect(
      statSync(pathFor(relativePath)).size > 0,
      `${relativePath} is empty`,
    );
  } catch {
    errors.push(`${relativePath} is missing`);
  }
}

for (const relativePath of [
  ".cursor/hooks.json",
  ".cursor/cli.json",
  ".cursor/sandbox.json",
  ".cursor/permissions.json",
  ".cursor/config/settings.json",
]) {
  try {
    JSON.parse(read(relativePath));
  } catch (error) {
    errors.push(`${relativePath} is not valid JSON: ${error.message}`);
  }
}

try {
  const roles = read(".cursor/instructions/ROLES.md");
  for (const roleId of roleExpectations.keys()) {
    expect(roles.includes(roleId), `ROLES.md does not define ${roleId}`);
  }
  for (const requiredTerm of [
    "docs/workstreams/<task-id>/",
    "PASS",
    "CONDITIONAL",
    "BLOCKED",
    "risk",
    "handoff",
    "exhaustive",
  ]) {
    expect(
      roles.toLowerCase().includes(requiredTerm.toLowerCase()),
      `ROLES.md is missing required contract term: ${requiredTerm}`,
    );
  }
} catch {
  // Missing file is reported above.
}

for (const [roleId, readonly] of roleExpectations) {
  const relativePath = `.cursor/agents/${roleId}.md`;
  try {
    const text = read(relativePath);
    const frontmatter = text.match(/^---\n([\s\S]*?)\n---/);
    expect(Boolean(frontmatter), `${relativePath} has no YAML frontmatter`);
    if (!frontmatter) continue;

    const body = frontmatter[1];
    expect(
      new RegExp(`^name:\\s*${roleId}\\s*$`, "m").test(body),
      `${relativePath} has the wrong name`,
    );
    expect(
      /^description:\s*.+$/m.test(body),
      `${relativePath} has no description`,
    );
    expect(
      /^model:\s*inherit\s*$/m.test(body),
      `${relativePath} must inherit the parent model`,
    );
    expect(
      new RegExp(`^readonly:\\s*${readonly}\\s*$`, "m").test(body),
      `${relativePath} has the wrong readonly value`,
    );
    expect(
      /^is_background:\s*false\s*$/m.test(body),
      `${relativePath} must not run in the background by default`,
    );
    expect(
      text.includes(".cursor/instructions/ROLES.md"),
      `${relativePath} does not reference the canonical role catalog`,
    );
  } catch {
    errors.push(`${relativePath} is missing`);
  }
}

try {
  const hooks = JSON.parse(read(".cursor/hooks.json"));
  expect(hooks.version === 1, ".cursor/hooks.json must use version 1");
  for (const event of [
    "preToolUse",
    "beforeReadFile",
    "beforeShellExecution",
    "beforeMCPExecution",
    "subagentStart",
  ]) {
    const entries = hooks.hooks?.[event];
    expect(Array.isArray(entries) && entries.length > 0, `missing ${event} hook`);
    for (const entry of entries ?? []) {
      expect(
        entry.command === "node .cursor/hooks/policy.mjs",
        `${event} must call the deterministic policy`,
      );
      expect(entry.failClosed === true, `${event} must fail closed`);
    }
  }
} catch {
  // Invalid JSON is reported above.
}

const alwaysOnRules = ["00-core-routing.mdc", "git-privacy-and-secrets.mdc", "karpathy-guidelines.mdc"];
const retiredRules = [
  "01-per-turn-read-contract.mdc",
  "00-read-agent-context-first.mdc",
  "core-operating-context.mdc",
  "instruction-routing.mdc",
  "root-canonical.mdc",
  "tools-file.mdc",
  "skills-file.mdc",
  "working-memory.mdc",
  "state-and-compactification.mdc",
];
const eagerLoadPhrases = [
  /read every (?:existing )?file under/i,
  /on every (?:substantive|new) (?:turn|user message)[^.\n]*\bread\b/i,
  /\bread\b[^.\n]*on every (?:substantive|new) (?:turn|user message)/i,
  /even if it was read earlier/i,
  /read it on every substantive turn/i,
  /reread .{0,40}(?:every|each) (?:substantive )?turn/i,
];

function rejectEagerLoad(relativePath, text) {
  for (const pattern of eagerLoadPhrases) {
    expect(
      !pattern.test(text),
      `${relativePath} reintroduces a per-turn read-all mandate (matched ${pattern})`,
    );
  }
}

try {
  const ruleDir = pathFor(".cursor/rules");
  const rules = readdirSync(ruleDir).filter((name) => name.endsWith(".mdc"));
  expect(rules.length > 0, "no project rules found");
  for (const retired of retiredRules) {
    expect(
      !rules.includes(retired),
      `retired rule ${retired} still exists; its content lives in 00-core-routing.mdc`,
    );
  }
  for (const required of alwaysOnRules) {
    expect(rules.includes(required), `${required} rule is missing`);
  }
  for (const name of rules) {
    const text = read(`.cursor/rules/${name}`);
    const frontmatter = text.match(/^---\n([\s\S]*?)\n---/);
    expect(Boolean(frontmatter), `.cursor/rules/${name} lacks YAML frontmatter`);
    if (!frontmatter) continue;
    const body = frontmatter[1];
    const alwaysOn = /^alwaysApply:\s*true\s*$/m.test(body);
    const conditional = /^alwaysApply:\s*false\s*$/m.test(body);
    const hasDescription = /^description:\s*\S/m.test(body);
    const hasGlobs = /^globs:\s*\S/m.test(body);
    expect(
      alwaysOn || conditional,
      `.cursor/rules/${name} must declare alwaysApply: true or alwaysApply: false`,
    );
    if (alwaysOnRules.includes(name)) {
      expect(alwaysOn, `.cursor/rules/${name} must remain always-on`);
    }
    if (conditional) {
      expect(
        hasDescription || hasGlobs,
        `.cursor/rules/${name} is conditional but has neither a description nor globs, so the agent cannot discover it`,
      );
    }
    rejectEagerLoad(`.cursor/rules/${name}`, text);
  }
} catch (error) {
  errors.push(`could not validate rules: ${error.message}`);
}

for (const relativePath of [
  "AGENTS.md",
  ".cursor/AGENTS.md",
  ".cursor/INSTRUCTIONS.md",
  ".cursor/BOOTSTRAP.md",
  ".cursor/memory/MEMORY.md",
  ".cursor/instructions/ROLES.md",
  ".cursor/instructions/SUBAGENTS.md",
  ".cursor/skills/launch-pipeline/SKILL.md",
]) {
  try {
    rejectEagerLoad(relativePath, read(relativePath));
  } catch {
    // Missing file is reported above.
  }
}

for (const [relativePath, terms] of [
  ["AGENTS.md", [".cursor/AGENTS.md", ".cursor/instructions/ROLES.md", "/launch-pipeline"]],
  [
    ".cursor/INSTRUCTIONS.md",
    ["/instructions/ROLES.md", "/instructions/LAUNCH.md", "docs/workstreams/"],
  ],
  [
    ".cursor/instructions/SUBAGENTS.md",
    [...roleExpectations.keys()],
  ],
  [
    ".cursor/STATE.md",
    ["Active Workstream", "Active Role and Gate", "Owner Decision"],
  ],
  [
    ".cursor/BOOTSTRAP.md",
    ["docs/workstreams", "validate-agent-config.mjs", ".githooks"],
  ],
  [
    ".cursor/USER.md",
    ["cursoragent@noreply.github.com", "Never store secret values"],
  ],
  [
    ".cursor/skills/git-safety/SKILL.md",
    ["cursoragent@noreply.github.com", "GIT_AUTHOR_EMAIL", "scripts/git-safety.mjs"],
  ],
  [
    ".cursor/hooks/policy.mjs",
    ["usesForbiddenGitIdentity", "cursoragent@noreply.github.com"],
  ],
]) {
  try {
    const text = read(relativePath);
    for (const term of terms) {
      expect(text.includes(term), `${relativePath} does not reference ${term}`);
    }
  } catch {
    // Missing file is reported above.
  }
}

try {
  const compatibilityLink = pathFor(".cursor/settings.json");
  expect(lstatSync(compatibilityLink).isSymbolicLink(), ".cursor/settings.json is not a symlink");
  expect(
    realpathSync(compatibilityLink) ===
      realpathSync(pathFor(".cursor/config/settings.json")),
    ".cursor/settings.json does not resolve to config/settings.json",
  );
} catch (error) {
  errors.push(`settings compatibility link is invalid: ${error.message}`);
}

if (errors.length > 0) {
  for (const error of errors) process.stderr.write(`validation error: ${error}\n`);
  process.exit(1);
}

process.stdout.write("agent config validation complete\n");
