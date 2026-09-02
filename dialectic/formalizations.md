# formalizations.md — Round 5 trial record

Every entry must answer: (1) what each variable denotes; (2) what empirical object could instantiate it; (3) what assumptions make it meaningful; (4) what would falsify it; (5) what social or phenomenological structure it erases.

An entry with no answer to (5) is not finished. An entry with no answer to (4) is decoration and is marked `REJECTED — DECORATIVE`.

---

## F-01 — `Lebenswelt = generative model p(o,s|θ,m)`

**REJECTED.** See `claims.md` C-01. Fails (1): no observation space, no latent states, no likelihood is specifiable without arbitrary stipulation. Fails (4): nothing could falsify it because nothing determinate is asserted. Fails (5) catastrophically: erases anonymity, pre-givenness, intersubjective priority, and the three Habermasian reproduction processes.

---

## F-02 — `L_{c,t} ⇝ (Ω_{c,t}, Π_{c,t}, Σ_{c,t}, Γ_{c,t})`, bearer = practice-community, dissolved into four independently measured objects

**STATUS: RETAINED AS SCAFFOLD, NOT AS AN OBJECT.** The tuple is a *checklist of things a model must not silently conflate*, not a mathematical entity. The bundle itself is rejected (`contradictions.md` K-004); the four components survive separately.

| | denotes | instantiated by | timescale | falsified by |
|---|---|---|---|---|
| `Ω_{c,t}` | categories in which members of community `c` can render a situation as a case of something | classification schemes actually in force: diagnostic codes, legal statuses, form fields, kinship terms in use | generations | showing the operative categories are stable across communities where the theory predicts divergence |
| `Π_{c,t}` | actions practically available, not merely physically possible | eligibility rules, budget lines, licensing, platform affordances, documented refusals | months–years | showing action repertoires do not shift when the stated determinants shift |
| `Σ_{c,t}` | which categories entail, exclude or license which others | co-occurrence and inferential structure in institutional text and talk | decades | showing entailment structure is invariant across communities |
| `Γ_{c,t}` | what is salient, and with what weight decisions attend to it | audit trails, attention allocation, escalation thresholds, precision of reliance on a signal | weeks | showing attention weights are unresponsive to documented interventions |

**Erases (5):** everything that resists being a category, an action, a relation or a weight — that is, precisely the horizonal, the pre-predicative, the atmospheric, and the bodily. This erasure is *not* correctable within the formalism; it must be tracked externally. See F-07.

**Naming rule:** this object is `Sedimentation`, never `Lebenswelt`.

---

## F-03 — `M_i → M_{i+1}` as dialectical transformation

**REJECTED as a model of Aufhebung; RETAINED as ordinary Bayesian model selection under a different name.** The FEP theorist and the Hegel scholar converged here from opposite directions and this is the cleanest kill in the cycle:

Bayesian model selection computes `M* = argmax_M F(M | data)` — it requires **one functional `F` scoring all candidates**. Whatever else Aufhebung is, it is the case that the *criterion* (`Maßstab`) is transformed by the failure it diagnoses. A fixed `F` makes that structurally impossible to represent.

Consequence: `M_i → M_{i+1}` is not "closer to dialectical transformation than ordinary Bayesian updating." It **is** ordinary Bayesian model comparison, and the dialectical reading adds nothing but an honorific.

---

## F-04 — Making the evaluative functional a variable: `(M_t, F_t) → (M_{t+1}, F_{t+1})`

**STATUS: SPECULATIVE. The only formal proposal in this cycle with any claim to dialectical content.**

`F_t` = the scoring functional in force at `t` — what counts as a good account, an adequate explanation, a resolved case.

(1) Variables: `M_t` a model, `F_t: 𝔐 → ℝ` an evaluative functional over models. (2) Instantiation: `F_t` is observable as *institutional standards of adequacy* — what an audit accepts, what a court admits, what a journal publishes, what a clinical guideline treats as sufficient evidence. These are documented and change datably. (3) Assumptions: that standards of adequacy are recoverable from institutional records, and that they change at a rate distinguishable from model change. (4) Falsification: if `F_t` never changes except by exogenous shock, or changes only in ways predictable from `M_t` alone, the construction is idle. (5) Erases: the *experience* of a standard collapsing, which is what Hegel's *Verzweiflung* names; and it still presupposes that adequacy is scalar, which no Hegelian would concede.

**Honest limit:** even this is at best an *external* description of a criterion change, not the self-relating movement Hegel describes. The Hegel scholar's rating: "partially faithful; it captures that the measure moves, and nothing of why the movement is the thing's own."

---

## F-05 — The carving map `κ` as the theoretically loaded object

**STATUS: SURVIVED. Reorients the programme.**

From `contradictions.md` K-002: the interesting variable is not the state space but the map that produces it.

`κ_{A}: Situations → Ω_A`, an institution's operative carving.

(1) Denotes: the procedure by which an encountered situation is rendered as a case of a category — intake forms, triage protocols, model input schemas, feature engineering. (2) Instantiated by: schemas, codebooks, ontology files, training-label definitions, form fields. These are *literally artefacts* and can be collected. (3) Assumes: that the operative carving is recoverable from artefacts plus practice (it is often not — informal carving diverges from documented carving; this gap is itself measurable). (4) Falsified by: showing outcomes are insensitive to carving under controlled variation. (5) Erases: the labour of the front-line worker who bends the category to fit the person — the very *mētis* that keeps such systems working. Any `κ` reported as a function has erased the discretion that makes it survivable.

**Derived measurable: residuality.** Following Bowker & Star: `r_A(t) = |κ_A^{-1}(other)| / |domain|`, the load on residual categories, plus *torque* — the divergence between a person's biographical trajectory and the trajectory their record can represent. Residual-category growth is a leading indicator of carving failure and is available in nearly every administrative dataset. **This is the most immediately implementable measurement in the entire programme, and it requires no FEP.**

---

## F-06 — Non-isomorphic lifeworlds as sheaf-theoretic contextuality

**STATUS: SPECULATIVE, HIGH VALUE, UNDER ACTIVE ATTACK.**

The problem `Ω_A ≇ Ω_B` (`claims.md` C-04) has no home in Bayesian formalism, which presupposes a shared event space carrying different priors. Contextuality supplies an object with the right shape.

Setup: a site whose objects are *contexts* (practical settings in which a determinate set of questions can be jointly asked), a presheaf assigning to each context the assignments locally intelligible in it, and restriction maps for context inclusion.

- **Local sections** = descriptions valid within a practice.
- **Compatibility on overlaps** = successful partial translation. This is why translation *seems* to work.
- **No global section** = no single scheme reconciling all local descriptions, even though every pair reconciles.
- **Obstruction class** = a cohomological invariant measuring the failure.

Why this is the right shape and Bayesian formalism is not: it reproduces the actual ethnographic phenomenon — **pairwise translation succeeds everywhere and global reconciliation fails** — which a common-`Ω` model cannot represent at all, and which "they have different priors" gets exactly wrong.

(1) Contexts denote practical settings with a joint question-set; sections denote locally intelligible descriptions. (2) Instantiation: paired classification of the same cases by two institutional regimes (clinical vs. traditional diagnosis; state cadastral vs. customary tenure; platform content policy vs. community norm), with overlap structure given by cases classifiable in both. (3) Assumes each context supplies a determinate local question-set — **a strong and contestable assumption**, and the formalism's main hostage. (4) **Falsification: if empirically obtained overlap data always admits a global section, the construction has no object.** This is a real, decidable, empirical test. (5) Erases: everything about *why* the local sets are what they are; the historical and political production of contexts; and the embodied practice that makes a context a context rather than a list.

**F-06-D — destruction test (`contradictions.md` K-009).** The anthropologist's objection is that computing an obstruction converts equivocation into a quantity in the analyst's own scheme. **Decisive sub-test: is the obstruction class invariant under change of the analyst's frame?** If the measured incommensurability is an artefact of the analyst's carving, F-06 is the imperial move in better mathematics and must be rejected. If it is invariant, it is a genuine relational object. This is a mathematics question, answerable before more philosophy. Priority 1 for Cycle 2.

---

## F-07 — Reflexive model effect: `P(X_{t+1} | X_t, M) ≠ P(X_{t+1} | X_t)`

**STATUS: SURVIVED, WITH CORRECTED ATTRIBUTION.**

This is the one proposed formalisation that is both well-posed and empirically established — and it is **not FEP**. It is Hacking's *looping effect of human kinds* and *making up people*, with Desrosières on the constitutive role of statistical categories. The equation is a fair compact statement of a documented phenomenon.

(1) `M` = a deployed classification or scoring model; `X` = the classified population's states. (2) Instantiated by: risk scores, credit categories, diagnostic categories, predictive-policing deployments, recommender exposure. (3) Assumes deployment is datable and, ideally, staggered — which it often is. (4) Falsified by: staggered-rollout designs showing no divergence in the classified population's trajectories attributable to classification independent of the intervention the classification triggers. (5) Erases: the *first-person* dimension of being made into a kind — the experience of coming to answer to a description — which is the part Hacking himself insisted mattered most.

**Institutional intervention chain** `M_t → A_t → X_{t+1} → D_{t+1} → M_{t+1}` (model → action → world → data → model) is retained as the causal skeleton of F-07 and is straightforwardly implementable in simulation. Its danger: simulating it will show it converging, and convergence will look like validation. State in advance that convergence of such a loop is a *pathology indicator*, not a fit statistic.

---

## F-08 — `H8`: colonization as substitution of coordination mechanism

**STATUS: SURVIVED. The correct formalisation of Habermas's thesis, and it was absent from the original hypothesis set `H1`–`H7`.**

All of `H1`–`H6` transform something inside an agent (`P`, `Γ`, `Σ`, `Π`, `Ω`, `𝔐`). `H7` (institutional forcing through a shared administrative ontology `Φ: {L_i} → Ω_S`) is inter-agent, and is a real mechanism — **but it is Scott's legibility, not Habermas's colonization.** They are separable: a state can impose a uniform ontology while still resolving disputes through contestable reason-giving (a legible but communicatively intact bureaucracy), and it can abandon reason-giving without imposing new categories (media-steering within existing categories). Two mechanisms, two remedies.

`H8`: at a decision site `d`, let the coordination mechanism be
- `R` — coordination by mutual redemption of criticisable validity claims: the affected party can raise an objection that the deciding party is *obliged to answer in reasons*;
- `S` — coordination by steering media: the decision is settled by price, score, or authority output, and the affected party's recourse is procedural (appeal, exit) rather than argumentative.

**Colonization = the drift of `d` from `R` to `S` in domains where the coordination task is symbolic reproduction rather than material reproduction.**

(1) Denotes: the mechanism of coordination *at a decision site*, not a property of an agent or a territory. (2) Instantiation — genuinely available: is a reason given? is the reason of a *type the affected party can contest*? is there an obligation to respond? what fraction of objections receive substantive rather than procedural answers? Administrative appeal records, complaint logs, benefits determination files, content-moderation appeal data, model-explanation policies. (3) Assumes the `R`/`S` distinction is locally decidable at a site — much weaker and safer than assuming a system/lifeworld *territorial* boundary, which is what dodges Fraser's objection (`contradictions.md` K-007). (4) Falsified by: showing sites with high `S`-coordination show none of the predicted reproduction pathologies, or that `R`/`S` cannot be coded reliably between independent coders. (5) Erases: the *quality* of communication — `R` can be coded present while being coercive, ritualistic or performed in bad faith. `H8` measures the form of the obligation, not the achievement of understanding. Habermas's actual criterion is the latter. **This is a real and permanent loss, and it is the correct place for the formalism to stop.**

**Why the AI case is the clean instance (`claims.md` C-14):** a score is not contestable *in kind*. One can appeal it; one cannot argue with it, because it makes no claim whose grounds it is obliged to defend. Deployment of unarguable scores in symbolic-reproduction domains is `R → S` substitution with a documentary trace. **This is the single most defensible empirical proposition the cycle produced, and it does not use FEP at all.**

---

---

## F-09 — The coarsening event: anti-correlated detectors across assimilation

**STATUS: SURVIVED CYCLE 2. The cycle's one new empirical prediction.**

From `cycle2_rounds.md` Part I. Contextuality is cover-relative and vanishes in both degenerate limits. Imposing a single administrative ontology declares all questions jointly askable, which drives the obstruction to zero *by construction* while the loss relocates.

Define, over a period of institutional consolidation, for paired classification of the same case population under two regimes:
- `χ(t)` = contextuality obstruction under the operative cover at `t`
- `r(t)` = residual-category load and torque under the dominant carving at `t`

**Prediction: `χ` and `r` are anti-correlated across a coarsening event, and the transition is sharper than either series alone reveals.** Contested contact: `χ` high, `r` low. Post-assimilation: `χ` → 0, `r` high.

(1) Denotes: the passage from contested plural classification to a single enforced ontology. (2) Instantiation: cadastral vs. customary tenure through land registration; clinical vs. traditional diagnostic categories through health-system standardisation; platform policy vs. community norm through moderation consolidation; occupational or ethnic census categories through schedule revision. (3) Assumes both regimes leave records over the transition — the binding constraint, since the losing regime's records are typically what consolidation destroys, and *that destruction is itself the datum*. (4) **Falsified by:** finding coarsening events where residual load does not rise, or contested-contact periods with no detectable obstruction. (5) Erases: the experience of the transition; and it can only be computed after the fact, from records produced by the winning regime.

**Why it matters critically:** it formalises why a consolidated system *looks* consistent. Zero contextuality is not evidence of successful reconciliation. **It is what successful imposition produces.**

---

## F-10 — Type-contestation and level-2 colonization

**STATUS: SURVIVED CYCLE 2. The second-order form of F-08.**

At a decision site `d`, F-08 asks whether the affected party can raise an objection the deciding party must answer in reasons. F-10 asks the question one level up, about the carving itself.

- **token-contestation** `T₁`: is there a channel to contest *the application* of a category to a case?
- **type-contestation** `T₂`: is there a forum in which "this category should not exist / should be redrawn" is a possible move, with institutional uptake and the power to force revision of `κ`?

**Level-2 colonization = `T₁` present, `T₂` absent.** This is the modal condition of algorithmic governance and it is why the presence of appeals processes is not evidence against colonization — appeals are the mechanism by which `T₁` substitutes for `T₂`.

(1) Denotes: distribution of revisionary authority over a classification scheme. (2) Instantiation: who can amend a codebook, a schema, a label definition, a diagnostic manual; what the amendment procedure is; whether the classified population has standing in it; observed revision events and their initiators. All documented. (3) Assumes revision authority is traceable — usually true, occasionally obscured, and obscurity is itself a finding. (4) Falsified by: finding systems with `T₂` present that show the same pathologies as systems without it — which would sever the criterion from the outcomes. (5) Erases: informal type-contestation that never reaches a forum — refusal, exit, sabotage, and the slow drift of front-line practice away from official categories. **These are the most common forms of type-contestation and the formalism sees none of them.** This is the same erasure as F-05(5) and it is not accidental: *what a formalism of authority cannot see is precisely unauthorised contestation.*

**Critical use:** `T₂` is a constitutional criterion, not a methodological one. No modelling practice can satisfy it. It is the operational form of `survivors.md` S-13 and the only exit found from K-006 — and it is not an exit for the *modeller*, only a criterion for judging arrangements.

---

## F-06 — REVISION after Cycle 2

The Round 5 entry stands with one correction. F-06 was described as making incommensurability measurable. **It does not.** The obstruction is cover-relative (`cycle2_rounds.md` I.1), and both degenerate limits give zero.

**Corrected statement of what F-06 does:** it converts the assertion "these ontologies are incommensurable" into the empirical claim "these questions are not jointly askable in any single practical setting," which is ethnographically decidable per site — and it forces the analyst to declare that claim in contestable form. A common-`Ω` Bayesian model makes the opposite assumption *silently*.

**F-06's honest value is therefore not measurement. It is compelled declaration.** Which places it inside `survivors.md` S-12: its contribution is to make the frame declaration unhideable, not to compute a fact about the world.

Test F-06-D (Q-03) is **closed**. Result: not invariant; E7's technical objection upheld; the construction survives with a changed job description; E7's standing dissent migrated to K-011.

---

## Verdict on the formalization trial

Of the constructions attempted, those that survived are F-05 (carving and residuality — Bowker & Star / Scott), F-07 (looping — Hacking / Desrosières), F-08 (coordination-mechanism substitution — Habermas), and provisionally F-06 (contextuality — Abramsky–Brandenburger applied to Viveiros de Castro's equivocation).

**None of the survivors is an FEP construction.** Every FEP-derived formalisation (F-01, F-03, and the blanket-as-social-boundary identification) was rejected. The FEP theorist agent's own summary, recorded verbatim in `cycle1_rounds.md` R4: *"The mathematics I am here to defend does not license any of these applications, and saying so is the most useful thing I can do."*

This is a result about the research programme, and it should not be softened.
