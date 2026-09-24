# Ariane Lambert-Mogiliansky: contextual and non-classical uncertainty

Status: research note. This records a model family and its implications for
statistical intake and interpretation; it does **not** add a runtime method or
claim that a quantum-like representation is empirically required.

## Why this belongs here

A recurring econometric failure is to treat every uncertain response as a noisy
observation of one fixed latent scalar. Lambert-Mogiliansky's work develops a
different possibility: preferences or beliefs may be **contextual or
indeterminate**, so the act, question, or sequence used to elicit them can help
determine the state that is observed rather than merely reveal a pre-existing
value.

The mathematical machinery is quantum-like: events or questions need not admit a
single Boolean event algebra, incompatible observables can be noncommuting, and
updating can be represented by state change in a Hilbert-space model. That is a
formal model of contextual decision behavior, not a claim that brains are
physical quantum computers.

For an econometrician, the durable warning is broader than the particular
formalism:

- preserve question, treatment, and elicitation **order** when order can affect
  responses;
- do not automatically pool incompatible contexts as repeated noisy
  measurements of one fixed latent quantity;
- distinguish uncertainty from lack of information from indeterminacy induced
  or resolved by the measurement/choice context;
- do not call every post-question state change ordinary Bayesian conditioning
  when the model being considered makes the measurement itself state-changing;
- separate empirical evidence for order/context effects from the stronger choice
  of a Hilbert-space representation;
- treat persuasion or survey design as a possible intervention on the response
  process, not automatically as passive measurement.

This is especially relevant wherever inputs are human judgments, survey scales,
stated preferences, sequential choices, or beliefs whose meaning depends on the
questioning frame.

## Core sources

### Type indeterminacy

Ariane Lambert-Mogiliansky, Shmuel Zamir, and Hervé Zwirn,
"Type Indeterminacy: A Model for the KT (Kahneman-Tversky) Man" (2006).

- https://arxiv.org/abs/physics/0604166

The paper models preferences as potentially indeterminate before interaction,
with observed behavior produced in the act of choice. Its important statistical
consequence here is that "latent preference plus measurement noise" is not the
only coherent ontology for unstable answers.

### Expected utility under non-classical uncertainty

V. I. Danilov and Ariane Lambert-Mogiliansky,
"Expected Utility Theory under Non-Classical Uncertainty,"
*Theory and Decision* 68 (2010), 25-47.

- https://doi.org/10.1007/s11238-009-9142-6

This replaces the classical Boolean event structure with a non-classical event
structure and develops qualitative probability, expected utility, and belief
updating in that setting.

### Dynamic consistency

V. I. Danilov, Ariane Lambert-Mogiliansky, and Vassili Vergopoulos,
"Dynamic consistency of expected utility under non-classical (quantum)
uncertainty," *Theory and Decision* 84 (2018), 645-670.

- https://doi.org/10.1007/s11238-018-9659-7
- https://arxiv.org/abs/1708.08244

The paper distinguishes dynamic consistency from the classical recursive form
and relates conditional choice to a non-classical updating rule. For this
repository, it is a warning not to silently identify all sequential updating
with one classical conditional-probability mechanism.

### Belief preparation and persuasion

V. I. Danilov and Ariane Lambert-Mogiliansky,
"Preparing a (quantum) belief system," *Theoretical Computer Science* 752
(2018), 97-103.

- https://doi.org/10.1016/j.tcs.2018.02.017
- https://arxiv.org/abs/1708.08250

V. I. Danilov and Ariane Lambert-Mogiliansky,
"Targeting in quantum persuasion problem," *Journal of Mathematical Economics*
78 (2018), 142-149.

- https://doi.org/10.1016/j.jmateco.2018.04.005
- https://arxiv.org/abs/1709.02595

These papers make the measurement/intervention distinction especially sharp:
the sequence and choice of measurements can change reachable belief states.
That matters whenever an econometric workflow treats elicitation as if it were a
neutral readout.

### Experimental follow-up

Ariane Lambert-Mogiliansky and Adrian Calmettes,
"Phishing for (Quantum-Like) Phools—Theory and Experimental Evidence,"
*Symmetry* 13 (2021), 162.

- https://doi.org/10.3390/sym13020162

This gives an empirical follow-up to the persuasion line. It should be read as
evidence about particular predicted context effects, not as blanket validation
of every quantum-like decision model.

## Repository boundary

Nothing in this note licenses a generic "quantum correction" to data or an
automatic Hilbert-space fit. Before such a model could become an implemented
method, the data contract would need to preserve the relevant contexts and
sequences, the classical alternative would need to be stated, and the proposed
non-classical structure would need falsifiable acceptance cases.

Until then Lambert-Mogiliansky belongs here as a source for a distinct
uncertainty ontology and for the warning that the measurement process itself can
be part of the statistical object.
