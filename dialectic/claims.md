# claims.md — Cycle 1

Focal proposition **Q0**: *Is the Lebenswelt usefully formalizable as (a) a generative model, (b) a possibility-space/horizon constraining generative models, (c) neither, or (d) something requiring a fundamentally different formal ontology?*

Status vocabulary: `ESTABLISHED` (follows from a discipline's own standards) · `SPECULATIVE` (could be fruitful, unproven) · `INVALID` (category error, misuse, historical error, unjustified inference) · `SURVIVED` (withstood Round 4) · `REJECTED` · `SUPERSEDED`.

Nothing is deleted. Superseded claims retain their IDs.

---

## A. Claims about the identification `Lebenswelt = generative model`

**C-01** `[USER-HYPOTHESIS]` "From the FEP perspective, this [the Lebenswelt] is the human-level generative model. It is what is within the markov-blanket that mediates the outside with the internal."
**Status: INVALID → REJECTED.** Four independent refutations, no shared premise between them:
1. *[PHENOMENOLOGY]* A generative model is a density held by a system over its sensory causes. The Lebenswelt is pregiven and **anonymous** — not held by anyone. To make it `L_i`, indexed to individual `i`, already destroys it, because it is intersubjectively constituted *prior to* the individuation of subjects. **The subscript is the error.**
2. *[FRANKFURT]* Habermas's Lebenswelt is not a representation at all but three reproduction *processes*. A density has no reproduction functions and cannot exhibit anomie.
3. *[FEP]* A generative model in active inference is `p(o,s|θ,m)` — typed, with a fixed state space and a likelihood. Nothing in the source paper specifies observations, states, parameters, or a likelihood for `L`. The identification is notational, not mathematical.
4. *[HISTORY-OF-SCIENCE]* The identification requires that Husserl's `Lebenswelt` and Friston's generative model share an ancestor. They do not. Friston's lineage runs Helmholtz → Ashby/Conant → Pearl → variational Bayes. Husserl's runs Brentano → the *Krisis*. The shared invocation of Kant is a shared *citation*, not a shared *concept*.

**C-01a** `[CROSS-DISCIPLINARY-SYNTHESIS]` The refutation of C-01 is over-determined: four disciplines reject it for non-overlapping reasons. Over-determination of this kind is the strongest available evidence in a purely argumentative process. **Status: SURVIVED** (see `survivors.md` S-04).

---

## B. Claims about `Lebenswelt ≈ possibility space Ω`

**C-02** `[USER-HYPOTHESIS]` `L_i ⇝ (Ω_i, Π_i, Σ_i, Γ_i, …)`, i.e. the lifeworld decomposes into intelligible-state space, available-action space, semantic relations, and salience weighting.
**Status: SPECULATIVE, survives only after differentiation and re-indexing.** See `formalizations.md` F-02. Three amendments are mandatory:
- **Re-index.** The bearer is a *practice-community* over a *historical duration*, not an individual. Write `L_{c,t}`, not `L_i`. Husserl's own plurality concept is *Heimwelt/Fremdwelt* (Steinbock, *Home and Beyond*), which is generational and communal.
- **De-conflate.** The four components have different bearers, different timescales, and different observability. `Γ` (salience) is measurable in weeks from attention/audit data; `Ω` (intelligibility) changes over generations and is only visible in its breakdowns. Bundling them into one object licenses illicit scale-jumps. See `contradictions.md` K-004.
- **Do not call it the Lebenswelt.** It is at best a *model of sedimented constraint*, an operational proxy. Naming it "Lebenswelt" imports transcendental authority that the operationalisation cannot cash.

**C-03** `[PHENOMENOLOGY]` `Ω` presupposes the individuation of states; horizon is what makes individuation possible; therefore modelling horizon as `Ω` is circular.
**Status: ESTABLISHED within phenomenology; SURVIVED cross-examination.** The FEP agent's rejoinder — that all science is locally circular and this is benign — was accepted as reducing the objection from *fatal* to *scope-limiting*: `Ω` can model a *sedimented, already-individuated* residue of a horizon, never the horizonal function itself. The residue is real and worth modelling. It is not the Lebenswelt.

**C-04** `[ANTHROPOLOGY-STS]` `Ω_A ≇ Ω_B` — different lifeworlds may involve non-isomorphic conceptual spaces, not different distributions over a common space.
**Status: ESTABLISHED; SURVIVED; upgraded to a formal programme.** This is the single strongest claim in the cycle. It kills the default Bayesian framing (which presupposes a shared `Ω` on which all parties hold priors), and it has a candidate mathematics that is *not* FEP: sheaf-theoretic contextuality. See `formalizations.md` F-06.

---

## C. Claims about FEP's licence over social phenomena

**C-05** `[FEP]` FEP proper requires a system at nonequilibrium steady state with a *fixed* state space carrying a stationary density.
**Status: ESTABLISHED.**

**C-06** `[RED-TEAM]` Therefore the phenomenon the programme wants to model — historical transformation of the space of intelligible states, `Ω → Ω'` — **voids FEP's own mathematical preconditions.** Structure learning in active inference (Bayesian model reduction/expansion) always operates inside a fixed *super*-space `Ω*` of possible models. So either (i) `Ω'` ⊆ `Ω*` and nothing historically novel ever occurs — history is pre-contained in the measure space — or (ii) genuine novelty occurs and FEP has no formalism for it.
**Status: SURVIVED. Highest-value claim of Cycle 1.** No agent could break it. See `survivors.md` S-05 and `questions.md` Q-01.

**C-06a** `[CROSS-DISCIPLINARY-SYNTHESIS]` The horn (i) of C-06 — a pre-given `Ω*` containing all future intelligibility — **is Absolute Knowing in measure-theoretic disguise.** The universalism the Frankfurt School attacked in Hegel reappears not as a philosophical thesis but as a *technical precondition of the formalism*, where it is invisible to critique because it looks like a modelling convention. Adorno's identity-thinking is exactly this: subsumption under a fixed conceptual scheme. A σ-algebra is a fixed conceptual scheme with a completeness axiom.
**Status: SURVIVED. This is the concept the collision produced that none of the input frameworks had.** See `survivors.md` S-06.

**C-07** `[USER-HYPOTHESIS]` "The FEP gives us one way to understand geist. Geist is not universal. It is historically contingent."
**Status: PARTIALLY VALID, but self-undermining as stated.** The de-universalising move is right and is well supported by Hegel's own *Volksgeist*/*Zeitgeist* and by Steinbock's generative phenomenology. But it cannot be grounded in FEP, because FEP is *more* universalising than Hegel: Hegel's Absolute is at least a historical achievement, whereas FEP's fixed state space is an *analytic precondition* that no history can revise. Using FEP to de-universalise Geist substitutes a harder universal for a softer one.

---

## D. Claims about super-agents and empire

**C-08** `[USER-HYPOTHESIS]` "empire... may not be a super-agent in of itself, but perhaps, a particular dynamic of active inference between super-agents and people."
**Status: SPECULATIVE, and the *best* move in the source paper.** The shift from *substance* to *relation* is exactly the anti-reification move Lukács demands, and the source paper makes it unprompted. What does not survive is "active inference" as the name of the dynamic — see C-09. Reformulated as C-08\*.

**C-08\*** `[CROSS-DISCIPLINARY-SYNTHESIS]` **Imperial is a predicate of a relation between collectivities, not of a collectivity.** Its differentia is *asymmetric enforced translation*: A can compel B's states to be reported in `Ω_A`, B cannot compel the converse, and the residue of B not expressible in `Ω_A` is administratively nonexistent rather than merely unrecorded. **Status: SURVIVED.** See `survivors.md` S-07, `formalizations.md` F-06.

**C-09** `[COMPLEXITY]`+`[SOCIOLOGY]` Calling an institution a "super-agent with a Markov blanket" explains nothing that organisational network analysis does not already explain, **unless** one demonstrates macro-level informational closure for a specified variable.
**Status: ESTABLISHED.** This converts an ontological assertion into a testable one, and in most cases the test fails or succeeds only in narrow channels (financial reporting, legal personhood, formal decision procedures) rather than globally. Corporations are Cyert–March coalitions with conflicting goals; assigning one policy `π` erases the internal politics that is the object of study.

---

## E. Claims about Hegel and FEP

**C-10** `[USER-HYPOTHESIS]` "remarkable symmetry between the movement of the dialectic... with the concept of Bayesian error-correction, free-energy minimization."
**Status: INVALID as identity; the analogy is real but shallow.** Refutations: (i) prediction error is graded and metric, contradiction is structural and ungraded; (ii) free-energy minimisation *eliminates* discrepancy, determinate negation *produces* determinate new content out of failure; (iii) decisive — Bayesian model comparison requires a **fixed evidence functional**, Aufhebung is the transformation of the evaluative functional itself. See `survivors.md` S-02, `dead_ends.md` D-02.

**C-11** `[HISTORY-OF-SCIENCE]` The Hegel §339 citation ("Nature's formations are determinate, bounded, and as such enter into existence") does not support Markov blankets. It is a claim about *Bestimmtheit* in the logic of the Concept. "Bounded things are bounded" is shared by every boundary-theory ever proposed and therefore discriminates between none of them. **Status: ESTABLISHED. Zero-information citation.**

**C-12** `[HISTORY-OF-SCIENCE]` **The programme has already been run once.** Cybernetic systems theory applied to society — Ashby, Conant & Ashby's good-regulator theorem, Deutsch's *The Nerves of Government*, Beer, and above all Luhmann's autopoietic systems theory — is FEP's actual near ancestor, far closer than German idealism. **Habermas's system/lifeworld distinction and the concept of colonization were formulated *specifically against* Luhmann** (Habermas–Luhmann, *Theorie der Gesellschaft oder Sozialtechnologie*, 1971). Therefore "critical computational sociology built on FEP" risks re-running Luhmann's programme under a Habermasian banner — reconstructing the position the critical concept was invented to defeat.
**Status: SURVIVED. Highest-value historical finding of Cycle 1.** See `survivors.md` S-08.

---

## F. Claims about colonization and AI

**C-13** `[FRANKFURT]` None of `H1`–`H6` is Habermas's colonization thesis; all are agent-internal. `H7` is Scott's legibility, which is a real and distinct mechanism but not the same one. The colonization thesis requires `H8`: substitution of the *coordination mechanism* between actors. **Status: ESTABLISHED; SURVIVED.** See `formalizations.md` F-08.

**C-14** `[CROSS-DISCIPLINARY-SYNTHESIS]` The AI-specific case is unusually clean for `H8` because the substitution leaves a **documentary trace**: a decision reached by a score is not contestable *in kind* — you cannot argue with a risk score, only appeal against it procedurally. The distinguishing observable is not "is a model used?" but **"can the affected party raise a validity claim that the deciding party is obliged to redeem in reasons?"** **Status: SURVIVED, and empirically operationalisable.** See `formalizations.md` F-08, `survivors.md` S-03.

**C-15** `[SOCIOLOGY]` The Palantir claims in the source paper require distinguishing two explanations that predict the same observables: (a) the vendor supplies integration infrastructure to agencies whose intent and capacity pre-exist, versus (b) the technology transforms what those agencies can intend. These are different causal claims with different remedies. The source paper asserts (b); the evidence given supports (a). This is not a defence of the vendor — under (a) the harm is identical — it is a demand that the *causal* claim carry its own weight rather than borrowing force from the moral one.
**Status: OPEN. Empirical bottleneck.** See `questions.md` Q-07.

**C-16** `[HISTORY-OF-SCIENCE]` Two biographical claims about Karp used as premises in the source paper require primary-source verification before load-bearing use: (i) that Habermas supervised the dissertation — the frequently reported supervisor is Karola Brede, with Habermas as institutional context rather than advisor; (ii) the exact content of the aggression thesis as opposed to its journalistic summary. **Status: TEXTUAL BOTTLENECK.** See `questions.md` Q-08.

---

## G. Answer to Q0

**C-17** `[CROSS-DISCIPLINARY-SYNTHESIS]` Adjudication of the focal question:
- **(a) generative model — REJECTED.** Over-determined refutation, C-01.
- **(b) possibility-space constraining generative models — SURVIVES ONLY AS A DIFFERENTIATED HEURISTIC, AND MUST NOT BE CALLED THE LEBENSWELT.** It models the sedimented, already-individuated residue of a horizon. That residue is a legitimate object. Naming it "Lebenswelt" is the *Ideenkleid* move Husserl diagnosed. C-02, C-03.
- **(c) neither — TOO COARSE.** It abandons genuine formal traction on `Ω_A ≇ Ω_B`, on residuality, and on the looping effect.
- **(d) something requiring a different formal ontology — CORRECT, AND ITS SHAPE IS NOW PARTLY SPECIFIABLE.** Five constraints, each derived from a different discipline's refutation of (a)/(b):
  1. **No pre-given total state space.** (from C-06; else Absolute Knowing smuggled in)
  2. **Inter-agent coordination *mechanisms* as first-class objects, not only agent-internal states.** (from C-13)
  3. **Translation loss and residuality as primitives, not error terms.** (from C-04)
  4. **Bearers are practice-communities across historical durations, not individuals.** (from C-02)
  5. **Retrodictive as well as prospective evaluation; the evaluative functional must itself be a variable.** (from C-10/S-02)

Candidate formal home meeting 1, 3 and partially 2: **sheaf-theoretic contextuality** over a site of practices — local sections agreeing pairwise with no global section, obstruction measurable as a cohomological invariant. This is *not* FEP, and its independence from FEP is the point. See `formalizations.md` F-06 and its own destruction test F-06-D.
**Status: SURVIVED Cycle 1. Primary output.** *(Cycle 2 amendment: F-06's job is compelled declaration of the cover, not measurement of incommensurability. See `formalizations.md` F-06 revision.)*

---

## H. Cycle 2 → 3 handoff: the composed definition of empire

**C-18** `[CROSS-DISCIPLINARY-SYNTHESIS]` **PROPOSED, NOT YET ATTACKED. Do not promote to `survivors.md` until Cycle 3 has run on it.** The Cycle 1 and 2 results compose into a definition that none of the input frameworks contained:

> A relation between collectivities `A` and `B` is **imperial** when:
> **(i)** `A` enforces a cover `𝓜_A` under which `B`'s states must be reported — *the coarsening* (S-11);
> **(ii)** `B`'s residue under `Ω_A` is rendered administratively **nonexistent** rather than merely unrecorded (S-07 iii);
> **(iii)** `T₂` is absent for `B` — no forum exists in which `B` can force revision of `κ_A` (S-13);
> **(iv)** the enforced frame presents as **discovery rather than decision** (S-12).

**What it discriminates.** Ordinary bureaucracy fails (iii) — `T₂` present. Conquest without administration fails (i) — extraction without an imposed cover. Trade asymmetry fails (i) and (iii). Federated or plural administration fails (ii) — residue is recorded as unknown rather than as absent.

**THE SCANDAL, stated by the process against its own construction:** this definition contains **no violence, no extraction, no accumulation.** Lenin, Luxemburg, Wallerstein, and Hardt & Negri are entirely absent. An arrangement satisfying (i)–(iv) while extracting nothing is a **standards body**. A definition of empire that cannot distinguish the Colonial Office from ISO has failed at the first hurdle, and this one currently cannot. → `questions.md` Q-15.

**Two defences, both to be attacked in Cycle 3:**
- **(a) Differentia, not genus.** The epistemic conditions specify what is distinctive about the *administrative form* of empire and presuppose extraction as the genus. Weak: this makes C-18 an addendum to political economy, not a contribution.
- **(b) Mechanism.** The coarsening is *how* extraction is made routine and deniable — it is the operation that converts violence into administration, which is why empires generate paperwork and why the paperwork is not incidental. **Stronger, and it makes a historical prediction: the coarsening event should precede or accompany the stabilisation of extraction, never follow it.** Cadastral survey before or with dispossession; census and classification before or with conscription and taxation; not after.

**Status: SPECULATIVE. This is Cycle 3's focal proposition, and the empirical test in (b) is its first destruction attempt.**
