# definitions.md

Discipline-specific meanings of contested terms. A term appears here when two agents were found to be using it non-identically. Equivocation is the primary failure mode detected in Cycle 1.

---

## Markov blanket

**[FEP — technical]** A partition of the states of a random dynamical system into internal `μ`, sensory `s`, active `a`, external `η`, such that `μ ⊥ η | b` where `b = (s,a)`. Existence depends on the sparsity structure of the Jacobian of the flow at a nonequilibrium steady state (NESS). It is a *conditional-independence statement about a density*, not a description of a physical membrane.

**[FEP — Pearl's original]** Pearl (1988): the minimal set of nodes d-separating a node from the rest of a Bayes net. A property of a *model*, chosen by a modeller.

**Critical distinction (Bruineberg, Dołęga, Dewhurst & Baltieri 2022, "The Emperor's New Markov Blankets"):**
- *Pearl blanket* = a formal construct internal to someone's model.
- *Friston blanket* = a metaphysical claim that the blanket demarcates a real thing in the world.

The slide from the first to the second is unlicensed. **This distinction is structurally identical to Lukács's reification thesis, arrived at by a completely independent route.** See `survivors.md` S-01.

**[USER-HYPOTHESIS]** "a statistical boundary, a membrane... moreso, a perceptual boundary." — This is a Friston blanket plus a phenomenological gloss. Two unlicensed steps, not one.

**[PHENOMENOLOGY]** No equivalent. The inside/outside topology presupposed by the blanket is a Cartesian spatialisation of a relation (intentionality) that phenomenology holds to be non-spatial and not containment-structured.

**Technical fragility (must be stated whenever the blanket is invoked socially):** Aguilera, Millidge, Tschantz & Buckley (2021) showed that for generic systems the internal states do *not* parameterise a posterior over external states; that result requires restrictive conditions (near-linear flow, specific solenoidal structure). Biehl, Pollock & Kanai (2021) identified errors in the derivation connecting internal-state dynamics to Bayesian inference. The mathematical object is far weaker than its social borrowings assume.

---

## FEP / active inference / predictive coding — NOT interchangeable

- **FEP (proper):** a claim that any system possessing a Markov blanket at NESS can be *described as if* it minimises variational free energy. A description principle, closer to Hamilton's principle than to a mechanism.
- **Active inference:** a normative process theory. Requires an explicit generative model, a POMDP, and expected free energy `G(π)` for policy selection. Adds substantive, falsifiable commitments FEP alone does not carry. (Its derivation is itself contested — Millidge, Tschantz & Buckley, "Whence the Expected Free Energy?", 2021.)
- **Predictive coding:** one specific message-passing scheme (hierarchical, Gaussian, precision-weighted prediction errors). Neither necessary nor sufficient for FEP.

The source paper uses all three as one word. Every claim in it must be re-indexed to exactly one. Most re-index to *predictive coding* — the weakest and most local of the three.

**Empirical correction, flagged not smoothed:** the negative-afterimage example is standardly explained by photoreceptor bleaching and opponent-channel adaptation — peripheral, retinal, non-inferential. It is not evidence for FEP, for active inference, or for hierarchical predictive coding. Citing it as such is exactly what the red team calls *vocabulary-generality capture*.

---

## Lebenswelt

**[PHENOMENOLOGY — Husserl, *Krisis* 1936]** The pregiven, always-already-there ground (*Boden*) of all praxis and all science. Not an object, not a representation, not possessed by anyone. It is *lived through* (durchlebt), **anonymous**, and **pre-individuated**. Its structure includes *Typik* (pre-predicative typification) and *horizon*. The central *Krisis* argument is that mathematisation throws an *Ideenkleid* (garb of ideas) over the lifeworld and substitutes it for true being (*Substruktion*). **Husserl's thesis is a prediction about, and an indictment of, precisely the project proposed here.**

**[FRANKFURT — Habermas, TCA vol. 2, 1981]** Explicitly *de-transcendentalised* and reconstructed linguistically via Mead, Durkheim, Schutz. Three structural components — **culture, society, personality** — with three reproduction processes — **cultural reproduction, social integration, socialisation** — and three pathologies — **loss of meaning, anomie, psychopathology**. It is a *reproduction process*, not a space.

Husserl's is a transcendental-ground concept; Habermas's is a resource-and-reproduction concept. **Not the same concept. Not compatible.** Habermas's is a deliberate demotion.

**[USER-HYPOTHESIS]** "shared cultural symbols, language, and experiences... this is the human-level generative model." — Conflates Husserl's and Habermas's senses and then adds a third (individual generative model) that neither author would accept. Rejected: `dead_ends.md` D-01.

**Ruling:** "lifeworld" may not be used as a synonym for "culture" or "shared context." Where the source paper does so, substitute the intended narrower term.

---

## Horizon

**[PHENOMENOLOGY]** Not a set of possibilities. Horizon-intentionality has *und so weiter* structure: **determinable indeterminacy**. It is not "one of these N options" but "more, of this style, unspecified." A horizon does not have members. It has *style* and *typicality*.

**Formal consequence:** `Ω` as a set (or measurable space) presupposes prior individuation of states. Horizon is supposed to be *what makes individuation possible*. Therefore `Lebenswelt ≈ Ω` is not merely imprecise; it is **circular** — it presupposes the explanandum. See `contradictions.md` K-002.

---

## Contradiction

**[HEGEL]** *Widerspruch* — a structural self-undermining: a determination that, thought through consistently, requires its opposite. **Not graded.** There is no "a little bit of contradiction." It is a relation, not a magnitude.

**[FEP]** Prediction error — a graded, metric quantity in a state space; typically a precision-weighted residual. It has a norm. It can be small.

**These are not the same kind of object.** One is structural, one is metric. Identification is a category error: `dead_ends.md` D-02.

**[SOCIOLOGY / MARXIAN]** "Contradiction" (forces vs. relations of production) is a third thing again — a functional incompatibility between institutional complexes, diagnosed retrospectively. Neither Hegelian nor Fristonian. The source paper slides across all three.

---

## Aufhebung / determinate negation

**[HEGEL]** *Bestimmte Negation*: the negation of a determinate content yields a determinate new content. In the *Phenomenology*, consciousness "provides its own criterion" (*Maßstab*); when a shape of consciousness fails by its own standard, **the standard itself is transformed along with the object.** The movement is legible as necessary only retrospectively, *für uns*, through *Erinnerung*.

**The formal point that survived every round:** Bayesian model selection requires a **fixed evidence functional** (marginal likelihood / variational free energy) common to all candidate models. Aufhebung is precisely the **transformation of the evaluative functional itself**. This is not a difference of degree or of vocabulary. It is a structural incompatibility at the level of the mathematics. See `survivors.md` S-02.

**"Thesis–antithesis–synthesis"** is Fichte via Chalybäus, not Hegel (Mueller 1958). Any FEP↔Hegel mapping built on the triad maps onto something Hegel did not hold. Note that the DESTROY/PRESERVE/ELEVATE protocol governing this document *is* that triad. See `meta_critique.md` MC-03.

---

## Geist

**[HEGEL]** Not a collective mind, not distributed cognition, not a super-organism. Objective spirit = the ensemble of institutions, law and custom (*Sittlichkeit*) in which freedom is *actualised*. Geist is **self-relating** — the process of coming to know itself as what it is — and is sustained by **mutual recognition** (*Anerkennung*), a **normative** relation, not a statistical one. Hegel explicitly opposed Romantic organicism about the state.

**[USER-HYPOTHESIS]** "super-agent of humans, a shared markov blanket." — This is Romantic organicism, the position Hegel attacked. `dead_ends.md` D-03.

---

## Reification

**[FRANKFURT — Lukács 1923]** *Verdinglichung*: a **historically specific social form** in which social relations take the form of relations between things, arising from the universalisation of the commodity form. Its **subjective correlate is the contemplative stance** — the calculating observer confronting law-like regularity, able to predict but structurally unable to intervene qua observer.

**Consequence, unavoidable:** on Lukács's own terms the computational modeller occupies the paradigmatic reified position. "Critical computational sociology" is not incidentally at risk of reification; **the modelling stance *is* the reified stance.** This is stronger than the source paper's worry and cannot be answered by better modelling hygiene. See `contradictions.md` K-006.

**[LOOSE / WHITEHEADIAN]** "Treating an abstraction as a concrete thing" — the fallacy of misplaced concreteness. This is the sense the source paper uses. It is weaker and ahistorical. Both senses are legitimate; they must not be traded on interchangeably.

---

## Colonization of the lifeworld

**[FRANKFURT — Habermas]** The **replacement of communicatively achieved coordination (*Verständigung*, the redemption of criticisable validity claims) by delinguistified steering media (money, power)** in domains where **symbolic** reproduction — not material reproduction — is at stake.

**The mechanism is a change in the coordination mechanism *between* actors.** It is not, in the first instance, a change in anyone's beliefs, categories, salience, or action repertoire. Those are downstream symptoms.

**Consequence for Round 7, decisive:** hypotheses `H1`–`H6` in the research problem are all **agent-internal transformations**. None of them is Habermas's concept. `H7` is inter-agent but is Scott's legibility, not Habermas's colonization. The missing hypothesis is `H8`. See `formalizations.md` F-08 and `survivors.md` S-03.

**Known internal problem:** the criterion "domains where symbolic reproduction is at stake" requires a functionalist premise. Fraser (1985) showed the system/lifeworld boundary naturalises the gendered division of labour — the family is classed as lifeworld though it is power-saturated. Honneth pressed the same dualism objection. Any model built on the distinction inherits this. Do not launder it into a variable.

---

## Super-agent / collective agency

**[COMPLEXITY]** Legitimate only if a coarse-graining exists whose macro-dynamics are (approximately) informationally closed with respect to micro-detail — testable via causal-state / ε-machine closure, or `Ψ`-style emergence criteria. This is an **empirical claim about a specific macro-variable**, not a licence to speak of "the corporation" as an agent generally.

**[SOCIOLOGY]** The firm is a coalition with conflicting goals (Cyert & March); Arrow forbids non-dictatorial preference aggregation. Collective agency, where it exists, is constituted by **procedure and governance**, not by an averaged model. Any formalism assigning one policy `π` to an institution has already erased the internal politics that is the sociological object.

---

## Provenance tags

`[USER-HYPOTHESIS]` `[FEP]` `[PHENOMENOLOGY]` `[HEGEL]` `[FRANKFURT]` `[SOCIOLOGY]` `[ANTHROPOLOGY-STS]` `[COMPLEXITY]` `[HISTORY-OF-SCIENCE]` `[MODEL-INFERENCE]` `[CROSS-DISCIPLINARY-SYNTHESIS]` `[RED-TEAM]`
