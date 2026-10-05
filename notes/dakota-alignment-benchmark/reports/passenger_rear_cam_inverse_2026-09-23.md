# Passenger rear-cam inverse calculation — 23 September 2026

Status: working physical calculation from the currently reconstructed notebook state sequence. This is not a factory degrees-per-flat specification and not a universal linear cam calibration.

## Current state

The current physical baseline is the **22 September sweep**. The rear passenger cam had been returned before that sweep. The user has now confirmed that the returned position is **near the rear eccentric's inward limit**.

For a simple auditable check, use the passenger one-turn pair from the current sweep:

- one turn left: about +2.75° camber
- one turn right: about +4.00° camber

With the documented 17.4:1 nominal steering ratio, the symmetric one-turn multiplier is approximately 1.4152, giving

```text
C_passenger,current ≈ 1.4152 * (4.00 - 2.75)
                    ≈ 1.77°
```

This is the current baseline for the inverse calculation.

The corresponding current driver one-turn pair gives approximately +3.2° to +3.5° caster, with a midpoint near +3.36°. Matching the passenger side to that current driver value is the working target used below.

## Earlier outward calibration state

A previous passenger state was measured after the **rear passenger cam was moved roughly 2–3 flats outward**. Its one-turn pair was approximately:

- one turn left: -0.125°
- one turn right: +3.50°

which gives

```text
C_passenger,outward ≈ 1.4152 * (3.50 - (-0.125))
                    ≈ 5.13°
```

That earlier state is **calibration evidence**, not the current truck state.

The sequence is therefore approximately

```text
rear cam near inward limit -> C ≈ 1.77°
rear cam 2–3 flats outward -> C ≈ 5.13°
rear cam returned near inward limit -> current state ≈ 1.77°
```

The return-to-baseline closure is important evidence that the large caster change tracks the rear-passenger cam intervention.

## The independent variable is eccentric angle

Do **not** use a constant degrees-of-caster-per-flat rule.

The earlier ~0.6°/flat number was an uncalibrated paper estimate. More importantly, a flat count is a finite rotation of an eccentric. The pivot displacement is nonlinear in cam angle.

Taking the returned near-inward-limit position as `phi = 0`, write the outward displacement coordinate as

```text
u(phi) ∝ 1 - cos(phi).
```

The observed caster change between the two measured states is

```text
Delta C_observed ≈ 5.13 - 1.77 = 3.36°.
```

Using the current driver midpoint target `C_target ≈ 3.36°`, the required fraction of the measured response is

```text
f = (3.36 - 1.77) / (5.13 - 1.77)
  ≈ 0.47.
```

This is a fraction of the **measured response / eccentric displacement**, not a fraction of the bolt rotation.

Solve

```text
1 - cos(phi_target)
  = f * [1 - cos(phi_outward)].
```

For the unresolved earlier move magnitude:

| Earlier outward state | Inferred move from current inward-limit state |
|---|---:|
| 2 flats = 120° | about 73° = 1.22 flats outward |
| 2.5 flats = 150° | about 83° = 1.39 flats outward |
| 3 flats = 180° | about 87° = 1.45 flats outward |

So the working inverse result is

```text
rear passenger cam: about 1.4 flats outward
                   about 84° bolt rotation
conditional branch: about 73–87° from the 2-vs-3-flat historical ambiguity
```

## What this result does and does not mean

- **Current state:** 22 September, rear passenger cam returned near its inward limit.
- **Earlier 5.13° state:** only a measured comparison state used to calibrate the finite response.
- **Target:** approximately the current driver caster, not an arbitrary factory number inserted into the inversion.
- **Independent variable:** eccentric angle / resulting pivot displacement.
- **Nonlinearity:** the cosine eccentric map is applied before interpolating the measured response.
- **Not claimed:** a universal 1.0–1.5° caster-per-flat derivative.
- **Not claimed:** that 84° is a factory setting or a precision alignment-machine result.
- **Required follow-up:** settle the suspension and repeat the same caster/camber sweep after the move; preserve the actual final cam angle/witness mark and do not replace it with the commanded wrench rotation.

This note should be read with the intervention-timeline and nonlinear-eccentric failure records. If the source pairing, cam identity, or earlier 2-vs-3-flat branch is corrected, this inverse result must be recomputed rather than patched by a linear correction.
