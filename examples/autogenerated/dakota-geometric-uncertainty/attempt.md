# Program attempt: `dakota-geometric-uncertainty`

Status: `PARTIAL`

## Purpose

This program is the executable type-and-invariant slice for the Dakota caster
uncertainty procedure.  It was produced while reconciling the active caster
audit with the user's sphere, rotation, Jacobian, nested-error, and robustness
requirements.  Its job is to prevent an error source from disappearing before
or during first-order propagation; it is not a replacement for the finite
trigonometric model or for the raw-evidence audit.

## Intended behavior

The program constructs tagged error sources, assigns each source exactly one
auditable disposition, checks that the source census is complete, represents
the three nested uncertainty levels without assuming symmetry or probability,
and verifies two exact three-dimensional rotation facts:

- an infinitesimal orientation perturbation `omega x n` is tangent to the
  sphere at `n`;
- rotation about the wheel normal lies in the first-order kernel.

It also checks that steering reversal negates an odd component and preserves an
even component.  It does not parse readings, choose among transcription
alternatives, evaluate sine/cosine, infer an error magnitude, or identify
physical caster independently of the steering-input model.

## Type-system sketch

### Values and domains

- raw-reading decisions: accept one value, retain alternatives, or reject an
  incompatible record;
- uncertainty kinds: stochastic covariance, shared systematic, bounded set,
  symbolic epsilon, discrete alternative, incompatible state, model
  discrepancy, and arithmetic rounding;
- propagation dispositions: propagated, cancelled at first order, retained
  symbolically, branched, or rejected as incompatible;
- nested levels `one`, `two`, and `three`, interpreted only through inclusion;
- exact integer samples of vectors in three-dimensional Euclidean space;
- odd and even steering-response samples.

### Types and signatures

```text
ErrorSource : Type
SourceReceipt : Type
account_for_every_source : List ErrorSource → List SourceReceipt → Bool
level_contained_in : UncertaintyLevel → UncertaintyLevel → Bool
cross : Vector3 → Vector3 → Vector3
infinitesimal_rotation : Vector3 → Vector3 → Vector3
is_tangent_at : Vector3 → Vector3 → Bool
reverse_steering : SteeringResponse → SteeringResponse
```

The intended finite numerical layer additionally needs:

```text
rodrigues : UnitVector3 → Angle Float32 → UnitVector3 → UnitVector3
gauge_projection : GravityFrame → UnitVector3 → Angle Float32
caster_observation : CommandModel → CasterState → GaugeState → Reading Float32
```

These signatures are design targets, not claims that the pinned compiler
already supplies `Float16`/`Float32` transcendental primitives or the dependent
unit-vector proof needed by that layer.

### Actions and effects

All census, containment, vector, parity, and receipt checks are pure.  `main`
only prints a deterministic conformance receipt.  Reading acquisition,
photograph/OCR handling, user confirmation, and persistence remain outside
this program.

### Laws, invariants, and errors

- every registered source ID occurs exactly once in the disposition receipt;
- duplicate or missing source IDs fail the completeness check;
- `one` is contained in `two`, and `two` in `three`;
- containment does not assert a center, radius, distribution, or symmetry;
- `n dot (omega cross n) = 0` exactly for integer samples;
- `n cross n = 0`, so axial spin is a first-order kernel direction;
- steering reversal changes the sign of the odd component but not the even
  component;
- a cancelled source remains present with disposition
  `cancelled_first_order` rather than being deleted.

### Runtime and backend boundary

The structural slice requires only current Idriç algebraic data, `Integer`,
lists, equality, and text output.  It targets the pinned Idriç compiler used by
the repository's caster workflow.  An Idriç implementation of the desired
physical numerical layer would need explicit `Float16` storage and `Float32`
sine/cosine/atan2 evaluation (or a checked fixed-point/interval alternative);
host `Double` is not an acceptable physical carrier.  The repository now has a
separate binary32 Haskell endpoint-pair path.  Long-decimal binary64
computations elsewhere in the branch remain regression oracles only.

## Idriç attempt

Source: `DakotaGeometricUncertainty.idric`

Numeric carrier probe: `Float32CasterProbe.idric`

Revision and compiler: repository-pinned Idriç revision
`a8c24b10c143e97f8b24fc90a929eeee1e8f0392`; the built compiler reports
`Idris 2, version 0.8.0-a8c24b10c`.

Commands (with the pinned checkout's `prelude`, `base`, `linear`, `network`,
`contrib`, and `test` TTC directories in `IDRIS2_PATH`, its `support` directory
in `IDRIS2_DATA`, and its Chez toolchain on `PATH`):

```text
build/exec/idris2 --check DakotaGeometricUncertainty.idric
build/exec/idris2 --output-dir <scratch-output> -o dakota-geometric-uncertainty DakotaGeometricUncertainty.idric
<scratch-output>/dakota-geometric-uncertainty
build/exec/idris2 --check Float32CasterProbe.idric
```

What the program tried to do: compile and run the exact structural checks, then
type-check the smallest honest `Float32` trigonometric boundary.

## Result or failure

`DakotaGeometricUncertainty.idric` type-checked, linked with the Chez backend,
and ran successfully. Its receipt was:

```text
receipt_version dakota-geometric-uncertainty-v1
implementation Idriç
status PASS
source_census PASS
nested_uncertainty_levels PASS
sphere_tangent_map PASS
axial_rotation_kernel PASS
odd_even_steering_reversal PASS
robust_intake_interface PASS
physical_numeric_carrier STRUCTURAL_ONLY_NO_DOUBLE
```

`Float32CasterProbe.idric` failed during type checking at its first physical
scalar declaration:

```text
Error: While processing type of physical_sine. Undefined name Float32.
Float32CasterProbe:6:17--6:24
```

The stock pinned bootstrap encountered an incidental host dependency while
installing the unused RefC support library: `gmp.h` was unavailable. The Chez
support, compiler, and required libraries were built without installing RefC
and were the artifacts used for the successful check above. No result is
attributed to the unavailable RefC backend.

## Fallback

None inside Idriç.  The binary64 implementations are retained as historical
cross-language regression oracles, and the separate Haskell binary32
endpoint-pair path is not misrepresented as an Idriç Float32 implementation or
as the complete finite three-dimensional kernel.

## Idriç language work exposed

First blocking capability: the pinned compiler has no `Float32` type name, so
the desired physical signature cannot yet be stated without an invalid alias to
`Double`.

Smallest plausible language change: add an explicit `Float32` primitive carrier
with Chez/backend representation, conversion and rounding semantics, and the
`sin`, `cos`, and `atan2` operations needed by the finite rotation/gauge map.
`Float16` storage/conversion can then be added as the narrower input carrier;
it need not be the transcendental evaluation type.

Acceptance test for that change: the probe type-checks without aliasing its
physical scalar to `Double`, and a Float32 caster kernel emits a receipt naming
its arithmetic-error source.

## Evidence boundary

The structural source type-checked, linked, launched, and emitted `PASS` for
all declared checks under the pinned Chez compiler. The Float32 probe failed at
name resolution exactly as recorded. No Idriç Float16/Float32 trigonometric
caster kernel, full-graph arithmetic-error bound, or new physical Dakota value
was produced. The repository's Haskell binary32 endpoint-pair path remains a
separate, narrower implementation.
