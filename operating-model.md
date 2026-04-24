# Builder Operating Model — Reference

This is the generic, project-independent reference for the Builder Operating Model. When `project-bootstrapper` generates a project's `docs/ARCHITECTURE.md`, it adapts this reference to the project's specific modules, agents, and context.

## Project initiation

Every project begins with `/builder init`. The builder chooses one of two paths:

### Fast path: "I know what I'm building"
For builders with clarity. Capture intent (what, who, stack, scope), derive modules and agents, scaffold the project. Takes 15-20 minutes. The result is a well-structured scaffold ready for immediate development.

### Deep path: "Let's reason through it first"
For builders who have a problem space but not yet a solution. Six phases of structured reasoning:

1. **Problem framing** — What's the problem? Who has it? What does success look like? Claude probes and challenges — not just capturing answers, but reasoning about them.
2. **Constraints & unknowns** — Timeline, team, budget, compliance. Separate what's known from what's guessed. Flag critical assumptions.
3. **Requirements reasoning** — Claude reasons WITH the builder. "You said multi-tenancy — let me think through what that implies for data, auth, deployment, and compliance." Edge cases explored. Dependencies surfaced.
4. **Approach exploration** — 2-3 possible architectures with trade-offs, risks, and a recommendation with reasoning.
5. **Decisions** — Tech stack, v1 scope, what's deferred. Each decision captured as an ADR with full rationale.
6. **Scaffold** — Same output as fast path, but carrying the full reasoning context. ARCHITECTURE.md includes a "Context & Reasoning" section. First ADRs already exist.

**The deep path takes 1-2 hours.** The reasoning itself is the most valuable output — it produces a project whose every architectural decision can be traced back to a structured conversation about the actual problem.

**Why this matters:** The reasoning that produces the answers IS the guardrails being built. Skip it, and you're building the wrong thing faster. A scaffold without reasoning is a guess. A scaffold grounded in structured problem exploration is a foundation.

Both paths produce the same scaffold structure. The deep path produces richer docs, earlier ADRs, and a builder who deeply understands the problem before any agent writes a line of code.

## The agent model

**N specialized subagents + one builder (the human).**

More agents = more coordination overhead and more drift risk. 3-5 is enough for most projects without becoming unmanageable. Only add more when the project has genuinely non-overlapping domains that benefit from parallel execution.

### The builder

**You are the builder.** Your main Claude Code session is the builder thread. There is no separate "builder agent" — the main thread is the builder.

The builder's job:
1. Read the shared state docs at session start
2. Decide what to advance — usually a milestone from ROADMAP.md
3. Spawn specialized subagents in parallel to execute
4. Receive their reports when they complete
5. Review their changes, merge worktree branches, commit
6. Update ROADMAP.md with milestone progress
7. Triage new ideas in IDEAS.md

The builder does NOT do execution work when a specialized agent can do it. The builder orchestrates.

### Builder modes

Every builder session fits one of seven canonical modes. The mode names are a vocabulary for session intent.

| Mode | Builder's question | Contract |
|---|---|---|
| **`advance`** | What should we ship next? | Read ROADMAP current phase → pick next task → spawn owner subagent(s) in worktrees → await → review, merge, update ROADMAP + CURRENT_STATE. |
| **`status`** | Where are we right now? | Read CURRENT_STATE → scan active worktrees → summarize blockers, completions, next steps. No code changes. Reports only. |
| **`triage`** | What's in the idea backlog? | Read IDEAS.md entries → evaluate each against project vision + architecture gates → promote to ROADMAP or park/reject with reason. No code changes. |
| **`planning`** | How should we shape `<module>`'s roadmap? | Pick one canonical module. Perform the five-activity planning session (see below). Output: ROADMAP + IDEAS updates, planning memo. No code changes. No execution spawns. |
| **`review`** | Is this subagent's work ready to merge? | Read a subagent's worktree diff → verify CURRENT_STATE was updated → verify ROADMAP status matches → run quality checks (tests pass, lint clean, no hardcoded secrets, security scan if configured) → merge or reject with specific, actionable feedback. |
| **`delta`** | What changed since `<point>`? | Diff CURRENT_STATE between two git shas → summarize capability changes, removals, new blockers. |
| **`retrospective`** | What did we learn? | At phase completion → capture what worked, what didn't, what to change. Update rules only if a real principle violation was surfaced. |

**Session opening protocol.** State the mode in the first line. Include scope or target:
- *"Mode: advance. Phase 1, next task P1.1."*
- *"Mode: planning. Module: Backend API."*
- *"Mode: delta. Since last Friday's demo sha."*

**Modes are intent, not machinery.** The tools are the same across modes. The mode defines what you're trying to accomplish.

**Scripted helpers allowed; scripted decisions are not.** A helper that produces a status summary is fine. An automation that picks the next task or merges on your behalf is not.

### Planning session structure

A `planning` session on a single module has five activities, in order.

**1. Load module context.**
Read CURRENT_STATE for what this module currently does, ROADMAP for all tasks across phases, IDEAS for entries touching the module, and any module-specific docs. State the module's current status and blockers.

While loading, **flag any CURRENT_STATE drift** — descriptions that don't match actual file paths, features described as working that are broken, or capabilities missing from the doc. Log drift in the planning memo for the module owner to fix on next touch.

**2. Backlog grooming.**
Walk every open task and every relevant IDEAS entry. For each:
- Still relevant?
- Description still accurate?
- Phase assignment still right?
- Problem it solves has evolved?
- A newer idea obsoleted it?

Mark drift. Rewrite stale descriptions. Re-sequence, demote, split, merge, or delete.

**3. New feature and idea capture.**
Brainstorm what's missing. Capture as new IDEAS entries (not direct ROADMAP tasks). The IDEAS gate still applies.

**Then filter.** Separate into two tiers:
- **Formal IDEAS entries** — architecturally non-trivial ideas that affect sequencing or dependencies
- **Parked in memo** — minor polish, nice-to-haves, or ideas too speculative to evaluate yet

**4. Dependency mapping.**
For every in-flight or upcoming task:
- **Upstream dependencies** — what this module needs from other modules
- **Downstream dependents** — what other modules need from this one
- **Broken chains** — any dependency that's misaligned, missing, or implicit

**5. Cross-module prioritization.**
Reconcile this module's sequencing with modules it connects to. Watch for:
- **Starvation:** this module's plan assumes capacity from another module that can't give it
- **Blockage:** this module is implicitly blocked on unscheduled upstream work

Guiding question: *"does this module's plan fit into the system's overall plan, or is it only coherent in isolation?"*

**Session output:**
- ROADMAP updates (re-sequenced, re-scoped, promoted, or demoted tasks)
- IDEAS updates (new entries, updated entries)
- Planning memo in commit message (module, status, changes, dependencies, blockers, rationale)

### Advanced elicitation methods

When the builder is reasoning about a decision (during deep init, `/builder reason`, or `/builder architecture`), they can stress-test their thinking using named elicitation methods:

- **Pre-mortem**: "Assume this decision failed spectacularly. What went wrong?"
- **First Principles**: "Strip away assumptions. What do we actually know to be true?"
- **Red Team vs. Blue Team**: "Argue against this decision, then defend it."
- **Inversion**: "What would we do if we wanted this to fail?"
- **Socratic Questioning**: "Why? And why that? And why that?"
- **Constraint Removal**: "If we had unlimited time/budget, what would we do differently?"
- **Stakeholder Mapping**: "Who else is affected by this decision?"
- **Analogical Reasoning**: "What similar problems have been solved before?"

After initial reasoning, Claude offers: "Want to stress-test this thinking? Available methods: Pre-mortem, First Principles, Red Team, Inversion..." The builder picks one (or skips). Claude applies that specific lens to the reasoning and surfaces what it finds.

This is especially powerful during the deep init path, ADR creation, and any architecture discussion.

### Implementation readiness check

A gate between planning and building. Before Phase 1 begins (or before any new phase), the builder can run a readiness check that validates coherence across all project docs.

The check verifies:
- Architecture principles don't contradict each other
- ROADMAP tasks match the architecture's module boundaries
- Task descriptions are specific enough for agents to execute (not vague one-liners)
- Dependencies between tasks are explicit and correctly ordered
- Security requirements in security.md are reflected in relevant tasks
- No module is referenced in ROADMAP that doesn't exist in ARCHITECTURE.md
- File-pattern rules exist for the project's tech stack

The output is a readiness report: green (ready to build), yellow (minor gaps to address), or red (contradictions or missing critical information).

Command: `/builder ready-check` or automatically offered after init/upgrade completes and before first advance.

### Correct Course (Mid-Build Requirements Revalidation)

When requirements change mid-build — a stakeholder shifts priorities, a discovery session reveals new constraints, or the builder's understanding evolves — simply amending the roadmap is insufficient. The architecture may no longer be coherent with the new requirements.

`/builder correct-course` triggers a structured revalidation:

1. **Capture the change** — What shifted? New requirement, removed requirement, changed constraint, new information?
2. **Impact assessment** — Which modules, tasks, and architectural decisions are affected? Claude reads the full project state and identifies ripple effects.
3. **Architecture revalidation** — Do the architecture principles still hold? Do any ADRs need revision? Are security requirements still met?
4. **Roadmap adjustment** — Re-sequence tasks. Some may need to move phases. Some may become irrelevant. New tasks may be needed.
5. **Readiness re-check** — Run the readiness check on affected modules to verify coherence after the adjustment.

**The difference from reshape:** Reshape is about evolving module boundaries as understanding deepens. Correct-course is about responding to external changes that affect requirements. Reshape restructures the project's internal organization. Correct-course re-aligns the project with shifted external reality.

**When to use:**
- Client changes priorities or scope
- Discovery reveals a constraint that invalidates an assumption
- A technical spike proves an approach won't work
- Compliance or regulatory requirements change

### Why the builder is a human, not an LLM

1. **Novel architectural decisions compound.** An LLM making decomposition calls on novel work makes small errors that compound invisibly across phases.
2. **Every extra hierarchy layer amplifies error.** Three levels (human → orchestrator → specialist) doubles instruction-drift surface compared to two.
3. **The builder's role is judgment, not coordination.** Specialists know their boundaries. The builder's value is deciding *what matters now*.
4. **The seven modes already are the orchestration logic.** An LLM orchestrator adds nothing a disciplined human doesn't already get.

When (if) the project has well-understood, repetitive workflows, a specific workflow may warrant a scripted orchestrator. Until then, the builder is human.

## Canonical modules

Every project defines a fixed list of canonical modules — coherent scopes of the project's surface area.

**Properties of a good module:**
- Large enough to be a planning target (≥3 related features or components)
- Small enough to be internally consistent (one owner, one purpose)
- Has code anchors (files or folders you can point to)
- Has exactly one owner (a subagent or the builder)

**Module table format:**
```
| Module | Description | Code anchors | Owner |
|---|---|---|---|
| ... | ... | ... | <subagent-name> |
```

**Rules:**
1. These are the only valid scopes for a `planning` session
2. Legacy/deprecated code is not a module
3. New modules require explicit architecture doc update
4. Cross-module work is still welcome — modules scope *planning*, not *execution*

## Rocks and SYSTEM_MAP

Every project defines **rocks** — the major named pieces of the system with explicit lifecycle status. Rocks are product/system things (e.g., "Clinical Triage Engine", "Billing Module", "User Auth"). They are distinct from canonical modules: a rock may span multiple modules, and a module may contribute to multiple rocks.

`docs/SYSTEM_MAP.md` is the **index above all other docs** — not the roadmap, not ARCHITECTURE, not CURRENT_STATE. It answers: "what are the major pieces of this system, what state is each one in, who owns it, which decisions govern it?" Organise rocks into layers appropriate to the project (Product, Platform, Business, Expand, etc.).

**Rock status vocabulary:** LIVE · PARTIAL · IN DEVELOPMENT · DESIGNED · IDEA · FUTURE · CONCEPT

**Each rock entry has:** What it is · What's inside it · Status · Owned by · Governing ADRs · Active work pointers

**Mechanical update ritual** — define a trigger/action table alongside the map specifying which events require a SYSTEM_MAP update: new ADR that changes a rock's scope or status, ROADMAP restructure, ownership change, new module added, major feature goes LIVE. Staleness prevention must be non-judgement-based; the trigger table makes it automatic.

**Per-rock specs** — when a rock enters active development (ROADMAP task opens), a planning session, or a queued ADR, create a detailed spec at `docs/specs/NN-<rock>.md`. The 11-section spec template (`docs/specs/00-template.md`) covers: Purpose, Scope (in/out), Stakeholders, Requirements (FR + NFR with status tags), User journeys, Technical contract, Dependencies, Acceptance criteria (feed the testing agent), Forward scope, Open questions, Change log. Header fields mirror SYSTEM_MAP — when status or owner changes in a spec, update the map in the same commit.

**Session-start check:** when `system-map` was last updated > 2 weeks ago AND git log shows changes in that period, flag it as potentially stale before starting a planning session.

## Shared state coordination

All cross-agent communication happens through shared state docs. No agent reads another agent's private context.

**The shared state docs:**
- `docs/SYSTEM_MAP.md` — index of all rocks with status, ownership, and governing ADRs. The orientation doc above all others.
- `docs/ARCHITECTURE.md` — principles, agent model, canonical modules, builder modes.
- `docs/ROADMAP.md` — phased delivery plan with task tables and interlock deliverables.
- `docs/IDEAS.md` — idea backlog with evaluation gates.
- `docs/CURRENT_STATE.md` — honest state of what works right now.
- `docs/security.md` — auth model, data classification, compliance.
- `docs/decisions/` — Architectural Decision Records (ADRs).
- `docs/specs/` — per-rock detailed specs (one file per rock, created when a rock enters active development).

**The IDEAS flow:**
1. **Idea capture** — anyone adds an idea to IDEAS.md
2. **Idea evaluation** — builder evaluates against project vision + architecture
3. **Promotion** — approved ideas move to ROADMAP.md with phase + task ID
4. **Assignment** — builder spawns subagent(s)
5. **Execution** — agent does the work, commits to its worktree
6. **Completion** — agent updates CURRENT_STATE.md
7. **Merge** — builder reviews, merges, updates ROADMAP.md

## Parallel execution via git worktrees

When two agents work on non-overlapping areas, they run in isolated git worktrees — each gets its own copy of the repo.

Worktree location: `../<project>-worktrees/<branch-name>/`

When an agent completes work:
1. Its worktree has a clean branch with commits
2. Builder reviews the diff
3. Builder merges to main
4. Worktree is cleaned up
5. CURRENT_STATE.md is updated

Agents must NEVER force-push, rebase main, or alter history. Only the builder handles merges.

## Context recovery (agent checkpointing)

When an agent exhausts its context window or crashes mid-task, a checkpoint file lets a new agent resume exactly where the previous one left off.

**How it works:** Agents write a checkpoint file (`.claude/checkpoints/<task-id>.yaml`) after each significant milestone. The checkpoint captures: current task ID, completed steps, files created/modified, pending work, test status, and any decisions made. When the builder detects an agent has stalled or context-exhausted, they spawn a new agent that reads the checkpoint and continues from where the previous one stopped.

**Checkpoint file format:**
```yaml
task_id: P1.3
agent: backend-engineer
started_at: 2026-04-11T10:00:00
last_milestone: "Created models and migration, tests pending"
completed_steps:
  - "SQLAlchemy models for Quote, Premium"
  - "Alembic migration 003"
  - "Pydantic request/response schemas"
pending_steps:
  - "Write tests for quote calculation"
  - "Update CURRENT_STATE.md"
files_changed:
  - src/models/quote.py
  - src/schemas/quote.py
  - migrations/003_quote_tables.py
decisions_made:
  - "Premium stored as integer cents to avoid floating point"
test_status: "not yet run"
```

The checkpoint is not a full replay log — it's a concise handoff brief. A new agent reads the checkpoint, verifies the current file state, and picks up the pending steps. The builder can also use checkpoints to understand where a stalled agent got stuck.

## Rules of engagement

Every agent, including the builder, follows these rules. They are customizable per project but the defaults are:

1. **No feature work outside the roadmap.** Not in ROADMAP? Not being built. New → IDEAS.md first.
2. **No touching legacy code without direction.** Legacy code stays static unless an explicit task addresses it.
3. **Update CURRENT_STATE on every capability change.** Drift between code and the doc is a bug.
4. **Respect module boundaries.** Cross-boundary tasks get split between agents.
5. **Every task advances the core loop.** If it doesn't close the loop or tighten feedback, justify it explicitly.
6. **Confirm before destructive actions.** Force pushes, branch deletions, history rewrites all need approval.
7. **Agents never modify global config or files outside their scope.**
8. **Documentation is part of the work.** A feature not in CURRENT_STATE is not a feature.
9. **Frontend app features require builder approval.** User-facing changes need explicit roadmap entries.
10. **Check `docs/decisions/` before re-debating architecture.** If an ADR exists for the question, the decision is made — do not relitigate it without a compelling new reason. Sessions that redebate settled decisions waste time and introduce drift. If you have new evidence that warrants revisiting a decision, surface it explicitly and propose a `reason` or `adr` session rather than debating inline.

## Bounded Autonomy (Risk-Based Task Classification)

Not all tasks require the same level of human oversight. **Bounded autonomy** classifies tasks by risk and adjusts the approval requirements accordingly.

**Risk levels:**
| Level | Examples | Autonomy |
|---|---|---|
| **Auto-safe** | Documentation, test additions, refactoring, linting fixes, dependency updates | Agent executes and commits. Builder reviews at next status check. |
| **Standard** | Feature implementation matching a spec, bug fixes with tests | Agent executes in worktree. Builder reviews before merge. (Default behavior.) |
| **High-scrutiny** | Auth/security code, payment/money logic, PII handling, external API integrations | Adversarial review required. Multi-model review enforced. Builder reviews with extra attention. |
| **Builder-only** | Architecture changes, module boundary changes, dependency additions, infrastructure | Builder does this directly, not delegated to agents. |

**The builder sets the risk level** for each task (or accepts the default). Risk classification is part of the task description in ROADMAP.md. The system uses the classification to apply the appropriate review rigor automatically.

**Why bounded, not full autonomy:** Anthropic's own research shows developers can fully delegate only 0-20% of tasks. The rest requires active supervision. The winning pattern: classify by risk, auto-execute the safe stuff, focus human attention where it matters.

## When agents conflict

Two agents with claims on the same code = the task decomposition was wrong.

Resolution:
1. Builder stops the conflicting work
2. Builder re-decomposes so tasks don't overlap
3. Module boundaries are the guide
4. Worst case: serialize (one finishes, then the other starts)

Conflict is a signal the agent model needs tuning, not a normal operating condition.

## Iterative delivery with scout-team

When a project is bootstrapped from scout-team discovery (`init --from-scout`), the default assumption is **iterative co-evolution**, not waterfall handoff. Discovery and development run in parallel.

### The bidirectional loop

```
Scout Team ──(graph delta)──→ sync ──→ Builder
    ↑                                      │
    └──(follow-up questions)──← feedback ←─┘
```

**Scout → Builder (sync):** After each scout-team run, the builder runs `/builder sync` to absorb new entities, resolved contradictions, validated tribal knowledge, and coverage improvements. The builder's roadmap evolves to match discovery's growing understanding.

**Builder → Scout (feedback):** When the builder encounters gaps during implementation (missing rules, ambiguous decisions, unspecified integrations), they run `/builder feedback` to send structured follow-up questions back to the scout-team. The scout-team's interview guide curator ingests these for the next discovery session.

### Why this matters

**Waterfall cost:** If the builder waits for complete discovery, the client sees nothing for 3-4 weeks. When they finally see a prototype, course corrections are expensive because nothing was validated early.

**Iterative value:** The client sees working software on Day 1. Each discovery session sharpens what was built and uncovers what to build next. Course corrections are cheap because the scope is small at each iteration. By the time discovery is "complete," the prototype is 60-70% built.

### Handling revision risk

The iterative approach introduces a specific risk: something built based on partial discovery turns out to be wrong when fuller discovery arrives. The sync mechanism handles this explicitly:

- **Updated entities** that correspond to completed tasks are flagged as "revision needed" — not automatically reverted.
- The builder evaluates each revision flag: Is the change material? Does it affect the user experience? Does it invalidate the logic?
- Most revisions are minor refinements, not complete reworks. The cost of occasional rework is far less than the cost of waiting for complete discovery.
- **Contradictions** are the hardest case: if a contradiction touches an actively-built feature, sync proposes deferring that feature until resolution. This is a local pause, not a global stop.

### Builder briefings during sync

Sync is not just "approve entity deltas." It is the primary mechanism by which the builder stays informed about the business problem. Every sync includes a **narrative briefing** — not just counts and entity IDs, but a human-readable summary of what was discovered, why it matters, and what edge cases were surfaced.

The briefing answers three questions:
1. **What was discovered?** — plain-language summary of the session's findings
2. **What does it mean for the product?** — implications for the build, especially edge cases, exceptions, and business rules that affect design decisions
3. **What does the builder need to understand to make good sequencing calls?** — business context that affects priority, trade-offs, or risk

Without builder briefings, the sync becomes a rubber-stamp: "23 new entities, approved." That defeats the purpose. The builder who approves a delta they don't understand is not directing — they're abdicating.

**The rule:** The builder must READ the briefing before approving the delta. If the briefing surfaces an edge case that affects an in-flight task, the builder should flag it immediately — don't wait for the review mode to catch it.

### Sync cadence

The builder decides sync cadence. Common patterns:
- **After every scout-team session** — highest fidelity, most interruptions
- **At the end of each discovery day** — good balance
- **At discovery milestone boundaries** (end of Week 1, end of Week 2) — lowest interruption, highest revision risk

The right cadence depends on the engagement pace and the builder's current focus. If the builder is deep in Phase 1 core-loop work, syncing daily is productive. If the builder is in Phase 3 hardening, weekly syncs suffice.

## When to use the Builder

Not every project needs an operating model. The threshold is complexity, not ambition.

- **Simple app (1 person, 1 week, < 20 files):** Just use Claude directly. No operating model needed. You can hold the whole project in your head, and there's no coordination to manage.
- **Medium app (1-2 people, 2-4 weeks, 20-100 files):** Consider the builder model if you're losing track of what's done, what's next, or dependencies between parts. The docs alone (ROADMAP, CURRENT_STATE, IDEAS) add value even without the full agent model.
- **Complex system (2+ people, 1+ months, 100+ files, multiple functional areas):** Use the full builder model. Without it, you'll drift, forget context between sessions, and build conflicting things. The coordination cost is real, but the cost of not coordinating is higher.
- **Client engagement with discovery:** Use scout-team + builder model together. Discovery feeds the builder through sync/feedback loops. The iterative co-evolution model (see "Iterative delivery with scout-team" below) prevents waterfall delays and validates early.

If you're unsure, start with just the shared state docs (ARCHITECTURE, ROADMAP, CURRENT_STATE, IDEAS) and add agents when you feel the need for parallel execution.

## The Builder Role

### What the builder IS

The builder is:

1. **An architect who makes judgment calls** about what to build, in what order, with what constraints. The builder decides scope, sequence, and trade-offs — not the agents.
2. **A quality gate who reviews every piece of work before it merges.** No code reaches main without the builder reading the diff, verifying state docs are updated, and confirming the work matches the intent.
3. **An orchestrator who spawns agents, manages parallel work, and resolves conflicts.** The builder decides which agents work on what, detects when they're stepping on each other, and re-decomposes when conflicts arise.
4. **A domain expert (or has access to one) who can validate that the system does the right thing.** Technical correctness is necessary but not sufficient — the builder ensures the system solves the actual problem.
5. **A business-context consumer who stays informed about what scouts discover.** The builder doesn't do the discovery, but MUST understand the business problem well enough to make judgment calls about sequencing, trade-offs, and edge cases. This understanding comes from reading scout briefing memos, sync narratives, and discovery artifacts — not from personally interviewing stakeholders.
6. **A delegator of routine quality checks.** The builder can delegate repeatable validation (lint, tests, security scan, architecture compliance) to automated review agents. The builder only reviews what the automated agents flag as needing human judgment. This is not an LLM orchestrator — it's automated validation that filters noise so the builder's attention stays on decisions that matter.

### What the builder is NOT

The builder is:

1. **NOT a developer who writes code.** Agents do that. The builder's hands are on the steering wheel, not the keyboard (for implementation work).
2. **NOT a project manager who tracks hours and timelines.** The operating model tracks capability state (CURRENT_STATE), delivery plan (ROADMAP), and idea backlog (IDEAS) — not Gantt charts or burndown velocity.
3. **NOT optional.** Without a human builder, the system produces technically correct code that solves the wrong problem. The agents are precise but lack judgment about what matters. The builder provides that judgment.
4. **NOT a scout.** The builder does not need to personally interview stakeholders or map processes. That's the scout team's job. But the builder MUST consume what the scouts produce — reading briefing memos, understanding edge cases, knowing the business context well enough to recognize when the agents are building the wrong thing.

### Why the builder decides sequencing — not Claude

It is tempting to let Claude decide what to build next. The scout-team already does this (the orchestrator sequences waves autonomously). Why not let the builder side do the same?

Because build sequencing requires judgment that goes beyond technical dependencies:

1. **Business priority is not the same as technical dependency.** The client may need to see Feature X first for political, funding, or stakeholder reasons — even if Feature Y is technically independent and higher-priority by score.
2. **Risk tolerance is a human call.** Do we build the uncertain thing now (learning faster but risking rework) or defer it (safer but slower)? That depends on the project's risk profile, the client relationship, and the phase of the engagement.
3. **Cross-project resource allocation.** A builder managing multiple projects makes sequencing decisions based on which project needs attention most urgently — context that no single-project agent has.
4. **The builder needs to understand what's being built to review it.** If the builder didn't choose the sequencing, they may not understand why a particular piece of code exists — which makes review shallow and defeats the quality gate.
5. **Client-facing timing matters.** Demo dates, board meetings, pilot launches — human events that constrain what needs to be ready when.

The scout orchestrator can sequence autonomously because discovery is a well-understood, repeatable process (extract → structure → validate). Build sequencing is not — it depends on business context, client relationships, and strategic judgment that only the builder has.

### Skills needed

- Systems architecture — the ability to decompose a problem into modules and understand their interactions
- **Business context absorption** — the discipline to read scout briefing memos, understand edge cases, and stay informed about the business problem without personally doing discovery
- Domain knowledge — understanding the problem space well enough to validate that the solution is correct, or access to someone who does
- Ability to read and review code — the builder doesn't write code but must be able to evaluate it
- Judgment about trade-offs — knowing when "good enough" is good enough, when to cut scope, when to invest in quality

### A day in the life of a builder

This is what the builder's daily work looks like in practice — the "assembly line" view:

**Morning — sync and orient (15-20 min)**
```
Mode: status.
→ "2 worktree branches ready for review. New scout snapshot available (not synced)."

/builder sync scout_team/
→ Delta report with narrative briefing:
  "Day 3 discovery focused on identity resolution. The enrollment lead
   confirmed that below 0.70 confidence, cases ALWAYS go to manual review —
   no exceptions. This resolves BQ-001 and unblocks P1.7.

   New edge case discovered: retroactive enrollments from employer group XYZ
   account for 40% of all retro exceptions. Consider a dedicated handler.

   3 new rules, 1 contradiction resolved, 1 new tribal practice flagged."

Builder reads the briefing. Understands the business context. Approves the delta.
```

**Mid-morning — review completed work (20-30 min)**
```
Mode: review. Branch: feat/eligibility-endpoint.
→ Diff shows 4 files changed. Tests pass. CURRENT_STATE updated.
  Builder reads the code, verifies it handles the edge cases
  from the scout briefing. Merges.

Mode: review. Branch: feat/member-schema.
→ 3 files changed. Tests pass. But wait — the schema doesn't include
  the "prior coverage overlap period" field that Day 3 discovery revealed.
  Builder rejects: "Add the overlap_period field per ENT-DEC-0045 update."
```

**Late morning — advance next task (5 min to spawn, agents work independently)**
```
Mode: advance. Phase 1, next unblocked task.
→ Claude identifies P1.7 (now unblocked after sync).
  Spawns backend-engineer in worktree. Builder moves on.
```

**Afternoon — planning session if needed (30-45 min, weekly)**
```
Mode: planning. Module: Enrollment Business Logic.
→ 5-activity planning session. Builder shapes the roadmap
  for this module based on accumulated scout intelligence.
```

**End of day — feedback if gaps accumulated (10 min)**
```
/builder feedback scout_team/
→ 2 gaps from today's build work sent to scout team.
```

**Total active builder time: 1-2 hours per project per day.** The rest of the day, agents are building in worktrees. A builder can run 2-3 projects simultaneously at this cadence.

## Building architecturally complex systems

The Builder works for any software project, but some systems require additional architectural depth in their architecture.md. The most challenging category is **agentic production systems** — systems where AI agents run in production with complex orchestration, not just at build time.

### Technical discovery before architecture decisions

For complex systems, architecture decisions should come from structured technical discovery — analyzing existing systems, API constraints, platform capabilities, integration surfaces — not just the builder's intuition. This can be an extension of the scout model (scouts investigate technical landscape alongside business processes) or a separate technical spike phase before Phase 1. The goal: architecture decisions grounded in evidence about what the technology actually supports, not assumptions about what it should support.

### When your project IS an agentic system

If what you're building has AI agents running in production (not just at build time), architecture.md must address these concerns before any code is written:

**1. Runtime agent architecture**
- How agents are spawned, scaled, and terminated in production
- Isolation model (containers, VMs, serverless functions, threads)
- Communication patterns (message queues, shared state, direct RPC)
- Failure handling (what happens when an agent crashes mid-task, retry logic, circuit breakers)
- Orchestration framework selection and rationale (Azure AI, Maestra, LangGraph, CrewAI, custom — document WHY)

**2. Deterministic conversion strategy**
- What CAN be expressed as business rules (no LLM tokens needed) vs. what MUST use an LLM
- Decision framework: "Use deterministic logic when the decision space is bounded and rules are enumerable. Use LLM when reasoning requires natural language understanding, ambiguity resolution, or open-ended classification."
- This is the single highest-impact cost optimization. Every rule you convert from LLM to deterministic saves tokens on every request, forever.
- Track the conversion over time: as the team learns the domain, more decisions become convertible

**3. Cost management**
- Token budget per request, per user, per day — defined upfront, not discovered in the first invoice
- Model selection per task (expensive model for complex reasoning, cheap model for classification, no model for deterministic rules)
- Caching strategy (which LLM calls produce cacheable results, what invalidates the cache)
- Cost monitoring and alerting (when spend exceeds threshold, who gets notified, what action is taken)

**4. Memory management**
- How agents maintain state across calls (database, Redis, in-memory, context window)
- Context window budget (what goes in, what gets summarized, what gets evicted)
- Shared vs. isolated memory (which agents share state, which are isolated, what are the trust boundaries)
- Long-term memory strategy (what persists across sessions, what's ephemeral)

**5. Observability**
- How you monitor agent behavior in production (logging, tracing, metrics)
- Hallucination detection (how you know when an agent produces incorrect output)
- Cost attribution (which agents, which calls, which users are consuming what)
- Performance monitoring (latency per agent, queue depth, error rates)

**6. Platform behavior**
- Every orchestration framework (Azure AI, Maestra, LangGraph, etc.) handles spawning, memory, and error recovery differently
- Document the specific behaviors of the platform you chose — don't assume teammates know
- Document what the platform does well and what it doesn't (where you'll need custom code)

### How the Builder helps with agentic complexity

The Builder doesn't solve these architectural challenges — it structures how the team addresses them:

1. **Architecture.md captures the decisions.** Every concern listed above goes into architecture.md as a principle or constraint. Agents that build the system read these constraints at session start.
2. **Planning sessions surface gaps.** When planning a module, Activity 4 (dependency mapping) will surface: "this module needs the memory management strategy decided before it can progress."
3. **Review mode enforces the architecture.** If the architecture says "use deterministic rules for bounded decisions" and an agent writes an LLM call for something rule-based, the builder catches it in review and rejects.
4. **The IDEAS gate prevents drift.** Someone proposes "let's add an LLM agent for this." It goes to IDEAS.md. The builder evaluates: "Can this be deterministic? What's the token cost? Does it fit the cost budget?"

### What the Builder does NOT do for agentic systems

- It does not choose your orchestration framework for you
- It does not design your memory management
- It does not optimize your token usage
- It does not replace the need for deep expertise in agentic production architecture

**The builder of an agentic system must be someone who understands agentic architecture deeply.** The methodology structures their work; it doesn't substitute for their knowledge. This is why the builder role requires "systems architecture" as a core skill — and for agentic systems, that means architecture of distributed AI systems, not just conventional software.

### Proof point: Criterion

Criterion is an example of this pattern working in practice:
- **Deterministic conversion:** AI runs at build time (L1 extraction pipeline). Runtime reasoning is deterministic — no LLM at the point of care. This is exactly the "convert to deterministic rules" pattern.
- **Cost management:** Tokens are spent during extraction (one-time, amortized across all users). Runtime is DB queries + deterministic logic (zero token cost per request).
- **Architecture enforcement:** Principle 12 ("grounded, not generated") is a hard constraint in architecture.md. Any change that introduces runtime LLM generation is rejected in review.
- **Platform decisions documented:** 4-layer stack (L1-L4) with explicit boundaries. Each layer has different runtime characteristics, documented in architecture.md.

The Builder didn't make these architectural decisions — the builder did. The Builder ensured they were documented, enforced, and evolved consistently.

## Security

Security principles that every project should follow. These are not optional hardening steps for Phase 3 — they are architectural decisions made before code is written.

1. **Security requirements are defined in ARCHITECTURE.md BEFORE any code is written** — not retrofitted. Auth model, data sensitivity, encryption needs, and compliance requirements are architecture principles, not afterthoughts.
2. **The bootstrapper generates a `docs/security.md` template** covering: auth model, data classification, encryption requirements, API security, dependency scanning, secrets management, and compliance requirements. This is populated during project setup and maintained as the system evolves.
3. **The `review` mode includes security checks:** no hardcoded secrets, dependencies scanned, auth properly implemented, input validation present. These are part of the standard review contract, not a separate security review.
4. **Security is a canonical module concern.** Each module's planning session should include "what are the security implications of this module's work?" — not as a checkbox, but as a genuine question about data access, trust boundaries, and attack surface.
5. **For healthcare/financial clients:** compliance requirements (HIPAA, SOC2, PCI) are architecture principles, not afterthoughts. They constrain every design decision from Day 1 — data storage, access logging, encryption, audit trails. If you discover compliance requirements mid-build, that's a planning failure.

## Code Quality

Quality gates that apply to every `review` mode session. These are the minimum bar for merging work.

1. **Tests exist and pass.** No merging code without tests for the changed functionality. The scope of tests matches the scope of change — unit tests for logic, integration tests for wiring, end-to-end tests for user-facing flows.
2. **Linting is clean.** The project's linter runs without new warnings. Existing warnings are not the reviewer's problem, but new ones are.
3. **No hardcoded secrets, credentials, or API keys in committed code.** Environment variables, config files in `.gitignore`, or a secrets manager. No exceptions.
4. **CURRENT_STATE.md is updated in the same commit as the code.** If the capability changed, the doc changes. If the doc didn't change, either the work wasn't meaningful or the update was forgotten — both are problems.
5. **The interlock deliverable still works after the merge.** Regression check: the thing that proves the current phase works must still work after the new code lands. If it doesn't, the merge is rejected until the regression is fixed.
6. **Security scan passes (if configured).** If the project has dependency scanning, static analysis, or security linting configured, those checks must pass before merge.

### Not vibe coding

The builder model produces production-grade code within defined architectural constraints. Every line is reviewed by the builder before merge. Every module has ownership. Every feature passes through the IDEAS gate. This is structured engineering with AI agents, not uncontrolled code generation.

The difference between "vibe coding" and this model:
- Vibe coding has no architecture doc. This model starts with one.
- Vibe coding has no quality gate. This model reviews every diff.
- Vibe coding has no idea backlog. This model gates every feature through IDEAS.md.
- Vibe coding has no state tracking. This model maintains CURRENT_STATE.md as the honest record.
- Vibe coding hopes the AI gets it right. This model assumes it won't and builds review into the process.

## Multi-Model Review

When review mode runs, a SECOND model (or a fresh, independent Claude session) reviews the agent's work before the builder sees it. The building agent and reviewing agent should never be the same session — fresh eyes catch what the builder missed.

**Why this matters:** No single model catches more than ~55% of bugs in its own output (observed in multi-model consultation systems like CodevOS). The building agent is biased toward its own work. A fresh session with no shared context reads the diff cold and finds different classes of issues.

**In practice for Claude Code:** Spawn a fresh agent specifically for review, with instructions to find issues. It reads the diff, the task spec, the architecture constraints, and the file-pattern rules — then reports findings. The builder sees the review findings alongside the diff.

The review agent's prompt is simple: "You are reviewing another agent's work. Read the diff, the task spec, the architecture constraints, and the file-pattern rules. Find issues. Report them." It has no knowledge of the building agent's intent, reasoning, or context — only the artifacts.

This is not a replacement for the builder's review. It's a pre-filter. The builder still reads the diff and makes the merge/reject call. But the review agent surfaces issues the builder might miss, especially in unfamiliar code or complex logic.

## Adversarial Review

An option within review mode that inverts the normal review bias. Instead of "does this look correct?" the reviewer is instructed: "Find issues. Zero findings requires explicit justification — re-analyze or explain why the code is genuinely flawless."

This breaks confirmation bias. Normal review expects correctness and skims. Adversarial review expects problems and digs.

**Trade-off:** ~18% of findings will be false positives. The builder's judgment filters these. But the real issues caught are worth the noise.

**When to use:** Adversarial review is recommended for security-sensitive code, complex business logic, and any code that touches money, auth, or PII. For straightforward UI changes or documentation, standard review is fine.

The builder invokes this with: `Mode: review (adversarial). Branch: feat/payment-processing.`

Adversarial review composes with multi-model review. The fresh review agent can be given the adversarial prompt, so you get both fresh eyes and a hostile lens. This is the highest-scrutiny configuration — use it for the code that matters most.

## Two-Stage Review

Review mode now operates in two distinct passes:

**Pass 1: Spec compliance — "Did you build what was asked?"**
- Compare the deliverable against the task description in ROADMAP.md
- Check that the acceptance criteria (if specified) are met
- Verify the scope matches — no extra features added, no required features missing
- Check that the approach aligns with the architecture principles and any relevant ADRs

**Pass 2: Code quality — "Is it built well?"**
- Code follows file-pattern rules
- Tests exist and cover the changed functionality
- No hardcoded secrets, credentials, or API keys
- Error handling is present and specific (no bare except)
- CURRENT_STATE.md is updated
- Security implications considered (if touching auth, data, or external APIs)

**Why two passes:** Conflating "right thing" and "thing right" in a single review misses issues. An agent might build the wrong thing beautifully — Pass 1 catches that. An agent might build the right thing poorly — Pass 2 catches that. Separating the concerns makes each pass more focused and thorough.

**In practice:** The multi-model review agent (fresh session) performs both passes and reports findings organized by pass. The builder sees: "Spec compliance: 2 findings. Code quality: 1 finding." This makes it immediately clear whether the problem is what was built or how it was built.

## Reconciliation Step (Completeness Check)

After building and before milestone review, a **reconciliation step** compares the delivered code against the specification to verify completeness.

This is NOT the same as review (which checks quality). Reconciliation checks: **"Did we build everything we said we would?"**

**What reconciliation checks:**
- Each acceptance criterion in the spec has corresponding implementation
- Each acceptance criterion has corresponding tests
- No scope drift — nothing was built that wasn't specified (over-engineering)
- No missing scenarios — edge cases listed in the spec are all addressed
- Partial implementations are flagged with what's remaining

**Output:** A completeness report:
```
Reconciliation Report — Phase 1

AC-1: Broker can create a policy        ✓ Implemented, 4 tests
AC-2: Quote calculation returns premium  ✓ Implemented, 6 tests
AC-3: Multi-tenant isolation             ✓ Implemented, 3 tests
AC-4: Carrier API returns quotes         ✗ NOT IMPLEMENTED (deferred to Phase 2)
AC-5: Audit logging on state changes     ✓ Implemented, 2 tests
                                           ⚠ Missing test for "delete" state change

Scope drift: None detected
Completeness: 4/5 acceptance criteria (80%). AC-4 explicitly deferred.
```

The builder reviews this alongside the review findings. Reconciliation prevents the scenario where code passes all quality gates but doesn't actually deliver what was specified.

## Checkpoint Preview (Comprehension-Ordered Review)

When a builder enters review mode, the system doesn't just dump a raw diff. It presents changes in **comprehension-optimized order** — organized by concern and intent, not by file path.

**Five steps:**

1. **Orientation** — One-line summary of what was built, number of files changed, scope assessment.
2. **Walkthrough** — Changes organized by concern (e.g., "data model changes," "API endpoint," "frontend wiring," "tests"). Sequenced for understanding: foundational changes first, dependent changes after.
3. **Risk tagging** — 2-5 highest-risk spots tagged by category: auth, data integrity, security, performance, external API. The builder's attention is directed to where it matters most.
4. **Testing verification** — What tests cover the changes, what's untested, suggested manual verification steps.
5. **Decision** — Builder approves, requests rework, or opens a discussion.

**Why this matters:** Raw diffs ordered by file path force the builder to reconstruct intent from implementation details. Checkpoint preview reconstructs the author's intent first, then walks through how it was implemented. The builder understands *what* was built before evaluating *how*.

**Composes with other review features:** Checkpoint preview is the presentation layer. Multi-model review, adversarial review, and two-stage review are the analysis layers. Together: the builder gets a comprehension-ordered walkthrough with independent findings organized by spec compliance and code quality.

## Protocol Enforcement / Quality Gates

The Builder Operating Model replaces the honor system with enforced gates. Instead of trusting that agents follow the contract, specific checkpoints must pass before the workflow advances.

**Gate 1: Build-verify gate.** Tests must pass before review can happen. When an agent completes a task, the system runs the project's test suite automatically. If tests fail, the builder sees the failures — not the diff. Review mode is blocked until the build is green. This prevents the pattern where agents skip broken tests intending to "fix them later."

**Gate 2: State-doc gate.** CURRENT_STATE.md must be updated in the same commit as code changes. If the diff includes code changes but CURRENT_STATE.md is untouched, review mode flags it: "Code changed but CURRENT_STATE not updated. Update before review."

**Gate 3: Review-before-merge gate.** No worktree branch merges to main without passing through review mode. The builder must explicitly approve. There is no auto-merge.

**Gate 4: IDEAS gate (existing).** No feature work outside the roadmap. New features go through IDEAS.md evaluation first. This gate already exists in the model — it is listed here for completeness.

**Implementation in Claude Code:** These gates are enforced by the builder's session (the main Claude thread). When running `advance`, Claude checks test output before presenting the review. When running `review`, Claude verifies CURRENT_STATE was updated. The enforcement is procedural (Claude follows the protocol) rather than mechanical (a state machine), but the contract is explicit: skip a gate, and the builder should reject the work.

**Principle:** Scripted helpers that enforce gates are fine. Scripted decisions that bypass them are not. The builder can override any gate with explicit justification — but the default is enforcement, not trust.

## Hooks as Enforcement Mechanism

Claude Code's **hooks system** transforms advisory rules into deterministic enforcement. Instead of trusting that the process is followed, hooks PREVENT violations mechanically.

**Three hook types:**
- **PreToolUse** — fires before a tool executes. Can block the action. Example: prevent writes to files outside the agent's module scope.
- **PostToolUse** — fires after a tool executes. Can validate results. Example: after every file write, run the linter automatically.
- **Stop** — fires when the agent tries to complete. Can block completion. Example: prevent task completion if CURRENT_STATE.md wasn't updated.

**Example hooks for the Builder model:**
```
PreToolUse: Write
  -> If file is outside agent's module code anchors -> BLOCK
  -> "This file is outside your module scope. Request builder approval."

PostToolUse: Write
  -> If file matches *.py -> run ruff check automatically
  -> If file matches *.ts -> run tsc --noEmit automatically

Stop:
  -> If CURRENT_STATE.md not in changed files -> BLOCK
  -> "CURRENT_STATE.md was not updated. Update it before completing."
```

**This is the difference between procedural and mechanical enforcement.** Procedural: "Claude, please follow the review protocol." Mechanical: hooks literally prevent the agent from skipping steps. The agent cannot write files outside its scope. The agent cannot complete without updating state docs.

Hooks compose with the existing gate system. The gates define WHAT must pass. Hooks enforce HOW it's prevented from being skipped.

## Adaptive Guardrails — Rules, Evidence, and Self-Improvement

The adaptive guardrails are the layer between the AI model and your codebase that encodes your project's knowledge into AI behavior. Three mechanisms make the guardrails compound in value over time. (Credit Carl Tierney: "The harness is the product. The model is just the engine.")

### File-Pattern Rules

Code-level guardrails triggered by file patterns. Claude Code supports `.claude/rules/` files with glob patterns:

```
# .claude/rules/python-api.md
globs: engine/api/**/*.py
---
- All endpoints use parameterized queries, never string interpolation
- Every endpoint has input validation using Pydantic models
- Never return raw exception messages to client
- Every new endpoint gets a corresponding test
```

These prevent convention violations, security anti-patterns, and framework mismatches AUTOMATICALLY — the builder doesn't need to catch these in review because Claude can't violate them. The bootstrapper generates starter rules based on tech stack during init.

### Evidence-Based Verification

Review mode requires EVIDENCE, not just pass/fail. "It should work" is not evidence. (Credit Carl Tierney.)

After a task completes, the system provides:
- **Actual test output** — which tests ran, what they verified, specific data checked
- **API response** — actual HTTP response from endpoints that were changed
- **UI screenshot** — rendered page showing the feature works visually
- **DB query result** — data was actually persisted correctly

The builder sees evidence in plain language and can verify correctness functionally without reading code.

**Testing agent.** After an agent completes a task, a SEPARATE testing agent automatically writes test cases for the changed functionality, runs them, takes screenshots, and presents evidence to the builder. This is automated evidence generation — the building agent builds, the testing agent proves it works.

### Spec-Driven Independent Testing

The testing agent tests against the **specification**, not the code. It does not read the implementation first.

**Traditional testing flow:** Read code -> write tests that exercise the code -> verify
**Spec-driven testing flow:** Read spec/acceptance criteria -> write tests that verify the spec -> run against the build -> divergence = bug

**Why this matters:** If the testing agent reads the code first, it tests what was BUILT, not what was SPECIFIED. It will write tests that pass against incorrect implementations because it's testing the implementation, not the intent.

**In practice:**
- The testing agent receives: the task spec, acceptance criteria, and the project's architecture docs
- It does NOT receive: the source code of the implementation
- It writes functional tests from the acceptance criteria
- It runs those tests against the build
- Any divergence between spec and actual behavior is flagged

This is the principle: **"Separate the builder from the validator."** The agent that writes the code never validates its own work. Different context, different prompt, different objective.

**"Ready for Testing" prompt.** When a phase's tasks are complete, the system surfaces a concise testing checklist — what to test, where to click, what to expect:

```
What am I testing?

You're testing that the Settings view works end-to-end:
1. Does it load? — Click the Settings gear icon
2. API Key — Paste your key, hit Save, refresh — does it persist?
3. Vault Path — Save the path, does it scan and show folders?
4. Categories — Toggle some on/off — do they persist on refresh?
```

Keep it terse. Four points, not fourteen.

### Self-Improvement Loop

After each session where the builder corrects Claude:

1. **Detect the correction pattern** — what category of mistake was it?
2. **Propose a new rule** — a file-pattern rule or architecture principle that prevents recurrence
3. **Builder approves or skips** — no automatic rule creation
4. **Track improvement** — session 1 had X corrections, session 10 had Y
5. **The system gets permanently better** — corrections become rules, rules prevent future corrections

This is the compounding differentiator. The guardrails don't just prevent known mistakes — they learn from new ones. Each builder correction is an opportunity to make the system permanently smarter.

### Guardrail Library (Stack-Specific Shared Rules)

Organizations maintain a **shared guardrail library** — a repository of technology-specific rule modules that projects inherit based on their tech stack.

**Library structure:**
```
pe-guardrails/
  stacks/
    sitecore.md           — Sitecore XM Cloud implementation patterns
    databricks-mosaic.md  — Mosaic AI + Langchain patterns, token management
    dotnet-core.md        — .NET 8+ patterns, EF Core, CQRS, MediatR
    react-typescript.md   — Strict TypeScript, component patterns
    azure-services.md     — App Service, Functions, Blob Storage patterns
    fastapi-python.md     — Pydantic, async patterns, SQLAlchemy
  patterns/
    multi-tenancy.md      — Schema isolation, tenant-scoped queries
    hipaa-compliance.md   — PHI handling, audit logging, encryption
    api-gateway.md        — Rate limiting, auth, versioning
```

**How it works:**
1. During `/builder init` or `/builder architecture`, the tech stack is determined through discussion or ADR creation
2. The builder identifies relevant guardrail modules from the connected library
3. Builder approves which modules to inherit
4. Modules are copied into the project's `.claude/rules/` directory
5. Project-specific rules accumulate on top of inherited stack rules through the self-improvement loop

**Connecting to a library:**
- `/builder guardrails connect <path-or-url>` — connect to a shared library
- `/builder guardrails list` — show available modules
- `/builder guardrails inherit <module>` — pull a module into the current project
- `/builder guardrails contribute <rule>` — propose a project rule back to the shared library

**Why this matters:** When PE starts a new Sitecore + .NET project, the team doesn't start from scratch. They inherit 20+ battle-tested rules from previous Sitecore projects. The guardrails compound not just within a project, but across the organization's entire portfolio.

### Self-Improvement Visibility

The self-improvement loop is one of the builder's most powerful features, but it's invisible. The builder knows rules accumulate, but can't easily see: how many corrections led to rules? What categories of mistakes are most common? Is the system actually getting better?

Self-improvement visibility surfaces this data:

**Session-level metrics:**
- Corrections made this session
- Rules proposed (accepted / skipped)
- Categories of corrections (security, conventions, architecture, testing, naming, etc.)

**Project-level trends:**
- Total rules by category (bar chart or table)
- Corrections per session over time (should trend down)
- Most common correction categories (where should the builder focus?)
- Rules that prevented the most violations (highest-value rules)

**How it surfaces:**
- At the end of each session, the self-improvement summary is shown: "This session: 2 corrections -> 1 new rule (security category). Project total: 18 rules. Corrections trending down: 4.2/session -> 2.1/session over last 10 sessions."
- During `/builder status`, include a guardrail health line.
- During `/builder retrospective`, include a full guardrail analysis.

**Why this matters:** Without visibility, the builder can't tell if the guardrails are working. With visibility, they can see the compounding effect — and it reinforces the discipline of approving rules when corrections happen.

## TDD Mode

An optional development mode where agents follow strict Test-Driven Development: Red-Green-Refactor.

**The cycle:**
1. **Red** — Write a failing test that describes the desired behavior. Run it. Verify it fails. If it passes, the test isn't testing anything new.
2. **Green** — Write the minimum code to make the test pass. Nothing more. Run the test. Verify it passes.
3. **Refactor** — Clean up the code without changing behavior. Tests still pass.
4. **Commit** — Each Red-Green-Refactor cycle is a commit.

**When to use TDD mode:**
- Business logic with clear expected inputs/outputs
- API endpoints with defined request/response contracts
- Data transformations and calculations
- Bug fixes (write the test that reproduces the bug first, then fix it)

**When NOT to use TDD mode:**
- UI/frontend work where the "test" is visual inspection
- Exploratory prototyping where requirements are still forming
- Infrastructure/deployment work
- One-off scripts

**Enforcement:** When TDD mode is active, the agent must demonstrate the Red phase — the test fails before implementation code is written. Code written before a test exists is flagged. This prevents the common pattern of writing code first and tests second (or never).

**The builder enables TDD mode** by specifying it when advancing: *"Mode: advance. TDD mode. Phase 2, task P2.3."* It's opt-in, not default — because not all tasks benefit from TDD.

## Systematic Debugging

A formalized 4-phase debugging methodology. When a bug is reported or discovered, the builder invokes `/builder debug <issue>`.

**Phase 1: Reproduce**
- Confirm the bug exists and is reproducible
- Document exact steps, inputs, expected vs. actual output
- If the bug can't be reproduced, stop — don't fix ghosts

**Phase 2: Investigate root cause**
- Trace the execution path from symptom to source
- Read the relevant code, not just the error message
- Identify the ACTUAL root cause, not just the proximate trigger
- Common mistake: fixing symptoms without understanding cause leads to whack-a-mole

**Phase 3: Fix**
- Write a test that reproduces the bug (the test should fail)
- Fix the root cause — the minimum change that addresses it
- Verify the test passes
- Verify no regressions (existing tests still pass)

**Phase 4: Verify with defense-in-depth**
- Beyond the specific fix: are there other places where the same pattern could cause the same bug?
- If yes, fix those too (or add a file-pattern rule to prevent recurrence)
- Update CURRENT_STATE.md if the fix changes behavior
- Consider whether this bug pattern should become a guardrail rule

**Why 4 phases:** Agents tend to pattern-match fixes without understanding root cause. Phase 2 is the critical gate — no fix is attempted until the root cause is understood. This prevents the cycle of fix -> new bug -> fix -> new bug.

## Requirements Depth

For complex projects, flat task lists in ROADMAP.md are insufficient. The operating model supports three levels of requirements depth, adopted progressively as project complexity demands.

### Work Breakdown Structure

For complex projects, ROADMAP.md tasks should link to richer decomposition:
- **Per-module technical specs** — not just one-line task descriptions
- **API contracts between modules** — request/response shapes, auth, error handling
- **Dependency graph** — which tasks block which, shown explicitly in ROADMAP
- **Layer-by-layer decomposition** — frontend, backend, data, and integration tasks per feature

Can live in ROADMAP.md itself (enhanced task descriptions) or in a separate `docs/specs/` folder with per-feature spec documents.

### Architectural Decision Records (ADRs)

A `docs/decisions/` folder tracking WHY architectural choices were made:

```
docs/decisions/
  001-database-choice.md
  002-auth-approach.md
  003-api-style.md
```

Each ADR has: context, decision, rationale, consequences, alternatives considered. Living docs that evolve. The planning mode should propose new ADRs when architectural decisions are made.

### PRD/Specs per Feature

For significant features, a lightweight product requirements doc or technical spec should exist before the task enters the ROADMAP:
- **What** the feature does (user-facing behavior)
- **Acceptance criteria** (how you know it works)
- **Technical approach** (how it should be built, at appropriate detail)
- **Edge cases** (what could go wrong)
- **Dependencies** (what it needs from other modules)

These specs feed the testing agent — acceptance criteria become test cases automatically.

## What the Client Sees

The builder model is an internal methodology. The client sees outcomes, not process.

### Internal (PE keeps)

These are tools of the trade, not deliverables:
- Operating model reference (this document)
- Dashboard (`/team-dashboard`)
- Agent definitions (`.claude/agents/`)
- Skills (`~/.claude/skills/`)
- Planning memos (commit messages, session notes)
- IDEAS.md (the internal backlog gate)
- Builder modes and session vocabulary

### Client-facing

These are what the client pays for and evaluates:
- Working software (demo environments, staging, production)
- Documentation (user-facing docs, API docs, architecture diagrams)
- Test results (proof the system works as specified)
- Deployment artifacts (infrastructure, CI/CD, runbooks)
- Discovery deliverables (if scout-team is in play: briefing memos, process maps, evidence graphs)

### The methodology is PE's competitive advantage

The client sees the outcomes, not the process. They see software delivered faster, with fewer bugs, with better architecture than they expected. They don't need to know that an AI agent wrote the first draft and a human builder reviewed every line. The methodology — the operating model, the agent decomposition, the quality gates, the planning sessions — is what makes the outcomes possible. It stays internal.

## Updating the architecture doc

The generated ARCHITECTURE.md changes rarely. Updates require:
1. Explicit rationale
2. Review of downstream impact
3. Deliberate update pass across affected docs

Drive-by changes are not allowed.
