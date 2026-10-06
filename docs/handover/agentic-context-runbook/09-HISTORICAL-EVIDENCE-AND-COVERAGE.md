# 09 · Historical observations, research preservation, coverage

Read when: a phase needs historical provenance, pricing/benchmark context, screenshot mapping, or a completeness check. Return to [index](INDEX.md). All numeric market/benchmark data below is **HISTORICAL**, copied from the 2026-09-17 research record, not newly measured during runbook compilation. Refresh primary sources in [08](08-EVIDENCE.md) before using these values for spending or routing. The present shared source differs from prior deployed copies; do not merge their counts.

**Provenance and corrections.** This self-contained pack consolidates the generic architecture, customization observations and primary research from the supplied material. Original reports, application-specific details and provider-specific handover prompts are excluded. Scope: shared `agent-instructions/.cursor` and active Cursor customization; phased implementation proposed for later authorization; first prove the loading intervention. Fixed provider-stage sequences become optional task routes. Broad rebuilding becomes gated work. Exact model choices/token targets remain hypotheses. Research on operational efficiency is not proof of semantic correctness; see E01/E02.

**Reported evidence boundary.** The screenshots and original local source bodies are not bundled. The observations below are historical audit reports, not independently inspectable runtime evidence for a remote reviewer. Primary research URLs and relevant generic claims are consolidated here and in [08](08-EVIDENCE.md). Shared-source counts and hash provenance are in [02](02-BASELINE.md): 15 rules and 45,966 core characters; neither corpus size nor hashes establish injected/billed tokens. Missing runtime evidence remains an implementation prerequisite, not a reason to fabricate measurements during proposal revision.

**Screenshots, all 16 reviewed.** Capture date 2026-09-17; IDs match original user order. Hidden “show more” entries were not visually enumerated.

| ID / capture time | Visible evidence | Implication to test |
|---|---|---|
| 1 / 19:53:04 | Vercel lifecycle hooks; custom policy at five events; execution log empty | Registration is not execution proof; inspect duplication/payloads |
| 2 / 19:53:00 | Two Vercel distributions with startup/end hooks; Astronomer prompt/stop hooks | Different functions can share event names; compare bodies and scope |
| 3 / 19:52:56 | Overlapping Vercel bootstrap/deploy/env/status/marketplace commands; Appwrite deploy commands | Preserve unique commands/auth; thin entry points |
| 4 / 19:52:52 | Slack digest/draft/discussion/standup/summary commands and Vercel commands | Communications/release are conditional domains |
| 5 / 19:52:46 | Repeated AGENTS entries and governance/planning/memory/tool rules | UI names do not establish body identity; trace inheritance |
| 6 / 19:52:42 | An 18-entry rules group including two AGENTS labels | A UI grouping and the shared source's 15-rule inventory have different scope |
| 7 / 19:52:35 | Six-role group; five visible product/growth/lead/security/software agents | Role availability need not mean six agents on every task |
| 8 / 19:52:30 | Vercel architect/deployment/performance agents; Apify; README-labelled entry | Inspect registration validity and duplication |
| 9 / 19:52:25 | Four compatibility-review agents and another Vercel trio | Onboarding/validation reviews can be explicit workflows |
| 10 / 19:52:14 | 100 plugin-contributed skill entries; visible 1inch family; four custom skills | Skill-group count is not installed-plugin count; metadata/body costs differ |
| 11 / 19:52:05 | Vercel skill groups of 33 and 25 with shared names | Locally compare versions, hashes and unique coverage |
| 12 / 19:52:00 | Docs/PR canvases and Slack development/messaging skills | Keep specialized presentation/comms skills available by need |
| 13 / 19:51:55 | Memory 9, Slack 27, time 2, Vercel 37, XcodeBuild 58 enabled tools | Domain scope/deferred discovery matter more than counts alone |
| 14 / 19:51:48 | GitHub user 26 + plugin 45 tools | Compare authentication/account/tool coverage before consolidation |
| 15 / 19:51:41 | Cline 5, Context7 2, fetch 1, filesystem 14; several disabled integrations | Native overlap and incorrect global directory bindings are leads |
| 16 / 19:51:31 | Nine installed plugins: two Vercel variants, Slack, compatibility, Astronomer, two canvases, Arize, GitHub | Installed != enabled != injected != invoked |

Unique visible enabled total: 5+2+1+14+26+45+9+27+2+37+58 = **226 tool entries across 11 connections**, not 226 unique semantic tools or eagerly inserted schemas. Disabled integrations in the screenshots include several unrelated services; disabling MCP does not prove associated skills/hooks vanish. The plugin Skills grouping “100” is not 100 installed plugins.

**Historical local follow-up** (superseded where [02](02-BASELINE.md) records a 2026-09-17 direct observation)**.** Vercel versions 0.48.0 and 0.40.0 exposed 33/25 skills; 25 shared names, 18 identical bodies; each registered three startup commands plus one end command. Select a maintained package only after unique behavior/auth checks; don't delete caches. Prior global filesystem and Cline bindings targeted one project instead of the selected workspace. Prior Codex default was Astra/ultra and role models inherited; these are configuration observations, not proof of billed costs or current account access. A credential argument was inadvertently emitted during the earlier audit; no secret is reproduced here. Credential remediation remains a separately authorized action; this pack does not claim rotation.

**Historical API prices, USD per million tokens, not subscription charges.**

| Direct route/model | Input | Cached input | Output |
|---|---:|---:|---:|
| GPT-5.6 Luna | 0.20 | 0.02 | 1.20 |
| GPT-5.6 Terra | 2 | 0.20 | 12 |
| GPT-5.6 Sol | 4 | 0.40 | 20 |
| GPT-6 Astra | 10 | 1 | 50 |
| Claude Haiku 4.5 | 1 | 0.10 | 5 |
| Claude Sonnet 5 | 2 | 0.20 | 10 |
| Claude Opus 5 | 5 | 0.50 | 25 |
| Claude Fable 5.1 | 10 | 0.25 | 50 |
| Gemini 3.1 Flash-Lite text | 0.25 | 0.025 | 1.50 |
| Gemini 3.8 Flash introductory direct API | 0.75 | 0.075 | 3.75 |

Earlier Cursor Composer 2.5 listing: input 0.50, cached input 0.20, output 2.50; separate Cursor/other-model pools were documented. Fast modes can change rates. Google's introductory Gemini 3.8 period was stated through 2026-12-31, followed by 1.50/0.15/7.50; Cursor listed different output pricing and Zen listed non-introductory pricing. Use the actual route/dashboard, never silently substitute vendor direct rates. Cache writes/storage, grounding/tools, batch/fast modes, long-context tiers, tokenization and thinking output can change total cost. Free-endpoint retention/availability differs; do not assume consumer-free and API-free terms match. Primary refresh sources: E31/E35/E37/E38 and [Cursor pricing](https://cursor.com/docs/models-and-pricing).

**Historical full-system benchmark, AA v1.5 rounded chart labels.**

| Harness/model/settings | Index | Mean API USD/task | Mean active minutes/task |
|---|---:|---:|---:|
| Claude Code/Fable 5.1 max, with fallback | 62 | 12.40 | 34.8 |
| Codex/Astra max | 62 | 7.47 | 29.4 |
| Claude Code/Opus 5 max | 60 | 10.80 | 41.9 |
| OpenCode/GLM 5.3 | 54 | 4.24 | 48.1 |
| Antigravity SDK/Gemini 3.8 Flash high | 42 | 2.47 | 11.7 |

Original observation was visual; downloadable data required paid access and was not extracted. Index composition then equally weighted DeepSWE 1.1 (113 tasks), Terminal-Bench 4.0 (66) and SWE-Atlas-QnA (124), averaging three attempts into pass@1. Costs excluded infrastructure/engineering/human supervision; settings/harness differ. Rankings and indices cannot establish pure-model strengths or a required provider sequence. See E40. Earlier Google TB2.1 versus TB4 rankings changed substantially and mixed source provenance; TB4 resource/setting changes also confound simple price-per-token claims. Retain those methodological cautions instead of making them deployment defaults; refresh through E37/E41.

**Coverage and implementation owner.**

| Theme | Authoritative chapter |
|---|---|
| Goal, epistemology, capability/discovery/execution, scope, authorization | [01](01-CONTRACT.md) |
| Active directories, inheritance/loading graph, corpus evidence, baseline | [02](02-BASELINE.md) |
| Read-all/reread removal, fifteen-rule dispositions, validator coupling, canary | [03](03-LOADING-EXPERIMENT.md) |
| Rules/skills/plugins/MCP/hooks/commands/subagents/memory/output/indexing | [04](04-CAPABILITY-SURFACES.md) |
| Provider plans/routes/adapters, task workflows, single entry, multiple repos | [05](05-ROUTING-AND-AUTOMATION.md) |
| Metrics, confounders, negative tests, onboarding, rollback, promotion | [06](06-EVALUATION-AND-RECOVERY.md) |
| Provider-neutral proposal revision, future task contracts, source integrity, evidence gaps | [07](07-REVIEW-AND-CONTRACTS.md) |
| Practitioner repositories, current-documentation lookup, empirical limits | [08](08-EVIDENCE.md) |
| Generic screenshot observations, historical prices/benchmarks, research provenance | This chapter |
| Proposal revisions versus applied changes, disagreements with v1.1 | [10](10-CHANGE-LOG.md) |
| Paths, versions, diff, validation outcomes, measured vs estimated, rollback | [11](11-IMPLEMENTATION-RECEIPT.md) |
| Prioritized remaining work with acceptance criteria | [12](12-REMAINING-WORK.md) |
| Second-pass instructions for Cursor | [CURSOR-IMPLEMENTATION-PROMPT](CURSOR-IMPLEMENTATION-PROMPT.md) |
| Copy-paste GPT review of both passes (v1.4 pack) | [GPT-REVIEW-PROMPT](GPT-REVIEW-PROMPT.md) |

**Explicitly deferred until earned:** hardcoded provider ladders; new subscriptions/APIs; custom tool gateways; vector/global-memory databases; messaging/scheduling frameworks; automatic cross-repo edits; wholesale plugin removal; blanket permission changes; generated universal application summaries. A future phase may adopt a component when evidence and authorization justify it. Defer does not mean the capability should be discarded.
