# General ε-structures: beginning without pretending to know the state space

Status: research direction, not an implemented statistical method and not a commitment to one representation.

## Starting point

The intended starting statement is stronger than “the answer lies in one interval.” It is closer to:

```text
I do not know the value.
I do not know how many distinct kinds of not-knowing are active.
I do not know their resolution conditions.
I may not know the depth of containment among them.
I may not know how the regions interact.
I may not know which observations could distinguish the live alternatives.
```

A schematic state may contain many ε-like regions:

```text
ε₁, ε₂, ε₃, ...
((•))
(((((•)))))
```

with no prior promise that:

- the number of ε objects is finite;
- all ε objects have the same mathematical type;
- containment depth is known;
- every containment relation is tree-shaped;
- two regions are independent, disjoint, nested, additive, or probabilistic;
- every region has a known scale;
- a resolution procedure exists;
- the system knows what evidence would resolve it;
- one “true answer” is already expressible in the current state space.

This is a better candidate foundation for incomplete knowledge than ordinary intervals. `intervals.idr` remains one small exact region library that Econometrician-in-a-Box may use when one-dimensional bounds are actually justified.

## ε is a role, not one universal number

Keep distinct unless a later theory constructs a relationship:

- nilpotent tangent ε, such as `ε² = 0`;
- ordered infinitesimal;
- finite numerical tolerance;
- machine-rounding enclosure;
- local perturbation parameter;
- unresolved model branch;
- unidentified nuisance direction;
- sampling uncertainty;
- measurement uncertainty;
- an unknown resolution scale;
- a placeholder for an unenumerated alternative;
- an interaction region produced by several uncertainties;
- a deliberately hidden or distorted information channel.

The notation may be shared because it is suggestive. The types and laws must not be shared by default.

## Unknown containment

Containment such as

```text
((•))
```

may mean that one unresolved object is visible only inside another context, model, scale, experiment, or language. More deeply nested forms need not be reducible to a fixed-depth inductive tree.

Research questions:

1. Is containment literal subset inclusion, contextual availability, refinement, conditioning, localization, or something else?
2. Does opening an outer context reveal the inner object, alter it, or merely make a question meaningful?
3. Can two containment hierarchies overlap without either containing the other?
4. Is depth data, a proposition, an inaccessible fact, or itself uncertain?
5. Can the representation admit “an unknown number of unknown inner regions” without fabricating a finite list?

No answer is selected here.

## Interaction among ε-regions

Two uncertainty regions may:

- overlap;
- exclude each other;
- share a latent source;
- constrain one another algebraically;
- combine only after a basis or coordinate choice;
- interact through a nonlinear model;
- merge under coarse observation and separate under fine observation;
- change the questions that are meaningful;
- interfere strategically because evidence is selected or withheld.

Do not multiply confidence scores or add error bars merely because two sources are present. Interaction needs an explicit operation and explicit assumptions.

## Resolution conditions

A resolution condition is not necessarily “collect more data.” It may be:

- perform a specified experiment;
- improve measurement resolution;
- identify a calibration;
- choose between model classes;
- observe a variable currently latent;
- change basis or representation;
- prove an implication;
- establish a causal intervention;
- obtain access to withheld records;
- discover that the question was malformed;
- learn that no finite observation can distinguish the alternatives.

The system must be able to record that the resolution condition is unknown, unavailable, impossible, contested, or manipulable.

## Propaganda and marketing

Incomplete knowledge is not always passive. A source may strategically shape:

- which alternatives are named;
- which evidence is shown;
- the apparent scale of uncertainty;
- the baseline or comparison class;
- the framing of a question;
- what counts as resolution;
- which nested context is visible;
- whether one ε-region is presented as if it exhausted all uncertainty.

This requires provenance and agency, not merely a wider numerical interval. The system should distinguish uncertainty in the world from uncertainty manufactured in the report.

## Crisp and smooth local patches

A one-dimensional interval gives a crisp membership region. Other local knowledge shapes may be smoother or basis-dependent:

```text
center
frame / basis
profile
scale or quadratic form
support or level-set convention
transport map
provenance
```

A Gaussian-shaped patch is one useful model of smooth localization, but “Gaussian” must not automatically mean a calibrated probability distribution. It may be a kernel, weighting profile, local chart, approximation, or visual/analytic device.

Possible operations include restriction, overlap, pullback, pushforward, convolution, thresholding, change of basis, and tensoring. Each needs its own meaning. Straight scalar multiplication is not the universal model for combining patches.

## Category-theoretic questions

Category theory may help by forcing distinctions among:

- objects of knowledge;
- maps that transform or forget information;
- refinement and localization;
- products versus tensor products;
- pullbacks of compatible evidence;
- pushforwards through models;
- sections over contexts;
- gluing and obstruction;
- change of basis and naturality;
- quotients that identify observationally indistinguishable states.

The goal is not abstraction for its own sake. The test is whether the structure prevents a false collapse and exposes which information an operation preserves or destroys.

## Relation to statistical work

Econometrician-in-a-Box owns the eventual relation between this open-ended structure and concrete statistical objects:

- observations and acquisition history;
- sampling design;
- estimands and model classes;
- likelihoods, priors, confidence procedures, and identification regions;
- Jacobians, covariance, nonlinear propagation, and bootstrap dependence units;
- contradictory or strategically selected evidence;
- reports that preserve unresolved alternatives rather than manufacturing one scalar answer.

A statistical method may consume a resolved slice of the ε-structure. It must not claim to have resolved the whole structure merely because it returned a number.

## Research leads, not adopted foundations

Relevant material to inspect includes:

- Anders Kock and the Kock–Lawvere approach to synthetic differential geometry;
- John L. Bell’s work on smooth infinitesimal analysis and alternative continua;
- sheaf/topos language for context-dependent local information;
- affine arithmetic and dependency tracking;
- interval, set-identification, possibility, evidence, and imprecise-probability theories;
- Gerald Jay Sussman and Jack Wisdom’s operation-first computational differential geometry, especially bases, forms, tensors, and coordinate independence.

These are sources of counterexamples and vocabulary. None is declared the final ontology.

## Non-goals for the first implementation

Do not begin by:

- defining `Uncertainty = Interval Number`;
- choosing one probability distribution;
- assigning a scalar confidence to every ε;
- fixing a maximum nesting depth;
- assuming a tree when overlaps are possible;
- treating unknown resolution as failure;
- normalizing all evidence into one posterior;
- hiding propaganda/selection effects in a generic provenance string;
- claiming that a finite algebraic data type exhausts unknown unknowns.

## First durable artifacts

Before implementation, preserve:

1. forcing examples that defeat intervals, distributions, finite trees, and flat provenance;
2. a vocabulary of ε roles without identifying them;
3. examples of known, unknown, impossible, and strategically blocked resolution conditions;
4. examples of nested and overlapping contexts;
5. explicit statements of what each candidate formalism erases;
6. a comparison between crisp regions, smooth patches, basis-bearing patches, and probabilistic objects;
7. only then, small typed experiments with honest `OPEN` and `NOT_VERIFIED` labels.
