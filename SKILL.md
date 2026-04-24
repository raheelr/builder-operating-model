---
name: builder
description: "Bootstrap and operate any software project with the Builder Operating Model — a structured agent-orchestration methodology with canonical modes, module-scoped planning, and human-in-the-loop coordination. Use /builder init to set up a new project from scratch, /builder init --from-scout to bootstrap from Scout Team discovery artifacts, /builder upgrade to bring an existing in-flight project up to the latest operating model, or /builder <mode> to run a builder session (advance, status, triage, planning, review, delta, retrospective)."
---

# Builder Operating Model Skill

## Overview

The Builder Operating Model is a structured approach to running software projects with AI agents. Proven on the Criterion Clinical Intelligence Platform, generalized for any project.

**Core idea:** A human builder (you) orchestrates specialized subagents through explicit modes, shared state docs, and a disciplined IDEAS → ROADMAP gate. The system is smart enough to derive the right modules, agents, and roadmap from the project's actual needs — you bring the vision, the operating model brings the structure.

**What it provides:**
- **Self-configuring agent model** — Claude reads your codebase and intent, then creates the right subagents for the right modules
- **Seven builder modes** — canonical session types with explicit contracts (`advance`, `status`, `triage`, `planning`, `review`, `delta`, `retrospective`)
- **Five-activity planning sessions** — structured backlog grooming for any module
- **Shared state coordination** — through docs (ARCHITECTURE, ROADMAP, IDEAS, CURRENT_STATE)
- **Parallel execution** — via git worktrees with conflict prevention
- **IDEAS gate** — all new features pass through IDEAS.md evaluation before entering the roadmap
- **Scout Team bridge** — seamless handoff from consulting discovery to prototype development

## Commands

### Bootstrap a project

```
/builder init
```

Interactive bootstrap for a brand-new project or an existing codebase that needs structure. Init starts by asking how the builder wants to begin:

**"How would you like to start?"**
1. **I know what I'm building** — fast path: capture intent, derive structure, scaffold
2. **I have a problem space — let's reason through it first** — deep path: structured reasoning → decisions → scaffold

#### Fast path (I know what I'm building)

For builders with clarity on what they want. The bootstrapper will:

1. **Read any existing code** — scan the project structure, languages, frameworks, patterns
2. **Understand intent** — ask what's being built, who it's for, what the stack is, what exists
3. **Derive canonical modules** — propose named scopes of the project's surface area from code + intent
4. **Derive subagents** — group modules by natural ownership boundaries, create `.claude/agents/<name>.md` for each
5. **Derive initial roadmap** — propose 3-5 phases; Phase 1 is always "prove the core loop once"
6. **Generate full scaffold** — write `docs/ARCHITECTURE.md`, `ROADMAP.md`, `IDEAS.md`, `CURRENT_STATE.md`, `CLAUDE.md`
7. **Confirm with builder** — present everything for review; builder adjusts before committing

#### Deep path (let's reason first)

For builders who have a problem space but haven't yet decided what to build, what approach to take, or what the scope should be. The reasoning is the work — the scaffold is a byproduct. Six phases:

1. **Problem framing** — What's the problem? Who experiences it? What happens without a solution? What does success look like in 6 months? Claude doesn't just capture answers — it probes, challenges assumptions, and surfaces implications.
2. **Constraints & unknowns** — Budget, timeline, team size, compliance requirements, biggest risks. What do you know vs. what are you guessing? Claude pushes on the unknowns — which ones matter most? Which need to be resolved before building?
3. **Requirements reasoning** — Claude reasons WITH the builder, not just records. "You said multi-tenancy — let me think about what that implies for the data model, auth, deployment, and compliance." Edge cases are explored. Dependencies between requirements are surfaced. Must-haves are separated from nice-to-haves with explicit rationale.
4. **Approach exploration** — 2-3 possible technical approaches with trade-offs. Claude presents each with pros, cons, risks, and a recommendation with reasoning. Not "what's your tech stack?" but "given these constraints, here's why approach A fits better than B."
5. **Decisions** — The builder decides. Tech stack, scope for v1, what's deferred. Each decision is captured as the project's first ADRs — not just what was decided, but the full reasoning that led there.
6. **Scaffold** — Same output as fast path, but the generated docs carry the full reasoning context. ARCHITECTURE.md includes a "Context & Reasoning" section capturing the problem understanding. The first 2-3 ADRs already exist in `docs/decisions/`. The roadmap is grounded in explored trade-offs, not guesses.

**The deep path typically takes 1-2 hours.** The result is not just a scaffold — it's a project whose architectural DNA is grounded in structured reasoning about the actual problem. Every agent reads this context at session start. Every decision can be traced back to the reasoning that produced it.

**Output:**
```
<project>/
  CLAUDE.md                          ← auto-loaded every session
  docs/
    ARCHITECTURE.md                  ← principles, agent model, canonical modules, builder modes
    ROADMAP.md                       ← phased delivery plan with interlock deliverables
    IDEAS.md                         ← idea backlog with evaluation gates
    CURRENT_STATE.md                 ← honest state of what works right now
  .claude/
    agents/
      <agent-1>.md                   ← subagent per ownership boundary
      <agent-2>.md
      ...
```

### Bootstrap from Scout Team discovery (Ask 2 — consulting → engineering bridge)

```
/builder init --from-scout <path-to-scout_team>
```

Bootstrap from a completed Scout Team engagement. Reads the Evidence Graph (`<path>/graph/<latest>/`) and handoff reports (`<path>/reports/<latest>/`), then translates discovery artifacts into a development plan.

**Translation rules (see `translation.md` for full detail):**

| Scout Entity | Prototype Component | Default Agent |
|---|---|---|
| Workflow (ENT-WF) | Frontend flow / user journey | frontend-engineer |
| Workflow Step (ENT-WS) | Screen state or API endpoint | frontend / backend |
| Decision (ENT-DEC) | Business logic module | backend-engineer |
| Rule (ENT-RUL) | Business rule in rules engine | backend-engineer |
| Exception (ENT-EXC) | Error handler / edge case flow | backend-engineer |
| System (ENT-SYS) | Integration adapter / API client | integration-engineer |
| Actor (ENT-ACT) | User role / auth scope | frontend-engineer |
| Handoff (ENT-HND) | Inter-system bridge | integration-engineer |
| Boundary attrs | Automation tier config | backend-engineer |

**Priority-driven phasing (default):**

| Phase | Scope | Source from graph |
|---|---|---|
| 1 — Prove the loop | Core workflow + highest-priority straight-through decisions | Top 20% priority_score, target_mode=straight_through |
| 2 — Assisted flows | Human-in-the-loop decisions, medium-priority rules | Next 30%, target_mode=assist |
| 3 — Full coverage | Manual decisions, exceptions, edge cases | Remaining, target_mode=human_required |
| 4 — Integration | External system integrations, legacy replacement | ENT-SYS with replaces_candidate=true |
| 5 — Hardening | Tribal knowledge validation, contradiction resolution | TRIBAL/CONFLICT confidence items |

**The bridge also carries forward:**
- **Contradictions** → become `IDEAS.md` entries flagged for resolution during build
- **Tribal knowledge** → flagged as high-risk areas needing SME validation before implementation
- **Low-confidence items** → sequenced later, with explicit "validate first" gates
- **Priority scores** → drive task ordering within each phase
- **Dependency edges** → drive build order (decisions before rules, workflows before exceptions)

Produces the same scaffold as `init`, but pre-populated with intelligence from the discovery engagement.

### Upgrade an in-flight project

```
/builder upgrade
```

For projects that already have partial structure — some docs, some agents, in-flight work — but need the full operating model methodology. Unlike `init`, upgrade **never overwrites existing content.** It only adds what's missing.

The upgrader will:

1. **Audit existing structure** — read CLAUDE.md, docs/, .claude/agents/, git log to understand what the project already has
2. **Diff against the operating model** — compare what exists against the full reference (`operating-model.md`) and identify gaps:
   - Missing docs (no IDEAS.md? no CURRENT_STATE.md?)
   - Missing sections in existing docs (ARCHITECTURE.md exists but has no builder modes? no canonical modules?)
   - Missing agent definitions (agents exist but lack ownership boundaries or session instructions?)
   - Missing coordination patterns (no IDEAS gate? no ROADMAP interlock deliverables?)
3. **Propose additions** — present a gap report: "here's what you have, here's what the operating model adds, here's my proposed additions." Each addition is shown as a preview with the exact text that would be inserted.
4. **Confirm each addition** — the builder approves or skips each proposed change individually. Nothing is written without explicit approval.
5. **Apply approved changes** — insert new sections into existing docs, create missing docs, add missing agent definitions. Existing content is never modified — only new sections are appended or new files created.

**Key principle: upgrade is additive, never destructive.** If your ARCHITECTURE.md has a "Principles" section, upgrade won't touch it — it'll add a "Builder modes" section alongside. If your agents already have instructions, upgrade won't rewrite them — it'll add missing fields (ownership boundaries, session-start instructions) if they're absent.

**Re-runnable.** As the operating model evolves (new modes, refined planning structure, new best practices), you can re-run `/builder upgrade` in any project. It will diff again, find what's new since the last upgrade, and propose only the delta. This is how operating model improvements propagate across all your projects.

**What upgrade checks for:**

| Component | What it looks for | What it adds if missing |
|---|---|---|
| `CLAUDE.md` | Pointer to docs/, critical rules, team structure (if scout+builder) | Adds pointer + rules + team structure section |
| `docs/ARCHITECTURE.md` | Agent model, canonical modules, builder modes, planning structure, rules of engagement | Adds missing sections |
| `docs/ARCHITECTURE.md` | Builder role definition (IS/IS NOT/skills needed) | Adds "The Builder Role" section from operating-model.md |
| `docs/ARCHITECTURE.md` | Security principles section | Adds security principles from operating-model.md |
| `docs/ARCHITECTURE.md` | Code quality gates section (incl. "not vibe coding") | Adds quality gates from operating-model.md |
| `docs/ARCHITECTURE.md` | Review mode contract includes quality checks (tests, lint, secrets, security) | Updates review mode contract if it's missing quality checks |
| `docs/ARCHITECTURE.md` | "What the client sees" section (client engagements only) | Adds internal vs. client-facing delineation |
| `docs/ARCHITECTURE.md` | Agentic production architecture section (if building agentic systems) | Adds runtime agent design, deterministic conversion, cost/memory/observability sections |
| `docs/ROADMAP.md` | Phase structure, task tables, interlock deliverables, per-app feature log | Creates if missing; adds missing structural elements if exists |
| `docs/IDEAS.md` | Evaluation gate, entry template, active ideas section | Creates if missing |
| `docs/CURRENT_STATE.md` | Honest state with "what works / what's broken / what's future" | Creates if missing |
| `docs/security.md` | Auth model, data classification, encryption, API security, secrets, dependencies, compliance | Creates if missing |
| `.claude/agents/*.md` | Ownership boundaries, "does NOT own" section, session-start instructions | Adds missing sections to existing agents |
| Canonical modules | Module table with code anchors and owners | Proposes module table based on code scan + existing agents |
| Builder modes | Seven modes with contracts (review mode includes quality checks) | Adds full modes section with updated contracts |
| Planning structure | Five-activity planning session (with drift-flagging + idea-filtering) | Adds full planning subsection |
| `.claude/rules/` | File-pattern rules exist for the project's tech stack | Proposes starter rules based on detected languages/frameworks |
| `docs/decisions/` | ADR folder with template and initial decision records | Creates folder with `000-template.md` and `001-tech-stack.md` |
| Evidence-based verification | Review mode contract includes evidence requirements (test output, API response, screenshots) | Adds evidence checklist to review contract |
| Self-improvement loop | Post-session rule proposal mechanism is documented | Adds self-improvement protocol to architecture doc |
| Testing agent | Testing workflow is documented (separate agent writes + runs tests after task completion) | Adds testing agent definition or workflow section |

### Sync with scout-team (iterative delivery)

```
/builder sync <path-to-scout_team>
```

**The core iterative mechanism.** Instead of waiting for a completed scout-team handoff, sync absorbs new discovery intelligence as it arrives — after every scout-team run, every discovery session, every delta. The builder starts building from partial discovery and evolves as coverage grows.

**What sync does:**

1. **Read the latest graph snapshot** from the scout-team engagement
2. **Produce a builder briefing** — a narrative summary of what was discovered, why it matters, what edge cases surfaced, and what the builder needs to understand to make good judgment calls. The builder MUST read this before approving the delta.
3. **Diff against last sync** — compare new graph entities against `docs/.scout-sync.json` (which tracks what's already been absorbed)
4. **Classify the delta:**

| Delta type | What happened | Builder action |
|---|---|---|
| **New entities** | Scout discovered new workflows, decisions, rules, systems | Propose new ROADMAP tasks, potentially new modules |
| **Updated entities** | Scout refined an entity (more detail, corrected facts) | Flag for builder review — may need rework if already built |
| **Contradictions resolved** | Scout resolved a conflict that was blocking work | Unblock the deferred task — move from IDEAS.md to ROADMAP.md |
| **Contradictions discovered** | Scout found a new conflict | Defer affected work — create IDEAS.md entry, add gate to ROADMAP task |
| **Confidence upgraded** | LOW → MEDIUM/HIGH, or TRIBAL validated by SME | Promote deferred items into active phases |
| **New domain covered** | Scout explored a previously dark area | Propose new module + agent + Phase N tasks |
| **Entity removed / superseded** | Scout determined something was incorrect | Flag for builder — may need to revert or revise existing work |

4. **Propose updates** — present each change for builder approval (same approve/skip/modify pattern as `upgrade`)
5. **Update sync state** — write `docs/.scout-sync.json` with the new graph date and entity mapping

**Sync state file (`docs/.scout-sync.json`):**
```json
{
  "scout_path": "~/path/to/scout_team",
  "last_sync_graph_date": "2026-04-13",
  "entities_absorbed": ["ENT-WF-0042", "ENT-DEC-0099", ...],
  "contradictions_active": ["CLM-00123↔CLM-00891"],
  "tribal_gates_pending": ["ENT-RUL-0215"],
  "coverage_at_last_sync": {"enrollment": "HIGH", "claims": "DARK", "pa": "THIN"}
}
```

**Rules for sync:**
- **Never interrupts active development.** Sync only proposes ROADMAP/IDEAS changes. If an agent is mid-task in a worktree, that worktree is untouched.
- **The builder decides when to sync.** Not automated. The builder runs sync when they're ready to absorb new intelligence (typically: after a scout-team session completes, before the next `advance` session).
- **Revisions are flagged, not forced.** If scout-team updates an entity that's already been built, sync flags it as "review needed — discovery evolved since you built this." The builder decides whether rework is warranted.
- **Phase assignments respect the builder's existing roadmap.** New entities are proposed into the builder's existing phase structure, not the default priority-driven phasing from `init --from-scout`. The builder's context wins.

### Send builder feedback to scout-team

```
/builder feedback <path-to-scout_team>
```

**The reverse flow.** When the builder discovers gaps during implementation — missing rules, ambiguous exceptions, unspecified integration contracts — those gaps should feed back to the scout-team as follow-up questions for the next discovery session.

**What feedback does:**

1. **Scan the project for builder-discovered gaps:**
   - IDEAS.md entries tagged as discovery gaps
   - ROADMAP tasks marked as blocked-by-discovery
   - Implementation notes where the builder flagged "need more info from discovery"
2. **Translate to scout-team follow-up questions:**
   - Each gap becomes a question for the scout-team's `stakeholder_interview_guide`
   - Questions are formatted to match the scout-team's `ROW-IVQ` artifact row schema
   - Questions are tagged with `category: follow_up_builder_gap` and linked to the entity they affect
3. **Write to a handoff file** at `<scout_path>/builder_feedback/<date>.md` (or JSON) that the scout-team's interview guide curator can ingest on its next `follow-up-prep` run

**This creates the bidirectional loop:**
```
Scout → (graph delta) → sync → Builder → (implementation gaps) → feedback → Scout
                                                                      ↓
                                                    interview guide curator picks up gaps
                                                              ↓
                                                    next discovery session targets them
                                                              ↓
                                                    Scout → sync → gaps resolved
```

### The iterative delivery timeline

```
Day 1   Scout: full-run on day1 sources (30% coverage)
        Builder: /builder init --from-scout (partial graph)
        → Phase 1 roadmap with high-priority items from partial discovery
        → Builder starts Phase 1 immediately

Day 2   Scout: full-run on day2 sources (55% coverage)
        Builder: /builder sync
        → Delta: 50 new entities, 2 contradictions resolved
        → 12 new tasks proposed, 3 previously deferred tasks unblocked
        Builder: /builder advance (absorb + continue building)

Day 3   Scout: full-run on day3 sources (75% coverage)
        Builder: /builder sync
        → Delta: "claims" domain filled (was DARK, now MEDIUM)
        → New "Claims Processing" module proposed with 8 tasks
        Builder: /builder feedback
        → 3 gaps from implementation sent back to scout-team

Day 4   Scout: follow-up-prep (ingests builder feedback) + full-run (85%)
        Builder: /builder sync
        → Delta: 3 builder-flagged rules now discovered and confirmed
        → Blocked tasks unblocked, gaps closed

Week 3  Scout: handoff (100% coverage, all contradictions resolved)
        Builder: /builder sync (final)
        → All TRIBAL items validated, all CONFLICT items resolved
        → Full scope visible, roadmap converges
        → Product is already 60-70% built because building started Day 1
```

**The client sees working software on Day 1, not Week 4.** Each discovery session sharpens what was built before and uncovers what to build next. Discovery and development co-evolve.

### Builder session modes

Once a project is bootstrapped or upgraded, run any of the builder session modes:

```
/builder advance              # What should we ship next?
/builder status               # Where are we right now?
/builder triage               # Evaluate IDEAS.md entries against gates
/builder planning <module>    # Backlog grooming + roadmap shaping for a module
/builder review               # Review a subagent's worktree, merge or reject
/builder review (adversarial) # Adversarial review — find issues or justify zero findings
/builder delta [since-ref]    # What changed since <point>?
/builder retrospective        # What did we learn? (phase boundaries)
/builder reason <topic>       # Open-ended reasoning about anything
/builder debug <issue>        # Systematic 4-phase debugging
/builder correct-course       # Mid-build requirements revalidation
/builder help [question]      # Enterprise guidance for non-technical builders: what to do next and why
```

Each mode reads the project's `docs/ARCHITECTURE.md` for its contract and executes accordingly.

**The `reason` mode** is for open-ended thinking — product direction, technical approaches, business strategy, "should we split this service?" questions. Unlike `planning` (which is module-scoped and structured), `reason` is exploratory: brainstorm options, evaluate trade-offs, arrive at a decision. The outcome gets routed to the right place: an ADR if it's an architecture decision, IDEAS.md if it's a feature idea, architecture.md if it's a principle, or just "answered" if it was a question.

**Advanced elicitation in reason mode:** After initial reasoning, Claude offers named stress-testing methods the builder can apply to pressure-test the thinking:
- **Pre-mortem** — "Assume this decision failed. What went wrong?"
- **First Principles** — Strip away assumptions, rebuild from ground truth
- **Red Team vs. Blue Team** — One lens attacks the proposal, the other defends it
- **Inversion** — "What would guarantee failure? Now avoid those things."
- **Socratic Questioning** — Recursive "why?" until the root assumption is exposed
- **Constraint Removal** — "If budget/time/team were unlimited, what changes? What does that reveal?"

The builder picks one (or skips). Claude applies that lens to the current reasoning and surfaces what it reveals. Also available during `init` deep path, `architecture`, `security`, and `adr` discussions.

**Multi-model review:** When running `review`, a fresh independent agent reviews the worktree diff before the builder sees it. The building agent and the reviewing agent are never the same session. The review agent reads the diff, task spec, architecture constraints, and file-pattern rules, then reports findings. The builder sees findings alongside the diff.

**Two-stage review:** The review agent performs two sequential passes:
- **Pass 1: Spec compliance** — "Did you build what was asked?" Compare deliverables against task spec, verify scope boundaries, confirm approach matches architecture decisions.
- **Pass 2: Code quality** — "Is it built well?" File-pattern rules, test coverage, no hardcoded secrets, error handling, CURRENT_STATE.md updated.

Findings are reported organized by pass. A change can pass spec compliance but fail code quality (or vice versa). Both passes must clear before the builder approves.

**Checkpoint preview (review opening protocol):** Every review opens with a comprehension-ordered walkthrough before the builder sees raw diffs:
1. **Orientation** — one-line intent + scope of the change
2. **Walkthrough** — changes presented by concern (not file order) so the builder follows the logic
3. **Risk tags** — 2-5 highest-risk spots, categorized (security, correctness, performance, complexity, data integrity)
4. **Testing verification** — test results, coverage delta, edge cases exercised
5. **Builder decision** — approve, request changes, or reject

Checkpoint preview composes with multi-model, adversarial, and two-stage review — it structures the presentation, not the analysis.

**Adversarial review:** The builder can invoke adversarial review: *"Mode: review (adversarial). Branch: feat/xyz."* The reviewer is instructed to FIND issues — zero findings requires explicit justification. Recommended for security-sensitive code, business logic, auth, money, and PII. Standard review remains the default for straightforward changes.

**TDD mode (opt-in for advance):** When enabled, the spawned agent follows strict Red-Green-Refactor:
1. **Red** — write a failing test that captures the requirement, verify it fails
2. **Green** — write the minimum code to make the test pass, verify it passes
3. **Refactor** — clean up implementation and test, confirm tests still pass
4. **Commit** each cycle

Builder enables with: *"Mode: advance. TDD mode. Phase 2, task P2.3."*

Opt-in, not default. **Good for:** business logic, API endpoints, calculations, data transformations, bug fixes. **Not for:** UI/styling work, prototyping/spikes, infrastructure/config.

**Session opening protocol:** Always state the mode in the first line. Examples:
- *"Mode: advance. Phase 1, next task P1.1."*
- *"Mode: advance. TDD mode. Phase 2, task P2.3."*
- *"Mode: planning. Module: Frontend (user-facing flows)."*
- *"Mode: reason. Should we split the API into public and internal?"*
- *"Mode: delta. Since Monday's merge."*

### Systematic debugging

```
/builder debug <issue>
```

4-phase methodology for resolving bugs. No guessing, no shotgun fixes.

1. **Reproduce** — confirm the bug exists. Document exact steps, inputs, and observed behavior. If it can't be reproduced, investigate why (environment, timing, data).
2. **Investigate root cause** — trace the failure to its origin. No fix attempt until the cause is understood. Read logs, add instrumentation, follow the data path.
3. **Fix** — write a failing test that captures the bug, implement the fix, verify the test passes. The test proves the bug existed AND is resolved.
4. **Defense-in-depth** — search for the same pattern elsewhere in the codebase. If the bug was a category error (e.g., missing null check, off-by-one, race condition), check for siblings. Consider proposing a file-pattern rule to prevent recurrence.

### Mid-build course correction

```
/builder correct-course
```

When external requirements change mid-build — new stakeholder input, scope change, regulatory shift, market pivot. Different from `reshape` (which re-proposes module boundaries when understanding deepens). `correct-course` handles changes to WHAT you're building, not HOW it's organized.

5 steps:
1. **Capture the change** — what shifted? New requirement, removed requirement, changed constraint? Document the delta in the builder's words.
2. **Impact assessment** — which modules, tasks, and in-flight work are affected? What's now obsolete? What's new?
3. **Architecture revalidation** — do existing architecture decisions still hold? Flag any ADRs that need revisiting.
4. **Roadmap adjustment** — re-sequence tasks, add/remove/defer work, update phase boundaries. Present the delta for builder approval.
5. **Readiness re-check** — run the same checks as `ready-check` against the updated plan. Confirm coherence before resuming.

### Discussion commands

Commands that invoke **conversations to shape or evolve foundational docs.** Unlike modes (which are session types), discussion commands produce or update specific documents through guided dialogue — exploring trade-offs, considering alternatives, and documenting the WHY.

```
/builder architecture         # Discuss/evolve architecture principles
/builder security             # Discuss/evolve security posture
/builder adr <topic>          # Create or discuss an architectural decision
/builder design               # Discuss design system, look/feel, branding, UX patterns
/builder question <topic>     # Quick triage: is this an idea, a question, or noise?
/builder reshape              # Re-propose modules when understanding evolves
/builder system-map           # Create or update the big-picture map of all system rocks
/builder spec <rock>          # Create or update the detailed spec for one rock
```

**`architecture`** — guided conversation about principles, layers, boundaries, tech stack, patterns. Produces or updates `docs/ARCHITECTURE.md`. Use at init and whenever the architectural understanding deepens.

**`security`** — guided conversation about auth model, data classification, compliance, threat surface. Produces or updates `docs/security.md`. Use at init and before any customer-facing deployment.

**`adr <topic>`** — creates a new Architectural Decision Record through dialogue. Explores the decision space, evaluates alternatives, documents rationale. Produces `docs/decisions/NNN-<topic>.md`. Use whenever making a significant technical choice.

**`design`** — guided conversation about design system, look/feel, branding, accessibility, UX patterns. Produces or updates `docs/DESIGN_SYSTEM.md`. Use when the project has a frontend.

**`question <topic>`** — lightweight triage for thinking. "I'm considering X — is this an idea, a question, a principle, or noise?" Claude reads the project's docs, evaluates, and routes: answers the question directly, or proposes an IDEAS.md entry, or suggests an ADR, or says "this is already covered in architecture.md, section Y."

**`reshape`** — for when the foundation needs to evolve. Reads everything (architecture, roadmap, current state, code), asks the builder what's changed in their understanding, re-proposes modules based on CURRENT understanding (not the original init conversation), shows the delta, and applies approved changes. In-flight work is remapped, not deleted. Use when you've pivoted, or when deeper understanding reveals the original module decomposition was wrong.

**`system-map`** — creates or updates `docs/SYSTEM_MAP.md`, the single orientation document for the whole system. SYSTEM_MAP is the **index above all other docs** — not a roadmap, not ARCHITECTURE, not CURRENT_STATE. It answers: "what are the major pieces of this system, what state is each one in, who owns it, and which decisions govern it?" Major components are called **rocks** — named, owned, status-tracked things that may span multiple modules. Organised into layers (e.g., Product, Platform, Business, Expand). Each rock has: what it is, what's inside it, status (LIVE / PARTIAL / DESIGNED / IDEA / FUTURE), owner, governing ADRs, and active-work pointers. A **mechanical update ritual** is defined alongside the map: which events trigger updates (new ADR, rock status change, ROADMAP restructure, ownership change) so the document doesn't go stale. Sessions that reason about system scope should read SYSTEM_MAP before planning. Offer to run `system-map` after init completes and after any `adr` that changes a rock's status or scope.

**`spec <rock>`** — creates or updates a detailed specification for one rock at `docs/specs/NN-<rock-name>.md`. A rock spec is written when the rock enters active development (ROADMAP task opens), a planning session, or a queued ADR. The spec template has 11 sections: (1) Purpose, (2) Scope (in/out — every out-of-scope item points to where it IS covered), (3) Stakeholders, (4) Requirements (functional + non-functional, each tagged LIVE / PARTIAL / DESIGNED / ROADMAP / IDEA), (5) User journeys / scenarios with happy path + edge paths + failure modes, (6) Technical contract (API surface, data contracts, event contracts), (7) Dependencies (depends-on + depended-on-by + external), (8) Acceptance criteria (objective, testable — feed directly into the testing agent), (9) Forward scope (roadmapped enhancements, IDEAS candidates, identified-not-yet-captured), (10) Open questions (with owner + target date), (11) Change log. Header fields mirror SYSTEM_MAP.md — when status, owner, or governing ADRs change in the spec, they must be updated in the map in the same commit. `docs/specs/00-template.md` is the blank template; it lives in the scaffold from init.

**Advanced elicitation** is available in `reason`, `architecture`, `security`, and `adr` discussions. After reasoning, Claude offers named stress-testing methods (Pre-mortem, First Principles, Red Team vs. Blue Team, Inversion, Socratic Questioning, Constraint Removal). See the `reason` mode description above for the full list.

### Guardrail library

```
/builder guardrails connect <path-or-url>    # Connect to a shared guardrail library
/builder guardrails list                      # Show available modules
/builder guardrails inherit <module>          # Pull a module into this project
/builder guardrails contribute <rule>         # Propose a rule back to the library
```

Organizations maintain shared, stack-specific rule modules (`sitecore.md`, `dotnet-core.md`, `react-typescript.md`, etc.) in a central guardrail library. During `init` or architecture discussions, relevant modules are suggested based on the detected tech stack.

**How it works:**
- **`connect`** — registers a library path or URL in `.claude/guardrails-config.json`. Multiple libraries can be connected (org-wide, team-level, personal).
- **`list`** — shows all available modules across connected libraries, grouped by stack/category.
- **`inherit`** — copies a module into `.claude/rules/` alongside project-specific rules. Inherited rules are tagged with their source library and version so they can be updated later.
- **`contribute`** — proposes a project-discovered rule back to the source library as a PR or append. The library maintainer reviews and accepts/rejects.

**Auto-suggestion:** During `init` and `architecture` discussions, if connected libraries contain modules matching the project's detected tech stack, those modules are offered for inheritance. The builder approves or skips each.

### Implementation readiness check

```
/builder ready-check
```

Validates coherence across the project's foundational docs before building begins. Reads architecture, roadmap, tasks, security docs, file-pattern rules, and agent definitions, then checks for:
- **Architecture ↔ Roadmap alignment** — every roadmap task maps to a canonical module; no orphaned tasks
- **Agent ↔ Module coverage** — every module has an owner; no agent owns modules that don't exist
- **Security ↔ Architecture consistency** — auth model, data classification, and compliance requirements are reflected in architecture principles
- **File-pattern rules ↔ Tech stack** — rules exist for detected languages/frameworks; no stale rules for removed tech
- **IDEAS gate integrity** — no roadmap tasks that bypassed the IDEAS evaluation gate
- **Task dependency chain** — no circular dependencies; blocked tasks have valid blockers

Reports readiness as **green** (coherent, ready to build), **yellow** (minor gaps, can proceed with awareness), or **red** (significant incoherence, resolve before building). Automatically offered after `init` completes.

### Enterprise Builder Guidance

```
/builder help <question>
/builder help
```

**Who this is for:** Business leaders, domain experts, and consultants who need to build enterprise-class systems but don't come from a programming background. You understand the problem space deeply. The Builder methodology handles the structure. This command bridges the two.

**How it works:** Ask anything in plain business language — what you're trying to accomplish, where you're stuck, what you're unsure about. The response gives you decisive, enterprise-grade guidance on exactly what to do next: which command to run, why it matters, what to expect, and what the stakes are if you skip or shortcut it.

**Example questions:**
- `/builder help I need to build a system to automate our claims approval process`
- `/builder help we have a board demo next Friday — what should we be doing right now?`
- `/builder help my team discovered new requirements mid-build. How do I handle this?`
- `/builder help I want to know if the work so far is any good`
- `/builder help something broke and I don't know why`
- `/builder help we just got new HIPAA compliance requirements — what changes?`
- `/builder help I have no idea where to start`

**Every response covers:**

1. **Situation** — a plain-English reflection of what you're dealing with (confirms the right problem is being addressed — correct it if wrong)
2. **What to do next** — the specific command, what it does in business terms, no assumed technical vocabulary
3. **Why this matters for your enterprise system** — the stakes: what goes wrong at scale, under audit, or in production if this step is skipped
4. **What to expect** — what will happen, what you'll see, how long it takes
5. **Common mistakes** — what non-technical builders typically get wrong at this stage
6. **The command** — exact text to run, copy-paste ready

**Enterprise concerns are always surfaced proactively.** If you're building a system that handles real data, serves real users, or operates in a regulated industry, the help response will raise these before you ask — because non-technical builders don't know to ask about them:
- Security and data access control
- Compliance requirements (HIPAA, SOC 2, PCI — whichever apply)
- Quality gates and how you know the system actually works
- Architecture decisions that are 10× cheaper to make now than mid-build
- How to demonstrate progress to stakeholders in a way that builds trust

**`/builder help` with no argument — the enterprise journey map:**

Shows the full journey from "I have a problem to solve" to "system in production," organized by phase. For each phase: what you're doing in plain English, why it matters specifically for enterprise systems, and the command:

| Where you are | What you're doing | Command |
|---|---|---|
| Just starting | Understanding the problem with stakeholders before writing a line of code | Scout Team |
| Setting up | Defining what to build, the architecture, and the team structure | `/builder init` — **always use the deep path for enterprise** |
| Defining the foundation | Deciding security model, compliance posture, key technical choices | `/builder architecture`, `/builder security`, `/builder adr` |
| Orienting the team | Mapping out all the major pieces of the system, their status, and who owns them — so everyone knows the big picture | `/builder system-map` |
| Detailing a component | Writing a clear spec for one major component: what it does, what it doesn't, who it serves, how you know it works | `/builder spec <component>` |
| Building | Having agents do the implementation work | `/builder advance` |
| Checking work | Verifying what was built is correct and high quality | `/builder review` |
| Tracking progress | Understanding where the project stands right now | `/builder status`, `/builder delta` |
| Fixing problems | Diagnosing and resolving what broke | `/builder debug` |
| Responding to change | Adjusting when requirements shift mid-build | `/builder correct-course` |
| Closing a phase | Capturing what was learned, improving the process | `/builder retrospective` |

**The deep path is the enterprise path.** When initializing any complex system, always choose "I have a problem space — let's reason through it first." This 1-2 hour conversation produces an architecture grounded in the actual business problem. Skipping it is the single most common reason enterprise systems get rebuilt from scratch six months in.

## The Definition Path

**The path from "I have a big idea" to "this is fully understood, documented, and ready to build."**

Builder has many commands. The Definition Path tells you which ones to run, in what order, and what "done" looks like at each step before moving to the next. Without this path, builders jump from idea to code and agents have to guess. With it, every component is agreed upon before anyone starts building.

Run the Definition Path at the start of a project, at the start of a new phase, or any time a major component is about to enter development.

### The six steps

**Step 1 — Understand the problem** (`/builder init`, deep path)

A structured 1-2 hour conversation that reasons through the actual business problem before anything is designed. What's the pain? Who experiences it? What does success look like? What are the constraints? What are you guessing vs. what do you know?

*Done when:* The architecture is grounded in the real problem, not assumptions. The first ADRs exist. Everyone agrees on what's being built and why.

---

**Step 2 — Map the system** (`/builder system-map`)

Name every major component of the system. Give each one a status (not started, designed, being built, live), an owner, and a pointer to the decisions that govern it. Organise into layers. Define the mechanical rule for keeping this map current.

*Done when:* You can describe the whole system in one page. A new team member reading it knows the major pieces, what state each is in, and who to talk to about each one.

---

**Step 3 — Spec each component** (`/builder spec <component>`)

For each component entering development: write a clear spec before a line of code is written. What does it do? What does it explicitly NOT cover (and who covers that)? Who uses it? What are the requirements? What are the acceptance criteria — the objective tests that prove it works?

*Done when:* Every component planned for the next phase has a spec. Acceptance criteria are written. Open questions have owners and target dates. Nothing is ambiguous.

---

**Step 4 — Validate coherence** (`/builder ready-check`)

Verify that all the docs agree with each other. Architecture principles, roadmap tasks, specs, security requirements — do they tell a consistent story? Does every agent have clear scope? Are dependencies correctly ordered?

*Done when:* Green readiness report. No contradictions. Safe to build.

---

**Step 5 — Build** (`/builder advance`)

Agents execute against the specs. They know exactly what they're building, what "done" looks like, and what they must NOT build (out-of-scope items are in the spec). No guessing.

*Done when:* The task is complete, tests pass, CURRENT_STATE.md is updated.

---

**Step 6 — Verify against the spec** (`/builder review` + reconciliation)

Confirm that what was built matches what was agreed. The review panel checks quality. Reconciliation checks completeness — every acceptance criterion from the spec is met.

*Done when:* Reconciliation passes. All acceptance criteria verified. Code merged.

---

### The key principle

**Specs are the bridge.** Without a spec, the gap between "big idea" and "working code" is filled by agents guessing what you meant. A spec makes the agreement explicit — before anyone starts building — so that review is a verification of a shared understanding, not a negotiation after the fact.

### When to run the Definition Path

- Starting a new project → run all six steps in order
- Starting a new phase → run Steps 2-4 (re-map, re-spec any new components, re-validate)
- A new component enters development → run Steps 3-4 at minimum (spec it, then validate coherence before building)
- Something doesn't feel right mid-build → run Step 4 (`ready-check`) to surface the incoherence

### In enterprise mode

The Definition Path surfaces automatically:
- After `init` — Builder prompts: "Before we start building, let's make sure the whole system is mapped and each part is clearly defined."
- When a builder says "I want to understand this before we build it" or "walk me through what we're doing" — Builder runs the Definition Path steps in order, in plain language.
- When a component first appears in conversation — Builder offers: "Before we build [component], let's write a quick spec so the team agrees on what it does and what done looks like."

## Enterprise Builder Mode

**The purpose of this mode is not to teach someone how to use Builder. It is to help them build enterprise-class software with ease.**

A business leader, domain expert, or consultant directing a software project should not need to know what a "worktree" is, what "Mode: advance" means, or how the IDEAS gate works. They need to direct the build — deciding what gets built, approving what's ready, responding to issues — in the language they already speak.

Enterprise Builder Mode makes the methodology invisible and the system being built visible.

### Enabling enterprise builder mode

During `/builder init` or `/builder upgrade`, the bootstrapper asks: *"Who is the primary builder on this project — a developer, or a business/domain leader directing the build?"*

If business/domain leader → write `builder_mode: enterprise` to CLAUDE.md.

### Natural language input (replaces formal mode protocol)

In enterprise mode, the formal session opening protocol is replaced by conversational direction. Builder maps intent to the right mode automatically:

| When the builder says... | Builder does... |
|---|---|
| "What should we build next?" / "Keep going" | `advance` — continues building the next roadmap task |
| "How are we doing?" / "Where do we stand?" | `status` — plain-language summary of what's done, in progress, blocked |
| "Is this ready?" / "Can we ship this?" | `review` — runs the review panel, presents findings in plain language |
| "Something's broken" / "This isn't working" | `debug` — systematic diagnosis in plain language |
| "We got new requirements" / "We need to change direction" | `correct-course` — structured impact assessment |
| "What changed this week?" / "Show me what's new" | `delta` — capability changes since the specified point |
| "What did we learn from this?" | `retrospective` — lessons captured for the next phase |
| "Help me plan [area]" | `planning` — five-activity session for the named module |
| "Show me the big picture" / "What does our system actually have in it?" / "What's the status of each part?" | `system-map` — creates or updates the overview of all major components with status, owner, and decisions |
| "Walk me through [component]" / "What is [X] supposed to do exactly?" / "Spec out [component] for me" | `spec <component>` — detailed spec for one component: purpose, scope, requirements, acceptance criteria, open questions |

### Output transformation

All Builder vocabulary is translated to business language. The builder never needs to know the methodology's internal terms:

| Internal term | What the builder sees |
|---|---|
| Phase 1, task P1.3 | "Next: building the claims intake form" |
| Interlock deliverable | "The milestone that proves this phase is done" |
| Worktree | "Your team member's private workspace" |
| IDEAS gate | "We check whether this is worth building before starting" |
| ADR | "A recorded decision, with the reason why" |
| Canonical module | "A defined part of the system" |
| Subagent | "The team member responsible for [area]" |
| CURRENT_STATE.md | "What the system can do right now" |
| Rock | "A major component of the system — a named thing it does (e.g., 'Claims Approval', 'User Access')" |
| SYSTEM_MAP.md | "Your system overview — all the major components, their status, and who owns each one" |
| Rock spec | "The detailed plan for one component — what it does, what it doesn't, how you know when it's done" |

### Signal-first output (always active in enterprise mode)

Every response opens with a **Signal** section — 3 bullets max, written for a business audience, before any detail:

```
## Your system, right now
- ✓ Claims intake is working and tested end-to-end
- 🔨 The approval workflow is being built (est. 2 hours remaining)
- ❓ Your decision needed: should retroactive enrollments from 2024 follow the new rule?
```

The builder asks "tell me more about [item]" to get detail on anything. Nothing is hidden — it's just not shown by default.

### Review output in enterprise mode

The builder never sees raw code. Review output is:
1. **"Here's what we built"** — plain-English description of what changed and why
2. **"Here's what we verified"** — what the review panel checked, in plain language
3. **"Here's what we found"** — issues described in terms of business impact ("this could let unauthorized users access patient records") not technical mechanics ("missing tenant_id scope check")
4. **"Your decision"** — approve, ask for changes, or flag for discussion

## Routing guide for the main Claude

**Universal output format (applies across all modes):**

Every Builder response follows this structure regardless of mode or audience:
1. **Signal** — 3 bullets max, plain language, what matters right now and what needs a decision. Always first, before any detail.
2. **Detail** — the full reasoning, findings, or output. Follows the signal.
3. **Proactive next step guidance** — closes every response. Non-negotiable. The builder should never have to ask "what do I do now?" — Builder tells them unprompted, every time.

In enterprise builder mode (`builder_mode: enterprise` in CLAUDE.md), the Signal uses business language, detail is collapsed by default, and the builder asks "tell me more about X" to expand anything.

**Proactive next step guidance — mandatory after every mode:**

After EVERY mode response completes — advance, review, status, planning, triage, debug, correct-course, architecture, security, adr, design, sync, feedback, ready-check, delta, retrospective, and all discussion commands — append a "What's next?" closing section. Never omit this. Never replace it with a generic summary.

**Format in technical mode:**
```
---
**What's next?**
- **[Most logical next step]** (`/builder [command]`) — [one-line reason specific to what just happened]
- **[Second option if genuinely useful]** (`/builder [command]`) — [one-line reason]

Or ask me anything about what we just did or what to do next.
```

**Format in enterprise builder mode** (drop all command syntax — builder speaks, Builder acts):
```
---
**What's next for your system?**
- **[Plain-language action]** — [why it matters for the system right now]. Say "[natural phrase]" and I'll do it.
- **[Second option]** — [why]. Say "[natural phrase]" to continue.

Or ask me anything.
```

**Rules:**
- Maximum 3 suggestions. The first is always the single most logical next step given what just happened.
- Every suggestion is immediately actionable: the builder responds with "yes," "let's do that," or the natural phrase shown, and Builder executes without re-explaining.
- Suggestions are specific to what just happened and the current project state — never generic ("you can run any mode").
- If the builder asks a follow-up question in response to the "What's next?" section, answer it AND repeat the next step suggestions so they can still act on them.

**Context-aware suggestion logic (what to suggest after each mode):**

| Mode just completed | First suggestion | Additional options |
|---|---|---|
| `init` | `system-map` — map out all the major components of what you're building, their status, and who owns them. The orientation document before everything else. | `security`, `architecture`, `ready-check` |
| `upgrade` | `ready-check` — verify everything is coherent before starting | `advance` |
| `advance` (task complete, not yet reviewed) | `review` — verify with the three-model panel before accepting | — |
| `advance` (task complete, already reviewed) | `advance` — next task | `status` if phase milestone reached |
| `review` (approved, merge done) | `advance` — continue with next task | `status` if phase milestone reached |
| `review` (changes requested) | Wait for agent fix, then `review` again | — |
| `status` (on track, no blockers) | `advance` — keep building | `planning` if a module needs shaping |
| `status` (blocked tasks present) | `debug` if it's a technical problem; `correct-course` if requirements shifted | — |
| `planning` | `spec <component>` if the component being planned doesn't have a spec yet — write the detailed spec while context is freshest; otherwise `advance` — execute the plan just shaped | `triage` if new ideas surfaced; `system-map` if the component's status changed |
| `system-map` | `spec <component>` — pick the most important DESIGNED or IN DEVELOPMENT component and write its spec | `advance` — start building what was just mapped |
| `triage` (ideas promoted to roadmap) | `advance` — build what was just approved | `planning` to sequence newly promoted items |
| `debug` (fix confirmed) | `review` — validate the fix with the panel before accepting | `advance` |
| `correct-course` | `ready-check` — verify coherence after the adjustment | `advance` once green |
| `architecture` | `security` (related decision area) or `adr` (capture what was decided) | `ready-check` |
| `security` | `ready-check` (verify compliance is wired into the architecture) | `adr` if a compliance decision was made |
| `adr` | `architecture` if the decision changes a principle; `system-map` if the decision changes a component's status or scope; otherwise `advance` — AND always: "Update CLAUDE.md to add this ADR to the check-first list: ADR-NNN (<one-line summary>)" | — |
| `delta` | `status` for full picture; `advance` to continue building | — |
| `retrospective` | `planning` — apply what was learned to the next phase | `advance` |
| `sync` (new intelligence absorbed) | `advance` — continue building with updated knowledge | `feedback` if implementation gaps were found |
| `feedback` (gaps sent to discovery) | `advance` — continue building while discovery catches up | — |
| `ready-check` (green) | `advance` — everything is coherent, start building | — |
| `ready-check` (yellow or red) | `architecture` or `correct-course` to resolve the gaps found | — |

When the user invokes this skill:

1. **For `init`:** Spawn the `project-bootstrapper` agent via the Agent tool. Pass the mode (scratch or from-scout) and any path argument. The bootstrapper will ask the builder which path they want (fast or deep reasoning).
   **For `init --from-scout`:** Spawn the `project-bootstrapper` agent with mode=from-scout and the path argument.

2. **For `upgrade`:** Spawn the `project-bootstrapper` agent with mode=upgrade.

3. **For `sync`:** Spawn the `project-bootstrapper` agent with mode=sync and the scout_path argument.

4. **For `feedback`:** Spawn the `project-bootstrapper` agent with mode=feedback and the scout_path argument.

5. **For `reshape`:** Spawn the `project-bootstrapper` agent with mode=reshape.

6. **For session modes (`advance`, `status`, `reason`, etc.):** Do NOT spawn a subagent — you (the main Claude) ARE the builder. Read the project's `docs/ARCHITECTURE.md` for the mode's contract, then execute it directly in the main conversation. **For `advance` with TDD mode:** instruct the spawned agent to follow the Red-Green-Refactor cycle — write failing test, minimum code to pass, refactor, commit each cycle.

7. **For `planning <module>`:** Read the canonical modules list from `docs/ARCHITECTURE.md`, confirm the module name matches, then execute the five-activity planning session structure directly.

8. **For discussion commands (`architecture`, `security`, `adr`, `design`, `question`):** Do NOT spawn a subagent. Read the relevant project doc (architecture.md, security.md, etc.), then have the guided conversation directly. The conversation produces or updates the doc. **Advanced elicitation** (stress-testing methods) is part of `reason`, `architecture`, `security`, and `adr` — offer the named methods after initial reasoning.

9. **For `ready-check`:** Execute directly in the main conversation. Read all project docs (architecture, roadmap, tasks, security, file-pattern rules, agent definitions), validate coherence across them, and report green/yellow/red readiness. Automatically offer this after `init` completes.

10. **For `debug`:** Execute directly in the main conversation. Follow the 4-phase methodology: reproduce the bug, investigate root cause (no fix until cause is understood), write failing test + fix, then check for the same pattern elsewhere and consider a guardrail rule.

11. **For `correct-course`:** Execute directly in the main conversation. Read all project docs (architecture, roadmap, current state, IDEAS, security), capture the requirement change from the builder, assess impact across modules, revalidate architecture decisions, adjust the roadmap, then re-run readiness check.

12. **For `guardrails connect/list/inherit/contribute`:** Execute directly in the main conversation. `connect` registers a library path/URL. `list` reads all connected libraries and displays available modules. `inherit` copies a module into `.claude/rules/`. `contribute` formats a rule proposal for the source library. During `init` and `architecture`, auto-suggest relevant modules from connected libraries based on detected tech stack.

13. **For reconciliation:** Automatically run after phase completion (all tasks in a phase marked done), before the builder runs milestone `review` or `retrospective`. Can also be invoked manually during `advance`. Reads the phase spec and acceptance criteria, compares against delivered code and tests, and outputs the completeness report. Execute directly in the main conversation.

14. **For `review` (including adversarial and multi-model):** First enforce the **build-verify gate** — run tests before reviewing the diff. If tests fail, show failures to the builder and stop (no diff review until tests pass).

   Once tests pass, spawn the **review panel** — composition scales with the task's risk tier:

   **Standard risk — one reviewer:**
   - **Claude Sonnet:** spec compliance + code quality. Balanced, catches structural and quality issues efficiently.

   **High-scrutiny risk — three reviewers in parallel:**
   - **Claude Opus** (deep correctness): Business logic, edge cases, spec fidelity. Opus's deep reasoning catches subtle violations the other models miss.
   - **Claude Sonnet** (architecture + quality): Code structure, test coverage, file-pattern rule compliance, CURRENT_STATE.md updated, no hardcoded secrets.
   - **Claude Haiku** (security scan): Injection risks, exposed credentials, auth gaps, known anti-patterns. Haiku's speed and pattern-matching make it ideal for this focused, high-signal check.

   **Adversarial flag** (any risk tier) — add hostile lens to all spawned reviewers: "Find issues. Zero findings requires explicit justification — re-examine or explain why this code is genuinely flawless."

   **Combining findings:** Organize by reviewer tier (Opus/correctness → Sonnet/quality → Haiku/security) before presenting to the builder. A change must clear all active tiers before the builder approves.

   **In enterprise builder mode:** Translate all findings into business impact language — "The security reviewer found that a user could access another company's data" not "Missing tenant_id scope in query." The builder approves or rejects based on business impact, not technical mechanics.

15. **For `help` (with or without a question):** Execute directly in the main conversation. Do NOT spawn a subagent. This is the enterprise guidance mode for non-technical builders — the most important entry point for someone who knows the business problem but doesn't know programming.

   **Before responding:** Check whether the project has a scaffold — does `docs/ARCHITECTURE.md` or `docs/ROADMAP.md` exist? If yes, read both before answering. Your guidance must be specific to their current project state, not generic. If no scaffold exists, treat them as Day 0 and guide toward init.

   **Response structure — every help answer must cover all six:**
   1. **Situation** — reflect back what they're dealing with in plain business language (1-2 sentences). If you might be misreading the situation, say so explicitly — let them correct you before you give direction.
   2. **What to do next** — the specific command(s) in business terms. No technical vocabulary without a plain-English explanation the first time it appears. If multiple steps are needed, sequence them explicitly: "first do X, then Y, then Z."
   3. **Why this matters for an enterprise system** — the stakes at scale, under compliance audit, or in production. What fails if this step is skipped or done poorly?
   4. **What to expect** — what happens, what they'll see, how long it takes. Remove uncertainty so they're not surprised.
   5. **Common mistakes at this stage** — what non-technical builders typically get wrong here. Be specific.
   6. **The command** — exact invocation, copy-paste ready, with a real example filled in for their specific situation.

   **The Definition Path — always surface when the builder is starting something new:**

   When a builder asks how to start, what to do first, or expresses uncertainty about a new component, present the Definition Path as the answer — not a list of commands, but a clear journey:

   > *"Before we build anything, there are six steps to make sure we understand it well enough to build it right. I'll walk you through each one. The first is understanding the problem deeply — not just what to build, but why, for whom, and what success actually looks like. This takes 1-2 hours and prevents months of rework. Ready to start?"*

   In technical mode, reference it as "The Definition Path" with the six steps. In enterprise mode, present it as "making sure we understand it before we build it" with plain-language steps.

   **Enterprise defaults — always surface proactively (even if not asked):**
   - Any system handling real user or organizational data → raise security, data classification, and access control
   - Regulated industry (healthcare, finance, legal, government) → raise compliance requirements (HIPAA, SOC 2, PCI, FedRAMP, etc.) before any building begins; these cannot be retrofitted cheaply
   - Reviewing completed work → confirm that tests and quality gates are part of the expectation, not optional
   - Early stages (no advance yet) → strongly recommend the deep reasoning path; frame it as: "the 2 hours you spend now prevents the 3-month rebuild later"
   - Skipping architecture discussions → flag explicitly: architecture changes mid-build cost 10× more in time, rework, and stakeholder confidence than decisions made upfront
   - Any agentic/AI component in the system → raise cost management, observability, hallucination risk, and deterministic conversion strategy
   - System has multiple named components or the builder mentions "modules", "parts", "areas", or separate functional areas → proactively suggest `system-map`: "It sounds like your system has several major components. I'd recommend mapping them out first — who owns each one, what state each is in, which decisions govern it. This keeps the whole team oriented and prevents different parts of the system drifting out of sync."
   - A component is entering active development for the first time or a planning session was just run for it → suggest `spec <component>`: "Before we start building [component], it's worth spending 15 minutes writing a clear spec — what it does, what it doesn't cover, how you'll know it's done. This becomes the acceptance criteria for the team."

   **If no argument provided:** First check for a project scaffold (`docs/ARCHITECTURE.md` or `docs/ROADMAP.md`).

   **No scaffold (Day 0 — no project yet):** Present the full capability landscape, organized by when in a project you'd need each thing. Cover EVERY capability — not a summary table. Structure:

   > *"Builder handles the full journey of building enterprise software — from understanding the business problem to shipping a production system. Here's everything it can do, organized by when you'll need it."*

   Then cover all capability groups in order:

   **The most important thing to understand first: The Definition Path**

   Builder has many commands, but they follow a single path from "big idea" to "ready to build." Every enterprise project should follow this before any agent writes a line of code:

   1. **Understand the problem** — 1-2 hours reasoning through what you're building and why. Prevents months of rework.
   2. **Map the system** — name every major component, its status, its owner. One page that orients the whole team.
   3. **Spec each component** — before building anything, write what it does, what it doesn't, and how you'll know it's done.
   4. **Validate coherence** — make sure everything agrees before building starts.
   5. **Build** — agents execute against clear specs, no guessing.
   6. **Verify against the spec** — confirm what was built matches what was agreed.

   Say "walk me through the Definition Path" and I'll guide you through each step.

   ---

   **Before you start building**
   - Discovery with stakeholders (Scout Team) — maps the business process in detail before writing any code. Finds rules, decisions, exceptions, edge cases. The most common reason enterprise systems fail is that the business wasn't understood deeply enough. This prevents that.
   - Set up your project (`/builder init`) — two paths: fast (if you know exactly what you're building) or deep (recommended for enterprise — 1-2 hours of structured reasoning that produces an architecture grounded in your actual business problem, not guesses).
   - Bring an existing project into the methodology (`/builder upgrade`) — adds full structure to a project that already exists.

   **Defining your foundation (before anyone writes code)**
   - Architecture (`/builder architecture`) — how the system is structured: what pieces exist, how they connect, how data flows. Decisions made here are 10× cheaper than changes mid-build.
   - Security (`/builder security`) — who accesses what, how data is protected, what compliance regulations apply. Enterprise systems get audited. Security designed upfront costs hours. Security retrofitted costs months.
   - Key decisions (`/builder adr`) — records significant technical choices with full reasoning. When the team changes or memory fades, these records explain why.
   - System overview (`/builder system-map`) — maps all the major components of the system: what each one does, what state it's in, who owns it, which decisions govern it. Keeps the whole team oriented as the system grows. **Run this right after init and update it whenever a component's status changes.**
   - Component spec (`/builder spec <component>`) — writes the detailed plan for one major component before building it: what it does, what it explicitly doesn't cover, who it serves, the requirements, and how you'll know it's working correctly. The acceptance criteria feed directly into quality checks. **Run this before starting any significant component.**
   - Design system (`/builder design`) — look, feel, UX patterns, accessibility. For projects with a user interface.
   - Readiness check (`/builder ready-check`) — verifies everything is coherent before building begins. Catches misalignments before they cost time.

   **Building day-to-day**
   - Build the next thing (`/builder advance`) — directs the team to build the next item on the roadmap. The most-used command during active development.
   - Plan a part of the system (`/builder planning [area]`) — shapes the roadmap for a specific area: which features, in what order, why. Run this before starting a new module.
   - Evaluate new feature ideas (`/builder triage`) — decides which new ideas are worth building. Prevents scope creep before it happens.
   - Absorb new discovery (`/builder sync`) — when your discovery team learns more about the business, sync pulls that new information into the build plan. Keeps building and discovery in step.
   - Send questions back to discovery (`/builder feedback`) — when builders hit gaps (missing rules, unclear decisions), this sends structured questions back to the discovery team for the next session.

   **Checking and approving work**
   - Review and approve (`/builder review`) — runs a three-model review panel (Opus checks correctness, Sonnet checks quality, Haiku checks security) before any code is accepted. Nothing goes into the system without your approval.
   - Adversarial review (`/builder review (adversarial)`) — for high-stakes code (security, payments, patient data, compliance-critical logic). Reviewers are instructed to find problems, not assume correctness. Recommended for anything with regulatory implications.

   **Staying oriented**
   - Where things stand (`/builder status`) — what's working, what's being built, what's blocked. Right now.
   - What changed (`/builder delta`) — what's new since a specific point. Useful for weekly updates, board reports, stakeholder demos, and catching up after time away.

   **When things change or go wrong**
   - Fix what broke (`/builder debug`) — systematic four-step diagnosis: reproduce the problem, find the root cause, fix it properly, confirm it stays fixed. No guessing.
   - New requirements mid-build (`/builder correct-course`) — when the business changes direction. Structured impact assessment: what changes, what stays, what needs rework.
   - Think through a hard question (`/builder reason`) — open-ended reasoning: "Should we split this into two systems?" "Is this architecture decision right for our scale?" Produces a structured answer, not a guess. Can stress-test decisions with named methods (pre-mortem, first principles, red team, inversion).
   - Quick triage (`/builder question`) — "Is this an idea, a decision, a question, or noise?" Routes thinking to the right place without requiring a full planning session.
   - Reshape the plan (`/builder reshape`) — when your understanding of the problem has changed enough that the original structure needs rethinking. Reads everything and re-proposes, preserving what's been built.

   **Shared guardrails across all projects**
   - Connect to organization's shared rules (`/builder guardrails connect`) — links to a shared library of coding standards for your technology stack. Projects inherit battle-tested rules instead of starting from scratch.
   - See available rules (`/builder guardrails list`) — shows what's available in connected libraries.
   - Pull rules into this project (`/builder guardrails inherit`) — brings a rule module into the project.
   - Contribute a new rule (`/builder guardrails contribute`) — when a project discovers a useful rule, proposes it back to the shared library so all future projects benefit.

   **Closing phases and learning**
   - Retrospective (`/builder retrospective`) — at the end of each phase, captures what worked, what didn't, what to change. The system learns from each engagement and gets better over time.

   End with: *"Tell me what you're building and I'll guide you to the right starting point: `/builder help I need to build [describe your system]`"*

   **Scaffold exists (mid-project):** Read `docs/ARCHITECTURE.md` and `docs/ROADMAP.md`. Then surface capabilities contextual to where THIS PROJECT is right now — not a generic list. Example: if Phase 1 is 70% complete with two tasks in flight, surface: advance (next task), review (for the in-flight tasks), status, and correct-course. Also surface any capabilities the project hasn't used yet that are relevant to the current phase. Always end with the most immediate next action for this specific project.

   **Model recommendation — always close with this:**

   At the end of every help response, recommend which Claude model to use for the work you just described. Frame it in cost/quality terms a business leader understands — not technical specs.

   | The work you're doing | Recommend | Why (in plain language) |
   |---|---|---|
   | Deep reasoning: init deep path, architecture decisions, security design, complex ADRs, hard "should we build this?" questions | **Claude Opus** | This is the highest-stakes work — decisions made here are expensive to undo. Opus thinks more deeply than the other models. The extra cost is trivial compared to the cost of a wrong architectural decision. |
   | Day-to-day building: advance, planning, review, triage, status, debug, correct-course | **Claude Sonnet** | The right balance of quality and cost for the work that fills most of a project. Good enough to catch real problems; fast and economical enough to use freely. |
   | Quick checks: security scans, simple status questions, pattern-based review passes | **Claude Haiku** | Fast and inexpensive. Best for focused, repeatable tasks where speed matters more than depth. Used automatically in the three-model review panel for security scanning. |

   **Format (at the end of every help response):**
   ```
   ---
   **Model to use for this:** [Opus / Sonnet / Haiku] — [one sentence in plain language: why this task fits this model, framed as cost vs. quality tradeoff]
   ```

   **Examples:**
   - Setting up architecture: *"Model to use for this: **Claude Opus** — architecture decisions are the most expensive to undo. Spending a little more now on deeper thinking pays back many times over."*
   - Building the next feature: *"Model to use for this: **Claude Sonnet** — this is standard build work. Sonnet gives you the quality you need at a cost that makes sense for day-to-day development."*
   - Checking on status: *"Model to use for this: **Claude Haiku** — this is a quick check, not deep analysis. Haiku is fast and inexpensive for exactly this kind of task."*
   - High-risk review (auth, payments, PII): *"Model to use for this: **Claude Opus** (or the full three-model panel) — this code touches [payments / patient data / authentication]. The three-model review runs Opus for deep correctness, Sonnet for quality, and Haiku for security. Use the full panel."*

   Never skip the model recommendation. Non-technical builders have no way to know this choice exists, but it directly affects both the quality of the output and the cost of the work.

   **Language rules (non-negotiable):**
   - No technical vocabulary without a plain-English explanation (example: "a git worktree — think of it as a private sandbox where one team member can work without affecting everyone else")
   - Frame everything in business outcomes, not software mechanics (say "so the system handles 50,000 transactions a day without slowing down" not "to ensure horizontal scalability")
   - Be decisive: "do this" not "you might consider"
   - Always answer the implicit question behind the explicit question — a non-technical builder asking "how do I check on progress?" is really asking "am I on track to deliver what I promised to stakeholders?"
   - Never assume they know what a module, worktree, ADR, or interlock deliverable is — explain on first use

## The operating model in brief

Full reference is in `operating-model.md`. The essentials:

### Agent model
**N specialized subagents + one builder (the human).** Each subagent owns 1-4 modules, has defined boundaries, and communicates only through shared state docs. The builder orchestrates through the seven modes. There is no LLM orchestrator above the specialists — the human is the builder.

### Canonical modules
Every project defines its canonical modules — coherent scopes of the project's surface area. Each module has:
- A name
- A description of its current surface
- Code anchors (paths)
- A single owner (subagent or builder)

Modules are the only valid scopes for `planning` sessions. The module list lives in `docs/ARCHITECTURE.md`.

### Planning session structure (five activities)
1. **Load module context** — read CURRENT_STATE, ROADMAP, IDEAS for the module. Flag any doc drift.
2. **Backlog grooming** — walk every task and IDEAS entry; mark drift, rewrite, re-sequence, demote.
3. **New feature and idea capture** — brainstorm, then filter: formal IDEAS entries for non-trivial ideas, parked-in-memo for minor ones.
4. **Dependency mapping** — upstream dependencies, downstream dependents, broken chains.
5. **Cross-module prioritization** — does this module's plan fit the system's overall plan, or is it only coherent in isolation?

### Shared state coordination
```
IDEAS.md → (evaluate against VISION + ARCHITECTURE) → ROADMAP.md → (execute) → CURRENT_STATE.md
```
All cross-agent communication flows through these docs. No agent reads another agent's private context.

### Rules of engagement (core set, customizable)
1. No feature work outside the roadmap. New features → IDEAS.md first.
2. No touching legacy code without explicit direction.
3. Update CURRENT_STATE.md on every capability change.
4. Respect layer/module boundaries. Cross-boundary work gets split.
5. Every task advances the core loop.
6. Confirm before destructive or shared-state actions.
7. Agents never modify global config or files outside their scope.
8. Documentation is part of the work.

### Bounded autonomy (task risk classification)

Not all tasks need the same level of oversight. Tasks are classified by risk, and the oversight model scales accordingly:

| Risk tier | Examples | Agent behavior | Builder involvement |
|---|---|---|---|
| **Auto-safe** | Docs, tests, refactors, linting fixes | Agent executes autonomously | Builder reviews later (batch) |
| **Standard** | Features, bug fixes, UI work | Agent works in worktree | Builder reviews before merge |
| **High-scrutiny** | Auth, money, PII, encryption, compliance | Agent works in worktree | Adversarial + multi-model review enforced |
| **Builder-only** | Architecture decisions, infrastructure, production config | Not delegated to agents | Builder does the work directly |

**Classification happens at task creation.** During `planning` or `advance`, each task is tagged with its risk tier. The tier can be overridden by the builder at any time.

**Defaults by module pattern:** Projects can define default risk tiers in `.claude/rules/` by file path or module. Example: anything touching `auth/`, `payments/`, or `**/middleware/encryption*` defaults to high-scrutiny. Anything in `docs/` or `tests/` defaults to auto-safe.

**Escalation:** An agent working on an auto-safe or standard task that discovers it needs to touch high-scrutiny code must stop and flag the builder. It cannot self-promote.

### Quality gates (protocol enforcement)
Four gates enforced procedurally by the main Claude session:

1. **Build-verify gate** — Tests must pass before review. If tests fail, the builder sees failures and error output — not the diff. Fix first, review second.
2. **State-doc gate** — CURRENT_STATE.md must be updated alongside code changes. A PR that changes behavior but doesn't update state docs is incomplete.
3. **Review-before-merge gate** — No auto-merge. Every change goes through review mode (standard or adversarial). The builder must explicitly approve before merge.
4. **IDEAS gate** — (existing, rule #1 above) No feature work outside the roadmap. New features enter through IDEAS.md evaluation.

Gates are enforced by the main session's routing logic, not by the subagent. A builder can override any gate with explicit justification — but the override is logged and visible in the review.

### Hooks as enforcement

Claude Code hooks (`PreToolUse`, `PostToolUse`, `Stop`) mechanically enforce gates — no relying on the agent to self-police:

| Hook | Trigger | Enforcement |
|---|---|---|
| **PreToolUse** | Before any file write | Block writes outside the agent's declared module scope. Prevents scope creep at the filesystem level. |
| **PostToolUse** | After any file write | Auto-run linter/formatter on the changed file. Catches style violations immediately, not at review. |
| **Stop** | Before agent signals completion | Block completion if `CURRENT_STATE.md` was not updated during the session. Enforces the state-doc gate mechanically. |

**Configuration:** Hooks are defined in `.claude/hooks.json` (project-level) or `~/.claude/hooks.json` (global). During `init` and `upgrade`, starter hooks are proposed based on the project's tech stack and agent model. The builder approves before they're written.

**Hooks complement gates.** Gates are procedural (the main session enforces them during routing). Hooks are mechanical (Claude Code enforces them at the tool-call level). Together, they make it structurally difficult to ship incomplete or out-of-scope work, even when the agent is running autonomously in a worktree.

### Reconciliation step

After building, before milestone review: reconciliation compares delivered code against the spec's acceptance criteria. Different from review (which checks quality) — reconciliation checks **completeness**.

**Output:** A completeness report with three columns:
- **Implemented + tested** — criteria with passing tests and working code
- **Missing** — criteria not yet addressed
- **Scope drift** — work delivered that wasn't in the spec (may be valid, but must be acknowledged)

**When it runs:** Automatically triggered after phase completion (all tasks in a phase marked done), before the builder runs `review` or `retrospective` for that phase. Can also be invoked manually: *"Mode: advance. Reconcile Phase 2."*

**Principle:** The spec is the contract. If the spec says "user can reset password via email," reconciliation checks that this works — not that the code is clean (that's review's job) or that the tests are thorough (that's the testing agent's job).

### Spec-driven independent testing

The testing agent tests against the **spec**, not the code. It does NOT read the implementation.

**How it works:**
1. Testing agent reads the task spec and acceptance criteria
2. Writes functional tests derived purely from the spec — expected inputs, expected outputs, expected behaviors
3. Runs those tests against the build
4. Flags divergence: tests that fail reveal where the build doesn't match the spec

**Principle: separate the builder from the validator.** The agent that wrote the code should never be the same agent that validates it. The testing agent has no knowledge of implementation details — it only knows what the spec promises. This catches assumption drift, where the builder unconsciously tests what they built rather than what was asked for.

**Composition with reconciliation:** Reconciliation checks "did you address every criterion?" Testing checks "does each addressed criterion actually work?" They complement each other — reconciliation catches omissions, testing catches incorrect implementations.

### Self-improvement visibility
The self-improvement loop surfaces metrics so the builder can see the system learning:

**Per-session (shown at session end):**
- Corrections count — how many times the builder corrected agent behavior this session
- Rules proposed — new file-pattern or process rules suggested based on corrections
- Categories — what types of corrections (naming, testing, architecture, scope, style)

**Per-project (shown in `status` mode and `retrospective` mode):**
- Total rules by category — how many rules exist and where they cluster
- Corrections trending — are corrections decreasing over time? (they should be)
- Most common categories — where agents still need the most guidance

This makes the guardrails' learning visible. A project with 40 rules and declining corrections has mature guardrails. A project with 5 rules and rising corrections needs more guardrails.

### Context recovery (agent checkpointing)
Agents write checkpoint files (`.claude/checkpoints/<task-id>.yaml`) at milestones — after significant progress, before risky operations, and when nearing context limits. A checkpoint captures: task ID, what's done, what's remaining, key decisions made, files touched, and current blockers. If an agent exhausts context or stalls, a new agent reads the checkpoint and resumes from where the previous agent left off. The builder doesn't need to manually re-context — the checkpoint carries the state.

### Why the builder is human
Novel architectural decisions compound. Every extra LLM hierarchy layer amplifies instruction drift. The builder's value is judgment, not coordination. The seven modes already are the orchestration logic. An LLM orchestrator adds risk without proportional value — at least until the project's workflows are well-understood and repetitive.

## File locations

| Component | Path |
|---|---|
| This file | `~/.claude/skills/builder/SKILL.md` |
| Operating model reference | `~/.claude/skills/builder/operating-model.md` |
| Scout → prototype translation rules | `~/.claude/skills/builder/translation.md` |
| Bootstrapper agent | `~/.claude/skills/builder/agents/project-bootstrapper.md` |
