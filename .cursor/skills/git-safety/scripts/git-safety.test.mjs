import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import {
  CURSOR_ANONYMOUS_EMAIL,
  commandReferencesSecret,
  extractGitIdentityEmails,
  isAllowedAnonymousEmail,
  isGitCommitCreating,
  isGitConfigMutation,
  isSecretPath,
  requiredAnonymousGitPrefix,
  scanTextForSecretRuleIds,
  usesForbiddenGitIdentity,
} from "./git-safety.mjs";

test("accepts only Cursor anonymous and GitHub noreply emails", () => {
  assert.equal(isAllowedAnonymousEmail(CURSOR_ANONYMOUS_EMAIL), true);
  assert.equal(
    isAllowedAnonymousEmail("132057194+cam-douglas@users.noreply.github.com"),
    true,
  );
  assert.equal(isAllowedAnonymousEmail("person@gmail.com"), false);
  assert.equal(isAllowedAnonymousEmail("owner@company.com"), false);
  assert.equal(isAllowedAnonymousEmail(""), false);
});

test("treats secret-bearing paths as blocked and keeps templates public", () => {
  assert.equal(isSecretPath(".env"), true);
  assert.equal(isSecretPath("apps/web/.env.production"), true);
  assert.equal(isSecretPath("certs/service.p8"), true);
  assert.equal(isSecretPath("auth.json"), true);
  assert.equal(isSecretPath("google-service-account.json"), true);
  assert.equal(isSecretPath(".env.example"), false);
  assert.equal(isSecretPath("id_ed25519.pub"), false);
});

test("requires explicit anonymous identity on commit-creating git commands", () => {
  assert.equal(isGitCommitCreating("git commit -m test"), true);
  assert.equal(isGitCommitCreating("git pull --ff-only"), false);
  assert.equal(isGitCommitCreating("git status"), false);
  assert.equal(usesForbiddenGitIdentity("git commit -m test"), true);
  assert.equal(
    usesForbiddenGitIdentity(
      `${requiredAnonymousGitPrefix()} git commit -m test`,
    ),
    false,
  );
  assert.equal(
    usesForbiddenGitIdentity(
      "GIT_AUTHOR_EMAIL='person@gmail.com' GIT_COMMITTER_EMAIL='person@gmail.com' git commit -m test",
    ),
    true,
  );
  assert.equal(
    usesForbiddenGitIdentity(
      `git -c user.email=${CURSOR_ANONYMOUS_EMAIL} -c user.name='Cursor Agent' commit -m test`,
    ),
    false,
  );
  assert.deepEqual(
    extractGitIdentityEmails(
      `${requiredAnonymousGitPrefix()} git commit -m test`,
    ),
    [CURSOR_ANONYMOUS_EMAIL, CURSOR_ANONYMOUS_EMAIL],
  );
});

test("blocks git config identity mutation and secret-path commands", () => {
  assert.equal(isGitConfigMutation("git config user.email someone@host"), true);
  assert.equal(isGitConfigMutation("git config --global user.name X"), true);
  assert.equal(isGitConfigMutation("git config --get user.email"), false);
  assert.equal(usesForbiddenGitIdentity("git config user.email x"), true);
  assert.equal(commandReferencesSecret("git add .env.local"), true);
  assert.equal(commandReferencesSecret("git add .env.example"), false);
});

test("detects secret content without needing to print it", () => {
  const pem = ["-----", "BEGIN RSA PRIVATE ", "KEY", "-----"].join("");
  assert.deepEqual(scanTextForSecretRuleIds(pem), ["private-key"]);
  assert.deepEqual(scanTextForSecretRuleIds("const token = 'not-a-secret'"), []);
});

test("token-aware merge detection: read-only merge-* allowed, real merges blocked", () => {
  assert.equal(isGitCommitCreating("git merge-base origin/main HEAD"), false);
  assert.equal(isGitCommitCreating("git merge-tree --write-tree a b"), false);
  assert.equal(isGitCommitCreating("git worktree add /tmp/x-merge-0433 origin/main"), false);
  assert.equal(isGitCommitCreating("git merge origin/main"), true);
  assert.equal(isGitCommitCreating("git merge --no-ff origin/main"), true);
  assert.equal(isGitCommitCreating("git merge --ff-only origin/main"), false);
  assert.equal(isGitCommitCreating("git merge-base a b && git merge origin/main"), true);
  assert.equal(isGitCommitCreating("git -C /tmp/r merge origin/main"), true);
  assert.equal(isGitCommitCreating("git commit -m test"), true);
  assert.equal(isGitCommitCreating("git checkout fix-commit-hook"), false);
  assert.equal(isGitCommitCreating("git pull origin main"), true);
  assert.equal(isGitCommitCreating("git rebase origin/main"), true);
});

test("allows GitHub web committer address", () => {
  assert.equal(isAllowedAnonymousEmail("noreply@github.com"), true);
  assert.equal(isAllowedAnonymousEmail("me@gmail.com"), false);
});

test("pre-push only inspects commits the server does not have", () => {
  const dir = mkdtempSync(join(tmpdir(), "gs-push-"));
  const script = fileURLToPath(new URL("./git-safety.mjs", import.meta.url));
  const git = (args, email) =>
    execFileSync("git", args, {
      cwd: dir,
      encoding: "utf8",
      env: {
        ...process.env,
        GIT_AUTHOR_NAME: "t",
        GIT_COMMITTER_NAME: "t",
        GIT_AUTHOR_EMAIL: email,
        GIT_COMMITTER_EMAIL: email,
      },
    }).trim();
  const push = (sha) =>
    spawnSync("node", [script, "push"], {
      cwd: dir,
      input: `refs/heads/x ${sha} refs/heads/x ${"0".repeat(40)}\n`,
      encoding: "utf8",
    });
  try {
    git(["init", "-q", "-b", "main"], "a@private.example");
    git(["commit", "-q", "--allow-empty", "-m", "published"], "a@private.example");
    git(["update-ref", "refs/remotes/origin/main", "HEAD"], "a@private.example");
    git(["commit", "-q", "--allow-empty", "-m", "new anonymous"], CURSOR_ANONYMOUS_EMAIL);
    assert.equal(push(git(["rev-parse", "HEAD"], CURSOR_ANONYMOUS_EMAIL)).status, 0);
    git(["commit", "-q", "--allow-empty", "-m", "new private"], "a@private.example");
    assert.equal(push(git(["rev-parse", "HEAD"], CURSOR_ANONYMOUS_EMAIL)).status, 1);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});
