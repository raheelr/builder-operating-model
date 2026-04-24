# Scout Team → Prototype Translation Rules

This document defines how Scout Team Evidence Graph entities translate into prototype development components. Used by the `project-bootstrapper` agent when invoked with `--from-scout`.

## Prerequisite: reading the graph

Before applying translation rules, load these files from the scout-team engagement:

```
<scout_team>/graph/<latest>/
  sources.json         → understand what was discovered and from where
  claims.json          → atomic facts with provenance
  entities.json        → canonical things (workflows, decisions, rules, systems, etc.)
  edges.json           → relationships between entities
  artifact_rows.json   → pre-projected rows with confidence and priority

<scout_team>/reports/<latest>/
  briefing_memo.md     → executive summary of discovery
  contradiction_register.md  → unresolved conflicts
  tribal_knowledge_log.md    → undocumented practices
  coverage_heatmap.md        → which domains are well-covered vs dark
  priority_ranking.md        → top entities by priority score
```

## Entity → component translation

### Workflow (ENT-WF) → Frontend flow

Each workflow entity becomes a candidate **user journey / frontend flow**.

| Graph field | Prototype output |
|---|---|
| `name` | Flow name / page title |
| `attributes.trigger` | Entry point (URL route, button click, event listener) |
| `attributes.frequency_estimate` | Load expectations, caching strategy |
| `attributes.happy_path_duration` | UX complexity target |
| `attributes.primary_actor` | Primary user role for this flow |
| Child `ENT-WS` steps (via edges) | Screens / states within the flow |

**Agent ownership:** `frontend-engineer` (or equivalent)

**Module derivation:** Group workflows by `domain` → each domain with ≥2 workflows becomes a frontend module.

### Workflow Step (ENT-WS) → Screen state or API endpoint

| Step type | Component type |
|---|---|
| `data_entry` | Form component / input screen |
| `decision` | Branching UI or API decision endpoint |
| `system_action` | Backend API call (automated) |
| `handoff` | Transition screen + notification trigger |
| `wait` | Polling/async state with status display |
| `review` | Review/approval UI component |
| `escalation` | Escalation flow (modal or redirect) |

**Key fields:**
- `is_workaround: true` → the prototype should replace this with a proper solution. Flag as a Phase 1 "fix the workaround" task.
- `pain_point` → becomes a UX requirement for the replacement
- `systems_used` → integration dependencies for this step

### Decision (ENT-DEC) → Business logic module

The `target_mode` from the boundary strategist determines the implementation shape:

| target_mode | Implementation |
|---|---|
| `straight_through` | Fully automated backend rule. No UI needed. API endpoint that applies rules and returns result. |
| `assist` | Backend logic + review UI. System proposes answer, human confirms/overrides. |
| `human_required` | Workflow step with tooling. System presents context, human decides. |
| `uncertain` | Flagged for Phase 5 hardening. Build as `human_required` initially. |

**Key fields:**
- `attributes.inputs_required` → API request schema / form fields
- `attributes.consequence_of_error` → error handling priority, validation depth
- `attributes.volume_estimate` → performance requirements
- `attributes.regulatory_constraints` → compliance requirements, audit logging
- `boundary.percentage_split` → expected load distribution across automation tiers
- `boundary.confidence_thresholds` → system design parameters for automation gates

**Module derivation:** Group decisions by `domain` → each domain becomes a backend module.

### Rule (ENT-RUL) → Business rule

| Graph field | Prototype output |
|---|---|
| `attributes.condition` | Rule condition / predicate |
| `attributes.action` | Rule action / consequence |
| `attributes.exceptions` | Edge case handlers |
| `family` | Rule group / rule engine namespace |
| `attributes.source_type` | Provenance tier (SPD=authoritative, tribal=risky) |
| `attributes.is_tribal` | If true → SME validation gate before implementation |
| `attributes.validation_status` | Implementation confidence |

**`family` → rule group mapping:**
Rules with the same `family` value belong to the same rule group. Each group maps to a module in the rules engine.

**Tribal rules:** Do NOT implement tribal rules directly. Create an IDEAS.md entry for each tribal rule: "Validate rule X with SME before implementation." The planning session will sequence validation before build.

### Exception (ENT-EXC) → Error handler / edge case flow

| Graph field | Prototype output |
|---|---|
| `attributes.frequency_category` | Priority: `daily`/`continuous` → Phase 1; `weekly` → Phase 2; `monthly`/`rare` → Phase 3 |
| `attributes.ai_classifiable` | If true → automated error triage. If false → manual escalation flow. |
| `attributes.resolution_approach` | Implementation hint for the fix |
| `attributes.downstream_impact` | Severity → error handling depth |
| `attributes.requires_tribal_knowledge` | If true → SME validation gate |

### System (ENT-SYS) → Integration adapter

| Graph field | Prototype output |
|---|---|
| `attributes.category` | Integration type (API, ETL, portal scrape, etc.) |
| `attributes.data_flows_in/out` | API contract (request/response shapes) |
| `attributes.replaces_candidate` | If true → this system is being replaced by the prototype. Mock first, integrate never. |
| `attributes.is_shadow_it` | If true → the new system should formalize what this spreadsheet/email-hack does |
| `attributes.fragility_signal` | Integration risk → defensive coding, circuit breakers |
| `integrates_with` edges | Integration dependency graph |

**Phasing rule:** Systems with `replaces_candidate: false` get integrated in Phase 4. Systems with `replaces_candidate: true` get mocked from Phase 1 (the prototype replaces them, so integration is unnecessary — but the mock must faithfully reproduce their behavior).

### Actor (ENT-ACT) → User role / auth scope

Each unique actor becomes a user role in the prototype's auth system. Actors with the same `role` but different `person_name` are the same role.

**Output:** Role-based access control rules, role-specific UI views, persona documentation for UX decisions.

### Handoff (ENT-HND) → Inter-system bridge

Handoffs between actors/systems within the prototype become internal workflow transitions. Handoffs to external systems become integration points with SLA tracking.

## Confidence → implementation gates

| Confidence | Implementation gate |
|---|---|
| **HIGH** | Build directly. Validated by ≥2 sources. |
| **MEDIUM** | Build with a "verify on first use" flag. Single authoritative source. |
| **LOW** | Create as IDEAS.md entry first. Validate before building. |
| **TRIBAL** | **Do not build without SME validation.** Create a gated task: "Validate with SME → then implement." Tribal rules implemented without validation are the #1 source of prototype drift from reality. |
| **CONFLICT** | **Do not build until contradiction is resolved.** Create an IDEAS.md entry with both sides of the conflict cited. The resolution decision drives the implementation. |

## Priority score → phase assignment

Scout-team computes `priority_score = (frequency × impact × build_criticality) × 10` per entity.

**Default phase mapping:**

| Priority range | Phase | Rationale |
|---|---|---|
| 70-100 | Phase 1 | High frequency + high impact + build-critical. Core loop. |
| 40-69 | Phase 2 | Important but not core-loop. Assisted flows. |
| 20-39 | Phase 3 | Lower frequency or lower impact. Full coverage. |
| 1-19 | Phase 4-5 | Rare or low-impact. Integration and hardening. |

**Overrides:**
- Any entity with `regulatory_constraints` not null → Phase 1 regardless of score (compliance is non-negotiable)
- Any entity with `target_mode: uncertain` → Phase 5 (needs more discovery before build)
- Any entity with `confidence: CONFLICT` → deferred until conflict is resolved

## Edge → dependency mapping

Graph edges translate to build-order dependencies:

| Edge label | Build dependency |
|---|---|
| `governed_by` (Decision → Rule) | Build the rule before the decision logic |
| `depends_on` | Build the dependency first |
| `occurs_in` (Exception → Workflow) | Build the workflow before exception handling |
| `integrates_with` (System ↔ System) | Both systems' adapters must be specced before either is built |
| `hands_off_to` (Step → Step) | Steps in sequence; build receiver before sender if async |
| `contradicts` (Claim ↔ Claim) | **Build blocker.** Resolve contradiction before implementing either side. |

## Module derivation algorithm

1. **Group entities by `domain`** (e.g., "enrollment", "identity_resolution", "coverage_decisions").
2. **Within each domain, group by layer:**
   - Frontend layer: workflows + workflow steps + actor UIs
   - Backend layer: decisions + rules + exceptions
   - Integration layer: systems + handoffs
3. **Each (domain, layer) pair with ≥3 entities becomes a candidate module.**
4. **Merge small modules** (< 3 entities) into the nearest related module.
5. **Name modules** after their domain + layer: e.g., "Enrollment Frontend", "Enrollment Business Logic", "Enrollment Integrations".
6. **Assign each module to a subagent** based on layer:
   - Frontend modules → `frontend-engineer`
   - Backend modules → `backend-engineer`
   - Integration modules → `integration-engineer`
   - Cross-cutting modules → `platform-engineer`

## Subagent derivation

Default subagents for a scout-team-derived prototype:

| Agent | Owns | Boundary |
|---|---|---|
| `frontend-engineer` | All frontend modules (flows, screens, forms, role-based UI) | Does not touch backend logic or integration adapters |
| `backend-engineer` | All backend modules (decisions, rules, exceptions, business logic) | Does not touch frontend components or integration adapters |
| `integration-engineer` | All integration modules (system adapters, handoffs, external APIs) | Does not touch frontend or core business logic |
| `data-engineer` | Database schema, migrations, data models, ETL | Does not touch frontend or business logic |

If the engagement scope is small (< 3 domains), collapse `integration-engineer` into `backend-engineer` and run with 3 agents.

If the engagement scope is large (≥ 6 domains), consider per-domain agents: `enrollment-engineer`, `claims-engineer`, etc.

The builder always adjusts the agent list during `init --from-scout` confirmation (step 7). The algorithm proposes; the human decides.

## Carrying forward scout-team intelligence

### Contradictions → IDEAS.md
Every unresolved `contradicts` edge becomes an IDEAS.md entry:
```
### [CONTRADICTION] <entity name>: <claim A summary> vs. <claim B summary>
Status: New (requires resolution before build)
Provenance: CLM-XXXXX ↔ CLM-YYYYY
```

### Tribal knowledge → gated tasks
Every entity where all supporting claims have `tribal: true` gets a two-step task in ROADMAP:
1. "Validate <entity> with SME" (knowledge task)
2. "Implement <entity>" (build task, blocked by #1)

### Low-confidence items → deferred with gates
Entities with `confidence: LOW` are sequenced to Phase 3+ with an explicit "validate before build" gate.

### Coverage heatmap → planning insight
Domains marked DARK or THIN in the coverage heatmap get an IDEAS.md entry: "Discovery gap: <domain>. Follow-up needed before Phase X planning."

### Handoff package → project docs
The scout-team handoff bundle (`reports/<latest>/handoff/`) is copied into the project's `docs/discovery/` folder as the provenance record. Every implementation decision should be traceable back to a discovery claim.
