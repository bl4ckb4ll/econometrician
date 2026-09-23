# Dakota caster reconstruction, 22 September 2026: evidence-fusion failure receipt

This note preserves the 22 September 2026 caster reconstruction and, more importantly, records why its uncertainty envelope was not acceptable as a physical uncertainty statement.

The numerical exercise found a central finite-geometry fit near:

| Quantity | Central fit from the 22 Sep reconstruction |
|---|---:|
| Driver caster | +2.95° |
| Passenger caster | +1.46° |
| Driver minus passenger | +1.49° |

The passenger value near +1.5° was qualitatively consistent with the small passenger-side camber spread through the steering sweep. The problem was not primarily the center. The problem was the very broad profile envelope that was then reported:

| Quantity | Reported stress envelope |
|---|---:|
| Driver caster | about +1.0° to +4.7° |
| Passenger caster | about +0.1° to +2.7° |
| Cross-caster | about -0.7° to +3.2° |

Those ranges were produced by admitting uncertainty families that contradicted or ignored information already available from the physical experiment. They are therefore a useful failure case for Econometrician in a Box: the machinery conserved named uncertainty sources, but it did not yet conserve all of the evidence that constrained those sources.

## Current sweep used in the reconstruction

The post-reset sweep was recorded at seven steering positions:

| Steering command | Driver camber | Passenger camber |
|---|---:|---:|
| Maximum left | +0.75° to +1.0° | +2.5° to +2.75° |
| One turn left | -0.75° | about +2.75° |
| Half turn left | -2.5° | +3.0° |
| Straight | -3.0° | +3.0° |
| Half turn right | about -3.25° | about +3.75° |
| One turn right | -3.25° to -3.0° | +4.0° |
| Maximum right | -2.5° | +4.0° |

The reconstruction used a finite three-dimensional steering-axis model rather than identifying the odd camber coefficient directly with caster. With s=+1 on the driver side and s=-1 on the passenger side, it represented the steering axis as

    a proportional to (-tan(C), -s*tan(I), 1)

and the outward wheel normal at road-wheel yaw delta and camber gamma as

    n = (-s*cos(gamma)*sin(delta),
          s*cos(gamma)*cos(delta),
         -sin(gamma))

Rigid rotation preserves the dot product a·n, giving the finite observation equation

    sin(gamma)
      + [tan(I)*cos(delta) - s*tan(C)*sin(delta)]*cos(gamma)
      = sin(gamma0) + tan(I)*cos(gamma0)

A shared parameter interpolated between equal left/right wheel angles and ideal Ackermann geometry. The least-squares center was approximately +2.95° driver and +1.46° passenger.

That calculation remains useful as a numerical reconstruction. What follows explains why its broad "uncertainty" envelope should not be treated as a physical result.

## Failure 1: a stress range was substituted for steering-ratio uncertainty

The manual-derived overall steering ratio is 17.4:1. In the failed profile, the nominal map was multiplied by a common factor from 0.9 to 1.1, and an even broader alternative family allowed half-turn, one-turn, and lock angles to move over wide independent ranges.

That was not justified by the available evidence. A ±10% scale change was a stress test, not a plausible uncertainty statement for a documented mechanical steering ratio. The user explicitly rejected that interpretation: a one- or two-percent discrepancy might be plausible; ten percent is not.

The model must distinguish:

- a manufacturer/manual nominal value;
- a calibration tolerance around that value;
- path-dependent linkage/Ackermann/model discrepancy;
- a deliberately exaggerated stress test.

Those are not interchangeable. A stress test may be useful diagnostically, but it must not widen the physical feasible set unless evidence supports that magnitude.

The earlier PR #5 work correctly said that 17.4:1 is the authoritative nominal input and that no numerical tolerance should be invented. The 22 September reconstruction violated the spirit of that rule by introducing a ±10% profile family anyway.

## Failure 2: measured body attitude was reopened as a free latent error

The broad envelope additionally allowed a shared body-roll term of ±0.36° at each nonstraight steering position. That scale came from a historical corner-height sensitivity exercise.

For the current experiment, however, body attitude was not simply an unknown nuisance parameter. It had been physically checked with a ruler/leveling procedure. Earlier reference work included a 46/49 inch cross-car test over roughly 72 inches and a return to equal 47.5/47.5 inch endpoints; the user also explicitly states that the body-attitude uncertainty for this sweep was removed by the ruler measurement.

Once a nuisance quantity is measured, the model must condition on that measurement and propagate the measurement's actual resolution/error. It must not silently replace the observation with a generic ±0.36° latent roll family.

This is a central Econometrician-in-a-Box requirement:

> Evidence that resolves an uncertainty source must shrink or transform that source. The source cannot remain in the final uncertainty budget merely because it appeared in an earlier census.

If a ruler observation leaves only reading resolution, placement error, or a known reference transformation, those specific residual sources should be propagated. A generic free body-roll parameter is no longer the right object.

## Failure 3: the estimator treated the current sweep too much like an isolated dataset

The truck has a history of discrete physical interventions. The caster/camber state was not drawn from an unconstrained parameter space on 22 September.

Available historical evidence includes:

- repeated seven-position camber sweeps under earlier cam configurations;
- marked eccentric/cam positions and photographs of those positions;
- known front-versus-rear eccentric roles;
- discrete cam movements, including one-flat and half-turn experiments;
- the fact that the rear cam had just been returned to the intended state before this sweep;
- driver/passenger spindle and lower-control-arm pivot height measurements;
- previous sweeps in which values near the factory-scale 3–4° region were obtained under nearby configurations;
- a known historical 8°-class result that had already been rejected as a provenance/model failure rather than accepted as physical caster.

Those observations constrain state transitions. They are not IID repeats, and they should not be pooled as though they were all measurements of one unchanged alignment. But the opposite mistake is also wrong: they cannot simply be discarded when inferring the current state.

The correct object is a state-space/intervention model:

    x[k+1] = F(x[k], u[k], eta[k])

where x[k] contains physical alignment state, u[k] is the recorded cam adjustment, and eta[k] is bounded mechanical/model discrepancy. Photographs and witness marks constrain u[k] and state identity. Previous sweeps constrain x[k]. The current sweep constrains x[k+1].

That history can rule out nominally algebraic solutions that would require an impossible change in caster for the recorded cam motion.

## Failure 4: photographs were treated mainly as provenance, not measurement constraints

The cam photographs and witness marks do more than identify which experiment occurred. Depending on image quality and camera geometry, they can provide:

- eccentric orientation;
- direction and approximate magnitude of cam rotation;
- confirmation that an adjustment was returned to a previous witness mark;
- exclusion of geometrically impossible adjustment histories.

The model should allow images to contribute interval or categorical constraints without pretending they are calibrated photogrammetry. For example:

- "rear eccentric returned to this witness mark" is a state-equality constraint with image/mark tolerance;
- "cam rotated clockwise by one flat" is an intervention constraint;
- "orientation lies between these two visible flats" is an angular interval;
- "image cannot resolve the direction" is a retained branch, not invented precision.

## Failure 5: instrument-side sign evidence was not integrated

The magnetic camber gauge has a perpendicular bubble. The user can directly observe which way that bubble moves when the gauge indicates positive or negative camber.

That observation is valuable. It is a sign/calibration experiment on the measurement map. It can constrain:

- which gauge direction corresponds to positive camber;
- whether a proposed wheel-normal/gauge projection has the correct sign;
- whether an apparent left/right convention has been reversed;
- whether a fitted model is explaining data with an impossible instrument orientation.

Econometrician in a Box needs a first-class representation for this kind of qualitative-but-hard evidence. A sign observation is not soft background knowledge; it can eliminate half of a parameter space when the geometry is otherwise symmetric.

## Failure 6: physical impossibility and model disagreement were conflated with uncertainty

The user has repeatedly established that values near 0–1° or near 8° are not plausible for the present mechanical configuration. The 8° class had already appeared as a historical failure mode. The 22 September broad envelope nonetheless admitted passenger values near zero and driver values near one degree.

A model should not respond to conflict by widening a parameter interval until every algebraic possibility fits. It must ask which assumption is failing.

There are several distinct possibilities:

1. measurement uncertainty;
2. transcription alternatives;
3. calibration uncertainty;
4. state-transition uncertainty;
5. model discrepancy;
6. incompatible observations;
7. hard physical constraints;
8. deliberate stress tests.

If a solution requires violating established mechanical/state constraints, it should be marked incompatible with those constraints. The failure should attach to the model/evidence branch that caused the contradiction.

The factory specification around +3.5° is useful context and a diagnostic reference, but it should not simply be imposed as a prior that forces the answer. The stronger constraints are the actual measured/intervened state history and the physical geometry.

## Required evidence-fusion behavior

The goal is not merely "more error bars." It is a model that accepts heterogeneous evidence and updates the feasible state correctly.

A future caster reconstruction should ingest typed evidence such as:

| Evidence type | Example | Required treatment |
|---|---|---|
| direct numeric observation | camber reading | bounded/probabilistic observation model |
| manufacturer nominal | 17.4:1 steering ratio | nominal plus justified tolerance/model discrepancy |
| direct reference measurement | ruler/body attitude | condition on observation; propagate its resolution |
| sign calibration | perpendicular bubble direction | hard sign/orientation constraint |
| intervention | rear cam one flat outward | state transition with bounded response |
| image/witness mark | eccentric returned to mark | state identity/angular interval |
| prior configuration sweep | earlier seven-position sweep | prior-state observation, not IID current data |
| mechanical monotonicity | rear cam direction raises/lowers caster | inequality constraint |
| factory target | approximately +3.5° | reference/diagnostic, not automatically a hard prior |
| stress test | ±10% steering scale | diagnostic branch only, never mislabeled as physical uncertainty |

The inference should preserve both uncertainty and information. In set language, every new compatible measurement should intersect or transform the feasible set; it should not be possible for adding a ruler measurement to leave an arbitrary body-roll interval untouched.

In probabilistic language, every observed auxiliary measurement belongs in the joint likelihood or conditioning set. In optimization language, it becomes a constraint or penalty with explicit provenance. The implementation can support more than one representation, but it must not lose the distinction.

## Acceptance criteria for the next model

A replacement reconstruction should demonstrate all of the following on the Dakota history:

1. **Steering ratio discipline.** Start from the documented 17.4:1 nominal. Do not use ±10% as physical uncertainty without evidence. Support a tight user/manual-informed tolerance such as 1–2% as a scenario, with linkage nonlinearity represented separately.
2. **Measured attitude conditioning.** When ruler/level measurements are supplied, remove the corresponding free body-attitude nuisance parameter and propagate only the measurement's residual uncertainty.
3. **Configuration history.** Preserve every cam intervention as a state transition and every sweep as an observation of the corresponding state.
4. **Photographic constraints.** Permit witness-mark/cam photographs to constrain state identity and adjustment intervals without pretending to obtain more angular precision than the image supports.
5. **Instrument sign calibration.** Use the perpendicular-bubble observation to constrain the gauge projection/sign convention.
6. **No impossible widening.** If a result near 0–1° or 8° is only reachable by violating supplied physical/state constraints, report that branch as incompatible rather than including it in the final physical interval.
7. **Source-conserving uncertainty.** Retain shared/correlated/bounded/model errors distinctly, but do not retain an uncertainty source after a measurement has actually resolved it.
8. **State-aware cross-checks.** Use nearby previous configurations to constrain change, not as independent repetitions of the current state.
9. **Traceable rejection.** For every excluded branch, record which observation or physical constraint rejected it.
10. **Answer the physical question.** Produce current driver caster, passenger caster, cross-caster, and defensible bounds from the integrated evidence, rather than stopping at a list of unresolved sources when those sources have already been measured elsewhere in the record.

## What remains useful from the 22 September reconstruction

The central finite-geometry result of roughly **+3.0° driver / +1.5° passenger** remains a useful candidate reconstruction. The passenger center in particular is consistent with the small caster-sensitive camber spread visible through the current passenger sweep.

The failed broad envelope should be retained as a regression case. It demonstrates a general statistical lesson:

**uncertainty bookkeeping is not sufficient if the estimator fails to condition on all of the available evidence.**

The next Econometrician-in-a-Box model must be able to combine quantitative readings, physical measurements, intervention history, photographs, sign observations, manual specifications, and geometric constraints in one provenance-preserving inference.
