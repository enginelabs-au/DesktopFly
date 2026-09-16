import assert from "node:assert/strict";
import test from "node:test";

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
