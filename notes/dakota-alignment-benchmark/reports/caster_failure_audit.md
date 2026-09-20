# Dakota caster estimate failure audit

Date: 2026-09-20

This report reconstructs the materially different caster results preserved in
conversation history, repository history, PRs/issues, and generated artifacts.
The row-level ledger is
[`data/caster_failure_ledger.csv`](../data/caster_failure_ledger.csv).

## Evidence limit

The complete original transcript corpus is not available. The audit recovered
timestamped turns and later context, but some historical bootstrap material,
the exact seven-road-wheel-angle metrology table, and the corrected canonical
Sep 12 passenger table remain missing. Missing details are marked missing; they
are not inferred from later prose.

The later Sep 16 reset sweep was absent from PR #5 even though its raw ordered
values survived in conversation history. It is now preserved as G5 in
`../dakota-caster-scalar-slice/g5_reset_sweep.csv`.

## Chronology and the exact failure transition

| Ledger | Result | Arithmetic/model status | Exact transition that failed |
|---|---|---|---|
| H-001 | legacy RF 5.1° | source calculation unrecovered | A later reconstruction treated a remembered result and an unrecovered bootstrap as analyzable evidence. The original data, resampling unit, and outputs are missing. |
| H-002 | driver 12.029°, passenger 6.015° | arithmetic correct for stated inputs | Driver `+0.5°` was transcribed as `+5°`. The 17.4:1 nominal conversion came from the manual and was not the cause of this failure. |
| H-003 | driver 5.095°, passenger 5.661° | nominal arithmetic correct | Correcting `+5` to `+0.5` repaired the gross result. The remaining limitation is that an overall manual ratio does not separately calibrate the two road wheels; passenger direction provenance also remained unresolved. |
| H-004 | driver 11.463°, passenger 5.661°, cross 5.80° | sensitivities/arithmetic correct | The bad `+5` returned, and one straight-ahead roll correction was carried through turned steering states. |
| H-005 | driver 7.63–9.75°; main fits 8.06–8.50° | code reproduces exactly | Conflicted transcription rows and an assumed per-wheel map built from the valid overall ratio entered a robust fit. Huber weighting handled residuals, not row identity or shared systematic error. The fitted odd coefficient `B` was then discussed too much like physical caster. |
| H-006 | 4.900±0.864° / 3.920±0.745° | first-order calculation correct under assumptions | `0.25°` camber and `5°` angle scales were assumptions, not measured standard deviations. Shared calibration was computed separately but never integrated into one covariance. A symmetric local bar hid nonlinear asymmetry. |
| H-007 | G2 passenger 5.5688°, 5.6608°, 5.5236°; combined 5.5647° | nominal arithmetic and Jacobian correct | Close agreement across steering scales was read as stronger confirmation than warranted because every pair shared the same manual-derived conversion, equal-angle assumption, setup, and model. |
| H-008 | G4 driver 3.4805°, 3.5380–3.8918°, 2.5317°; combined 2.8772–2.9749°; later about 3.5±0.6° | pair arithmetic and recorded-input interval correct | The `±0.6` construction is not recoverable. Between-pair spread was a steering/model/path diagnostic, not independent sampling error. |
| H-009 | seven-row 3-D fit 2.440° / 1.821° with narrow shape envelopes | conditional fit reproducible | A model-search acceptance envelope was liable to be read as measurement uncertainty; the passenger source was still provisional. |
| H-010 | preferred 3.3° [2.8,3.7] / 2.7° [2.1,3.2] | qualitative model criticism useful | The interval rule and coverage meaning were not recorded. Model choice, full-lock rejection, and measurement uncertainty were mixed into one range. |
| H-011 | G5 driver half 3.474° vs full 4.925–5.276°; passenger half 1.390° vs full 2.111° | pair arithmetic reproducible | The assumed command-to-wheel map did not explain the change with steering scale. Both sides showed nearly the same half-to-full odd-signal ratio near three, so this is a shared input-map problem, not one bad camber read. |
| H-012 | 4.6±1.0° / 1.9±0.5° / cross +2.7±0.7° | stated weighted centers reproducible | A two-to-one weight toward the one-turn result and “practical” bars replaced a covariance or bounded-error calculation. Shared errors and cross-caster covariance were not specified. |

No major episode was primarily a calculator mistake. The recurring pattern was
correct arithmetic applied after a provenance, geometry, or uncertainty-model
mistake.

## What kept going wrong

### 1. A valid overall steering ratio was overextended into an exact per-wheel map

The manual-derived 17.4:1 overall ratio is a valid nominal input, not an
arbitrary guess. It gives `10.3448°`, `20.6897°`, and `31.0345°` for a half,
one, and one-and-a-half steering-wheel turns. The mistake was narrower: some
calculations treated that overall ratio, plus an assumed symmetric or
ideal-Ackermann split, as an exact calibration of each tire angle.

That distinction does **not** make a large angle uncertainty plausible. Ideal
Ackermann changes the one-turn multiplier by only about `0.6%` in the preserved
geometry. Reducing the G2 half-turn result from `5.5688°` to `3.5°` by steering
angle alone would require about `16.60°` per road wheel, equivalent to roughly
`10.84:1`, far from the manual's `17.4:1`. The old `+/-5°` exercise is therefore
retained only as a nonlinear stress test, not as a Dakota tolerance or error
bar.

The G5 sweep makes the failure visible without choosing a corrected angle map:

- driver odd camber grew from `0.625°` at half turn to about
  `1.75–1.875°` at one turn, a factor `2.8–3.0`;
- passenger odd camber grew from `0.250°` to `0.750°`, a factor `3.0`;
- the simple proportional command model predicts roughly a factor of two over
  this range.

That common bilateral pattern is stronger evidence for input-map/model error
than for independent gauge noise. It does not identify whether the cause is
rack/steering-arm geometry, compliance, steering-state body attitude,
hysteresis, or some combination.

### 2. Source rows and adjustment states were not kept immutable

This caused the 12° result directly and contaminated the 8° fit more subtly.
Specific failures were:

- `+0.5°` became `+5°`;
- Sep 10 passenger left/right labels conflict with the saved array order;
- driver half-left survives as `+0.25°`, `+1.25°`, and `-1°` in different
  reconstructions;
- driver full-right survives as script `-5°` and timestamped cramped
  `-6° to -6.5°`;
- Sep 10, Sep 11, Sep 12, and Sep 16 states were at times discussed together
  despite intervening cam moves, settling, and reset work.

This is why a statistically elaborate fit did not rescue H-005: the uncertain
object was row identity/state, not merely a residual magnitude.

### 3. A model output was mistaken for the physical estimand

The robust fit's odd coefficient `B`, the exact-3-D fit, and the later preferred
interior fit are three instances. Each can be a valid conditional diagnostic.
None becomes physical caster unless the steering map, source rows, state, and
model adequacy are established.

The old 8° result was not a bad Jacobian. It was a reproducible coefficient of
a model fed disputed rows and assumed geometry.

### 4. Error bars were invented, mislabeled, or undocumented

Four episodes produced numerical ranges that were easy to read as physical
uncertainty without a complete construction: H-006, H-008, H-010, and H-012.
Only H-006 has enough detail to reconstruct its arithmetic; its input sigmas
were illustrative. H-008's raw input interval is valid, but the later `±0.6`
is not reconstructable. H-010's “identification intervals” lack a reproducible
rule. H-012's “practical” bars lack covariance and coverage definitions.

### 5. Shared evidence was counted as more confirmation than it supplied

The three G2 symmetric pairs use different camber endpoints, but share steering
calibration, gauge/setup, state, and model. The G5 half/full pairs are from the
same sweep and share all of those sources. Driver and passenger also share the
steering command and much of the mechanism. Averaging or weighting those
results can reduce a justified independent read-noise component; it cannot
reduce the shared input-map or setup component.

H-012 is the clearest numerical instance. The two-to-one weight was not derived
from a covariance. Its cross-caster `±0.7°` cannot be recovered from the stated
driver/passenger bars without an undocumented covariance assumption.

### 6. Local linear propagation was used beyond a locally symmetric regime

At the G2 half-turn point, a deliberately extreme historical stress fixture
used

```text
theta = 10.3448275862 deg
C     = 5.5687987431 deg
```

With that `±5°` road-wheel stress radius and fixed camber difference, the
first-order Jacobian gives the symmetric interval

```text
[2.9065, 8.2311] deg.
```

Direct nonlinear propagation gives

```text
[3.7789, 10.7354] deg
= 5.5688 -1.7899/+5.1666 deg.
```

The upper tail is badly missed. This demonstrates a propagation failure mode;
it does not establish that `±5°` is a plausible input error. At the H-006
`22.5°` point the same issue is smaller but still visible: driver exact
`4.0607–6.2353°` rather than symmetric `4.8996±1.0322°` for the shared `±5°`
angle perturbation.

### 7. Straight-ahead reference corrections were carried across steering states

The user explicitly rejected treating contaminated straight-ahead camber as a
valid fixed reference. Later body-height work reinforced the same point:
reference attitude belongs in `b(delta)` and its projection into camber changes
with steering. A `46/49 in` cross-car split is evidence about that reference
state, not a constant correction that can be subtracted from every sweep row.

## Error-bar audit

| Result | Status of its reported uncertainty |
|---|---|
| H-001 legacy 5.1° | Impossible to reconstruct. |
| H-002/H-003/H-004 pair calculations | No error bar was calculated; presentation was more certain than the inputs allowed. |
| H-005 robust fit | No coefficient confidence interval. Per-row effective sigmas were illustrative weights; treating them as empirical uncertainty would be conceptually invalid. |
| H-006 4.90±0.86° / 3.92±0.74° | First-order propagation was arithmetically correct for independent assumed inputs, but the bars are not measured Dakota uncertainties and are too symmetric under the stated large angle scale. |
| H-007 5.5688° and nearby pairs | No numerical error bar. The refusal to collapse unresolved terms was correct. |
| H-008 G4 | The `3.5380–3.8918°` and `2.8772–2.9749°` ranges correctly propagate recorded input ranges. The conversational `±0.6°` is impossible to reconstruct. |
| H-009 exact-3-D shape envelopes | Correct only as conditional model-search envelopes; conceptually invalid if read as probability/error bars. |
| H-010 preferred intervals | Impossible to reconstruct as statistical or set-valued intervals; weaken to judgment ranges or discard. |
| H-011 G5 pairs | No error bar; disagreement is structural evidence, not a variance estimate. |
| H-012 weighted G5 summary | Conceptually invalid and impossible to reconstruct. |

## Jacobian audit

For the checked G2 passenger half-turn calculation,

```text
x = [theta_right, theta_left, gamma_right, gamma_left]
  = [10.3448275862, -10.3448275862, 0.5, 2.5] deg

C = |(gamma_right-gamma_left)
      /(sin(theta_right)-sin(theta_left))|
  = 5.5687987431 deg.
```

The analytic row is

```text
[-0.2662274832, +0.2662274832, -2.7843993716, +2.7843993716].
```

It matches centered finite differences. The first two entries have units
degrees of inferred caster per degree of road-wheel angle; the last two have
units degrees of inferred caster per degree of camber. The variable ordering
and signs are correct.

The modes are informative:

- common additive steering zero: `J·[1,1,0,0]=0` at this symmetric point;
- symmetric steering-magnitude error: `J·[1,-1,0,0]=-0.532455`, so it does not
  cancel;
- common additive camber zero: `J·[0,0,1,1]=0`;
- endpoint-differential camber error is amplified by `2.7844` per endpoint.

Successful reproduction of this row does not validate the road-wheel angles.

The 14×26 repository Jacobian also passes its derivative tests. Its rank 14 and
nullity 12 mean it is diagnostic, not invertible evidence for one suspension
state. Neither Jacobian caused the 8° or 12° episodes.

## Bootstrap/resampling audit

No recoverable historical bootstrap calculation supports any Dakota error bar.
The oldest mentioned dataset/output is missing. The later repository work
correctly warned that seven steering positions are designed points, not seven
IID draws.

The independent unit depends on the question:

- repeated gauge rereads at one unchanged state can estimate read repeatability;
- left/right endpoints form one derived pair, not two independent caster
  estimates;
- steering positions within one sweep are designed correlated observations;
- a complete sweep is a possible cluster only if repeated sweeps have genuinely
  independent setup/state realization;
- an adjustment state or measurement session may be the unit for between-state
  variation, but the current record has too few comparable units.

A bootstrap over individual steering positions would answer the wrong
question. A bootstrap over raw reads and an explicit gauge-repeatability model
would double-count that component if both cover the same variation.

## Which results survive

The following survive as conditional calculations, not calibrated physical
caster:

- G2 passenger raw readings E-024–E-030 and nominal symmetric magnitudes
  `5.5236–5.6608°`; the exact half-turn `5.5687987431°` and its Jacobian are
  strong arithmetic regression cases.
- G4 driver corrected same-session rows and nominal pair results `3.4805°`,
  `3.5380–3.8918°`, and `2.5317°`; the full-turn/input-range propagation is
  valid as a range.
- G5 raw reset-state sweep and its nominal pair table: driver `3.4805°`,
  `4.9532–5.3070°`, `3.2221°`; passenger `1.3922°`, `2.1228°`,
  `2.0714–2.3015°`.
- The G5 nominal raw-difference least-squares diagnostics now reproduce as
  driver `3.7185–3.8162°` and passenger `2.0371–2.1873°`. Their narrow width is
  only propagation of recorded row ranges, not total uncertainty.
- The qualitative findings that steering-scale response is inconsistent with
  the simple command map, full-lock behavior differs from interior behavior,
  and setup/path state matters.

No surviving evidence supports one current physical caster value or a valid
current cross-caster error bar.

## Results to discard or weaken

- Discard H-002's 12° and H-004's 11.46° driver results: both contain the
  `+0.5` to `+5` transcription failure.
- Discard H-005's 8°-class driver coefficient as vehicle caster; retain it only
  as a regression fixture.
- Weaken H-003 and H-007 to nominal-model magnitudes because actual road-wheel
  angles are missing.
- Weaken H-009 to a conditional model fit; its envelope is not an error bar.
- Discard H-010's interval labels unless their construction is recovered.
- Discard H-012's weighted estimates and all three practical bars.

## Machinery added because of these failures

`uncertainty.py` now adds:

- named Jacobians with input/output labels and units; covariance label order
  must exactly match the Jacobian (H-006/H-007 variable-order risk);
- source-identified covariance receipts preserving every contribution and its
  provenance (all undocumented-bar episodes);
- an explicit independence assertion before separate covariance sources may be
  added, plus rejection of duplicate covered effects (H-005/H-012);
- latent shared-systematic propagation so a common source is represented once
  and does not shrink with the number of pairs (H-007/H-012);
- generalized least-squares combination using the complete estimate covariance
  rather than arbitrary pair weights (H-012);
- observation identity checks for generation, adjustment state, side, sweep,
  and approach direction (H-002/H-005 and cross-generation mixing);
- nonlinear bounded propagation receipts with asymmetric intervals and an
  explicit statement of whether corner extrema are a complete bound or only a
  diagnostic envelope (H-006/H-007);
- resampling-plan validation that rejects designed steering positions as IID,
  records the independent group count, and refuses overlap with explicit error
  sources (H-001 and the later bootstrap proposal).

The legacy low-level heterogeneous propagation helper remains for the existing
benchmark. A final numerical error bar should use the named receipt path.

`caster/` now makes that receipt path executable outside chat in five
languages. The R and Haskell frontends read the same TSV observations and
uncertainty-source records. Ithon, Agda, and Idriç independently recompute the
G2 anchor and the regression invariants. The programs:

- preserve the manual-derived nominal angle while refusing to invent its
  uncertainty distribution (H-003/H-007);
- emit no `±` for G2 because no empirical covariance was supplied (H-007);
- label H-006's reproduced `0.863804°` propagation as illustrative, not a
  Dakota confidence interval (H-006);
- print both the linear and exact asymmetric nonlinear stress intervals
  (H-006/H-007);
- reject incompatible states, designed-position bootstrap units, and overlap
  between bootstrap variation and explicit measurement error (H-001/H-005);
- demonstrate that a shared systematic component does not shrink when three
  pair estimates are averaged (H-007/H-012).

## Unresolved

- Direct road-wheel angles at every steering state.
- Independent repeatability data separated from new setup/session variation.
- Gauge calibration/drift and contemporaneous body/reference attitude by
  steering state.
- A canonical Sep 12 passenger table and exact mapping of the `4.75°`
  correction.
- The original H-001 bootstrap data/output.
- A post-reset controlled pair of sweeps approached from both directions.
- A calibrated physical forward model linking cam moves, suspension state,
  road-wheel angle, and observed camber.

Those gaps prevent a corrected physical caster/error bar. The audit therefore
ends with conditional calculations and refusal, not a manufactured final
estimate.
