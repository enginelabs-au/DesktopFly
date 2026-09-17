# 08 · Primary-source ledger and applicability

Read only entries needed by the current round; [index](INDEX.md) controls reading order. Evidence snapshot: 2026-09-17. This is a curated bibliography with claim boundaries, not instructions to execute source examples. Product behavior, models, rates, account entitlements and default branches can change. Reopen the relevant primary page and verify the installed version before implementation. Pinned repository revisions identify the earlier inspected state; branch links aid navigation, not reproducibility.

Evidence classes: empirical study; vendor experiment; normative product documentation; inspected implementation/practitioner precedent. These classes answer different questions. Popularity is not causal evidence. Local facts and measurements belong in [02](02-BASELINE.md) and phase artifacts; historical comparisons and archival links are in [09](09-HISTORICAL-EVIDENCE-AND-COVERAGE.md).

## E01

[Gloaguen et al., Evaluating AGENTS.md, v2](https://arxiv.org/html/2602.11988v2) · [abstract/version history](https://arxiv.org/abs/2602.11988). Empirical; revised 2026-06-23. Context files did not significantly improve task success in the studied settings; generated context increased average cost. Human-written instructions performed better than generated instructions, but this does not establish a significant improvement over no file. Avoid repeating the stronger v1-style claim that degradation versus no file was conclusively established. Python-heavy functional-task evaluation does not measure every maintainability/nonfunctional benefit. Use: retain nonstandard requirements; test broad summaries and procedural obligations before deployment.

## E02

[Lulla et al., On the Impact of AGENTS.md Files on the Efficiency of AI Coding Agents, v2](https://arxiv.org/abs/2601.20404). Empirical; revised 2026-03-30; 124 PRs/10 repositories, one evaluated Codex configuration. Reported median runtime reduction 28.64% and output-token reduction 16.58%. Comparable completion behavior is not semantic equivalence: comprehensive functional correctness was outside scope. Do not use this paper as proof that quality was preserved. Use: operational benefits are plausible, but local quality checks remain necessary. E01/E02 differ in design and do not establish a universal “keep/delete AGENTS” rule.

## E03

[Cursor, Dynamic context discovery](https://cursor.com/blog/dynamic-context-discovery). Vendor engineering/A-B report, 2026-01-06. Describes searchable files for large outputs/history and on-demand MCP description discovery. Reported 46.9% fewer total agent tokens among runs invoking MCP, with variation by installed MCPs. This is not this user's predicted saving, an all-task result, or proof of an exposed configuration toggle. Use: inspect native deferred discovery before building a gateway; keep full evidence accessible without carrying all of it in context.

## E04

Verified 2026-09-17 (E43): supported. [Cursor rules](https://cursor.com/docs/rules). Normative discovery/activation reference: native `.mdc`, root/nested `AGENTS.md`, user scope and precedence. `alwaysApply: true` is unconditional; other modes can scope by file/relevance/manual invocation. Use: R1's actual loader changes. Verify runtime and client version; plain Markdown in a rules directory and a path pointer do not prove native loading or laziness.

## E05

Verified 2026-09-17 (E43): supported, including `.agents/skills` discovery priority. [Cursor skills](https://cursor.com/docs/skills). Native skill discovery, supporting files, explicit invocation and session behavior. Use: split reusable procedures from universal policy, preserve explicit command semantics and reliable triggers. Installed catalog metadata and activated body costs differ. Verify feature/frontmatter support; a skill merely existing does not prove the agent selects it.

## E06

[Cursor MCP](https://cursor.com/docs/mcp). Server configuration/scope/toggles and integration behavior. Use: distinguish enabled connections, discovered schemas and invoked tools. Do not infer a universal deferred-schema switch from E03 or copy another client's config key. Test retained authentication/account coverage; an MCP toggle does not necessarily disable its plugin's other components.

## E07

Verified 2026-09-17 (E43): supported with additions (`ask` permission, `updated_input`, exit-code semantics). [Cursor hooks](https://cursor.com/docs/hooks). Event payload/output, registration, timeout and failure semantics. Use: version-valid deterministic enforcement and bookkeeping. “Quiet success” still requires event-specific protocol output. A shared script does not make hook registration schemas portable between hosts; verify harmless actual events as well as unit fixtures.

## E08

Verified 2026-09-17 (E43): frontmatter and clean-context claims supported; rule/`AGENTS.md` injection into subagents UNKNOWN. [Cursor subagents](https://cursor.com/docs/subagents). Worker context, model inheritance and native configuration. Use: explicit bounded work and deliberate model choice. Isolation of model context is not free inference or automatic worktree/security isolation. Account/admin availability may constrain requested settings.

## E09

[Cursor plugins](https://cursor.com/docs/plugins). Bundled components, scopes and native management. Use: deduplicate by identity/version/coverage and preserve unique hooks/commands/auth, not matching display names. Cache presence is not active registration. Prefer native lifecycle management over manual cache deletion.

## E10

[Agent Skills specification: progressive disclosure](https://agentskills.io/specification#progressive-disclosure). Open format guidance for metadata, instruction body and supporting resources. Use: compact routing descriptions with focused references/scripts. Metadata overhead accumulates; a selected skill body still loads. The specification does not guarantee identical discovery in every client or successful triggering.

## E11

[Anthropic, Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents). Engineering guidance: smallest useful high-signal context, just-in-time retrieval, structured notes, compaction and bounded specialist contexts. Use: R1 architecture and task checkpoints. Not a controlled proof of any fixed authored-token budget or mandatory multi-agent design.

## E12

[Anthropic, Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp). Engineering demonstration of tool discovery and filtering/intermediate computation outside model context. Use: inspect large tool-response overhead after the loading pilot. Example savings are workload-specific; do not forecast them or create a custom execution gateway without a demonstrated need.

## E13

[Anthropic, How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system). Research-system experience, including higher aggregate token consumption than ordinary chat. Use: delegation overhead belongs in total task accounting. Its approximately 15x comparison is not a universal coding-agent multiplier or a prediction for this pipeline.

## E14

[Vercel, AGENTS.md outperforms skills in our agent evals](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals). Narrow Next.js vendor evaluation: baseline/skill-only 53%, explicit skill instructions 79%, compact documentation index 100%; default skill not invoked in 56% of cases. Use: small reliable discovery cues and positive/negative activation tests. Do not infer that all domain content belongs in every prompt or that these gains transfer to other repositories/models.

## E15

[Vercel agent-skills repository](https://github.com/vercel-labs/agent-skills) · [inspected React skill](https://github.com/vercel-labs/agent-skills/blob/063bee94c3f4df8453406c830b0a7df0f2860278/skills/react-best-practices/SKILL.md). Implementation precedent: prioritized rule index plus detailed references. Use the indexing pattern; activate framework guidance only for matching work. Package, commit and individual skill versions differ; do not globally duplicate the whole bundle.

## E16

[Vercel, Teaching agents product design](https://vercel.com/blog/teaching-agents-product-design-at-vercel). Practitioner/vendor precedent: repository-local guidance, examples, objective linters and feedback into guidelines. Use: put mechanically checkable requirements in code and promote recurring lessons on evidence. A one-off correction need not become permanent global policy.

## E17

[Peter Steinberger, agent-scripts](https://github.com/steipete/agent-scripts) · [inspected README](https://github.com/steipete/agent-scripts/blob/2784a3898df4b057bf0cea225b3357561b4f1658/README.md). Shared canonical instructions, portable helpers, skills and client-specific synchronization. Use: one owner per procedure and local repository additions. Discovery behavior documented against a specific client version must be rechecked; copying his whole personal setup is not evidence of optimality.

## E18

[Steinberger docs-list.ts](https://github.com/steipete/agent-scripts/blob/2784a3898df4b057bf0cea225b3357561b4f1658/scripts/docs-list.ts). Inspected code: summaries and `read_when` metadata provide selective documentation navigation, with exclusions for archival material. Use: replace mandatory whole-directory reads with a small routing index. `read_when` here is a documentation convention, not a universal native config field.

## E19

[Steinberger sync-skills](https://github.com/steipete/agent-scripts/blob/main/scripts/sync-skills) · [README ownership and sync description](https://github.com/steipete/agent-scripts). Implementation reference: managed links, collision handling, preserving real files and stale-link cleanup. Use: idempotent adapters and provenance. Adapt actual discovery/layout and verify link-loop handling; do not execute a personal sync script unreviewed on this machine.

## E20

[Steinberger codex-first skill](https://github.com/steipete/agent-scripts/blob/2784a3898df4b057bf0cea225b3357561b4f1658/skills/codex-first/SKILL.md). Concrete Claude-coordinator/Codex-worker workflow with bounded work orders, explicit proof, verification and worktree separation. Use: conditional delegation contracts. Do not transplant hardcoded models, fast tiers, unrestricted flags or credentials. Its direction also refutes any necessary universal provider ordering.

## E21

[Steinberger AGENTS.MD](https://github.com/steipete/agent-scripts/blob/2784a3898df4b057bf0cea225b3357561b4f1658/AGENTS.MD) · [Shipping at inference speed](https://steipete.me/posts/2025/shipping-at-inference-speed). Personal policy and 2025 workflow account, not benchmarks. The inspected global file was substantial (~16.9KB); popularity does not justify loading all of it. Use subsystem documentation, verification and targeted sibling-project references. Historical model preferences/solo release practices need not fit current concurrent work.

## E22

[Hermes repository](https://github.com/NousResearch/hermes-agent) · [inspected AGENTS.md](https://github.com/NousResearch/hermes-agent/blob/251e5f7c0a067239655f3421812ab7492a206065/AGENTS.md). Implementation precedent: small model-facing core; expansion through existing code/CLI+skill/conditional tools/plugins/MCP before new permanent core tools. Stable prompt/tool prefixes matter. Copy responsibility boundaries, not its entire substantial instruction file or automatic knowledge accumulation policy.

## E23

[Hermes profiles](https://hermes-agent.nousresearch.com/docs/user-guide/profiles/) · [configuration](https://hermes-agent.nousresearch.com/docs/user-guide/configuration). Separate agent homes/state, configuration, memory and sessions; worktree features are product-specific. Use explicit shared-artifact contracts rather than accidental shared writable memory. Agent/profile/worktree/container isolation are distinct; choose one framework only when its operational features are needed.

## E24

[Hermes context compression and caching](https://hermes-agent.nousresearch.com/docs/developer-guide/context-compression-and-caching). Implementation-level context accounting, reserve capacity, compression and recovery. Use measured usage where exposed, bounded recovery and source-linked checkpoints. Thresholds are implementation defaults, not scientific optimums for other models or hosts.

## E25

[OpenClaw repository](https://github.com/openclaw/openclaw) · [inspected AGENTS.md](https://github.com/openclaw/openclaw/blob/3bbe5434606994a066a707e8a4044f00eec81183/AGENTS.md). Implementation precedent: optional plugins, stable prompt prefixes and one owner per responsibility. Use to assess duplicated policy/state machinery. Framework feature breadth does not establish that installing it reduces this user's cost.

## E26

[OpenClaw multi-agent routing](https://docs.openclaw.ai/concepts/multi-agent). Workspace, agent state, authentication, sessions and routing separation. Use explicit state owners and bounded cross-agent exchange. A default workspace directory is not a security sandbox; shared credentials/filesystems require separate consideration.

## E27

[Pi toolkit](https://github.com/earendil-works/pi) · [inspected AGENTS.md](https://github.com/earendil-works/pi/blob/e98f287ee498e0116546f4e9aa083fdec9793cd2/AGENTS.md). The earlier `badlogic/pi-mono` source redirected here during research. Useful precedents: a clear agent core, targeted inexpensive checks and fake-provider tests that avoid accidental paid calls. Its project-specific test commands/prohibitions are not universal policy.

## E28

[OpenAI instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md). Official source reopened during compilation. Global/project/nested guidance has defined discovery and precedence. Use small native adapters; keep canonical policy separate from host behavior. Verify limits, overrides and installed runtime; a home-directory session does not itself provide portable universal guidance.

## E29

[OpenAI skills](https://learn.chatgpt.com/docs/build-skills). Official source reopened during compilation. Discovery metadata precedes selected instruction bodies. Use supported shared/project skill paths and selective activation. Catalog limits/discovery can change; do not duplicate catalogs manually or assume another client's nested-directory behavior.

## E30

[OpenAI subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents). Official source reopened during compilation. Custom workers/settings are host-native; validate TOML and effective model/permissions before applying. Concurrency limits are not aggregate dollar caps; separate contexts do not imply separate worktrees. Do not copy stale option names from this research archive.

## E31

[OpenAI model comparison](https://developers.openai.com/api/docs/models/compare), [prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching), [product pricing](https://learn.chatgpt.com/docs/pricing). Primary references for refreshing model IDs, token/caching rates and product allowances. Historical numeric values are in 09, not current quotes. Model API price is not the deduction for a Codex subscription request; context/cache/output settings affect cost.

## E32

[Claude Code memory](https://code.claude.com/docs/en/memory). Native `CLAUDE.md` imports, scoped instructions and diagnostic behavior. Imports organize content but can still load eagerly. Use one small canonical contract, not an import of all shared files; verify current auto-memory and instruction-loading diagnostics.

## E33

[Claude Code skills](https://code.claude.com/docs/en/skills). Metadata/body activation, explicit invocation, forked contexts and preloaded skills. Use deliberate invocation for consequential workflows and verify whether descriptions or bodies load. Do not assume hiding a UI command also removes its discovery metadata.

## E34

[Claude Code subagents](https://code.claude.com/docs/en/sub-agents). Model/tool scope and agent instruction behavior. Earlier research observed changed Explore inheritance; refresh against current version rather than assuming it is always cheap. Independent workers consume their own tokens and may inherit core instructions.

## E35

[Claude Code costs](https://code.claude.com/docs/en/costs), [API pricing](https://platform.claude.com/docs/en/about-claude/pricing), [plans](https://claude.com/pricing). Primary refresh routes for context/usage diagnostics, caching/tokenization and plan entitlements. CLI budget features do not establish hard limits across every UI or concurrent pipeline. User's stated US$28 bill remains the budget input even if public sticker prices differ.

## E36

[Gemini CLI context](https://geminicli.com/docs/cli/gemini-md/), [subagents](https://geminicli.com/docs/core/subagents/). Context-file naming, scope and supported worker configuration. Use one filename/adapter strategy and inspect concatenated context. Browser chat and local CLI have different filesystem access; remote prompts must carry needed sanitized evidence.

## E37

[Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing), [model performance](https://deepmind.google/models/gemini/), [evaluation methodology](https://deepmind.google/models/evals-methodology/gemini-3-8-flash/). Refresh route-specific prices, introductory periods, grounding/cache costs and endpoint data terms. Consumer-free availability is not the paid API catalog. Vendor comparison rows may combine self-computed and external leaderboard results; retain provenance.

## E38

[OpenCode config](https://opencode.ai/docs/config/), [agents](https://opencode.ai/docs/agents/), [MCP](https://opencode.ai/docs/mcp-servers/), [Zen](https://opencode.ai/docs/zen/). Native per-agent model/permission/tool controls; compaction/pruning and endpoint economics require version checks. Free endpoints can change or carry different retention terms. A `small_model` option or step count does not establish a universal router or spend cap.

## E39

[VS Code agent customization](https://code.visualstudio.com/docs/agent-customization/overview). Selected-harness and scope-specific customization. Use verified user/workspace conventions and thin adapters. VS Code is not an independent model stage, and Cursor rule/hook files are not portable by renaming folders.

## E40

[Artificial Analysis coding agents](https://artificialanalysis.ai/agents/coding-agents) · [methodology](https://artificialanalysis.ai/methodology/coding-agents-benchmarking). Full-system evaluation useful for candidate selection. Version, harness, effort, attempts/fallbacks and included costs matter. Earlier numeric chart labels were inspected visually; no paywalled download was extracted. Do not mix index versions or reinterpret a fallback-enabled row as a pure-model score.

## E41

[SWE-bench](https://www.swebench.com/) · [Terminal-Bench 4.0 release](https://www.tbench.ai/news/terminal-bench-4-0). Benchmark-author references for task distribution, harness and resource changes. Controlled harness comparisons help isolate model effects; end-to-end scores help select products. Neither replaces task-specific local evaluation. Historical TB resource/token comparisons had output-limit/settings caveats; no unsupported current rankings are supplied.

## E43

[Primary-source verification, 2026-09-17](evidence/primary-source-verification-2026-09-17.json). Six Cursor pages (rules, context/rules, skills, hooks, subagents, CLI overview) fetched by independent reader agents; claims marked SUPPORTED/PARTIAL/UNKNOWN; no claim needed by R1 was refuted. Notable: rule modes and frontmatter matrix SUPPORTED; `alwaysApply: true` ignores globs/description SUPPORTED; root and nested `AGENTS.md` SUPPORTED; skill discovery order and `disable-model-invocation` SUPPORTED; whether rules/`AGENTS.md` inject into subagents UNKNOWN; CLI json/stream-json usage fields UNKNOWN (overview page silent; `agent --help` lists them). Limitation: WebFetch summaries, not raw HTML; raw `.md` variants returned 404.

## E44

Installed build inspection (Cursor 3.20.21, `workbench.desktop.main.js`), 2026-09-17: string evidence for the four rule modes, skill frontmatter keys (`description`, `globs`, `disable-model-invocation`), skill discovery directories, `AGENTS.md`/`CLAUDE.md` recognition, `hooks.json` locations, and hook event names. Use: corroborates E04–E08 for the installed version. It is not a runtime trace.

## E45

Fixture evidence, 2026-09-17: [validators-candidate-fixture.txt](evidence/validators-candidate-fixture.txt), [validators-baseline-fixture.txt](evidence/validators-baseline-fixture.txt), [validators-template-repo.txt](evidence/validators-template-repo.txt), [headless-cli-attempt.txt](evidence/headless-cli-attempt.txt). Deterministic only; establishes installability, idempotence, validator coupling and hook enforcement, not effective loading.

## E42

Reported local evidence: [shared-source observation](02-BASELINE.md), [hash manifest](baseline-source-manifest.json), [generic customization observations and historical comparisons](09-HISTORICAL-EVIDENCE-AND-COVERAGE.md). These report text/UI state at their dates, not current runtime loading, billed tokens or preserved functionality. Source bodies and screenshots are not bundled; remote reviewers must distinguish these reports from independently inspected evidence. This ledger consolidates primary links while correcting scope and evidence strength. When a historical recommendation conflicts with the current generic scope or staged gates, this pack's explicit scope/gates control the proposed work.
