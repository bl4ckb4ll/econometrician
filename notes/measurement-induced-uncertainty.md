# Measurement-induced uncertainty in survey and choice data

This note records a statistical design concern that is separate from arithmetic
rounding and from the dyadic-number exploration.

## Sources

Primary source:

- V. I. Danilov and A. Lambert-Mogiliansky, **“Measurable Systems and
  Behavioral Sciences”**, *Mathematical Social Sciences* 55(3), 2008,
  315–340. Preprint: https://arxiv.org/abs/physics/0604051
- DOI: https://doi.org/10.1016/j.mathsocsci.2007.10.004

Closely related companion paper:

- A. Lambert-Mogiliansky, S. Zamir, and H. Zwirn, **“Type Indeterminacy:
  A Model of the KT(Kahneman–Tversky)-Man”**, *Journal of Mathematical
  Psychology* 53(5), 2009, 349–361.
  Preprint: https://arxiv.org/abs/physics/0604166
- DOI: https://doi.org/10.1016/j.jmp.2009.01.001

These are easy to conflate. The Danilov/Lambert-Mogiliansky paper is
*Measurable Systems and Behavioral Sciences*; the KT-man paper has Zamir and
Zwirn rather than Danilov as coauthors.

## Statistical point

The important idea for this project is not that human cognition is physically
quantum. The useful claim is operational:

> an elicitation procedure may be a state-changing measurement rather than a
> passive readout of a fixed scalar quantity.

The paper explicitly treats a questionnaire or decision situation as a
measurement device and the recorded answer or choice as its outcome. It allows
measurements to be incompatible: performing one measurement can alter the
distribution of outcomes for another, so order can matter.

That matters for survey data because the familiar model

```text
fixed latent value
  + sampling error
  + response noise
  -> recorded number
```

can be structurally wrong. The question, response scale, framing, preceding
questions, and act of answering may participate in producing the observed
response.

The paper's notion of state is also useful because it need not mean a hidden
number waiting to be discovered. Operationally, a state is what determines the
probability distributions of possible measurement outcomes and how those
predictions change after measurements. Even a pure or maximally informative
state need not determine every future response with certainty.

## Consequence for numeric precision

This is a different uncertainty layer from floating-point precision.

Low-precision arithmetic can be desirable because a long mantissa encourages
false numerical specificity. Binary16, or a deliberately defined binary8-like
format, may be enough for many reported or stored quantities. But reducing the
mantissa cannot represent the uncertainty described above.

Keep separate, when relevant:

1. arithmetic quantization and rounding;
2. sampling uncertainty;
3. ordinary response stochasticity;
4. scale/coarsening effects such as 1–3 versus 1–5 versus 1–10 responses;
5. framing and question-order effects;
6. measurement-induced state change / incompatible elicitation procedures;
7. model uncertainty about whether a stable latent scalar exists at all.

Do not collapse these into one generic epsilon merely because they can all make
a final number less trustworthy.

## Design status

Research/design note only. It does not establish that the Hilbert-space model
is the correct empirical model for a particular survey, and it does not imply a
physical quantum mechanism in the brain.

The durable requirement is weaker: econometrician should be able to represent
uncertainty and measurement effects without pretending that every observed
number is a precise readout of a fixed underlying scalar.
