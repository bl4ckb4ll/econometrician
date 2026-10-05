# Persistent Dakota uncertainty: checked target attempt

Status: BLOCKED; no authoritative physical report or acceptance claimed.

## Type sketch before implementation

An observation binds a stable source revision, instrument, calibration epoch,
mounting episode, physical configuration, body/support state, steering command,
optional road-yaw evidence, units, frame, sign and acquisition group. Unknown
bindings inhabit supported alternatives. An empirical reading with no supplied
uncertainty stays unresolved; an exact definition has a separate constructor.

`SourceRevision` and accepted `Observation` constructors must remain private.
Validation receives raw text and returns a diagnosed rejection or a checked
observation. An identity resolution produces a new revision, never edits the
old record. Dependency closures retain shared identities and cancelled sources.

Finite expressions contain exact rational literals, versioned unknowns, sums,
products, trigonometric maps and constrained discrete branches. Their products
are ordinary finite products, not either formal differential algebra in
`epsilon.py`. Conditioning intersects supported relations without inventing
error scales. A derived result records its map revision, branch, operating
state, coordinate order, units, source closure and result revision.

The intended central operations are:

```text
validate_acquisition : RawRecord → Either Rejection Observation
load_closure : Store → RequestedRevision → IO (Either StoreFailure SourceClosure)
condition : SourceClosure → Constraint → Either Conflict ConditionedClosure
infer : ConditionedClosure → Query → InferenceResult
revise_source : Store → SourceCorrection → IO (Either StoreFailure Invalidation)
render_report : CurrentResult → Report
```

`CurrentResult` must only be obtainable after closure/version validation.
`InferenceResult` distinguishes an identified expression, feasible witness,
certified enclosure, infeasible branch, unresolved direction and solver failure.
Totality proves only encoded relationships. File-system operations, numerical
primitive implementations and source fidelity remain explicit trusted boundaries.

## Chosen capability route

Core: `isomorphisms/Idric`, `Idriç`,
`ef83e1627e0a8b84567ec1f461d3a85c26580019`.
Backend: `fuego-ironworks/idric-x86-aggressive-backend`,
`e185d326df5d63f93c7675cb51fde9a8cb4d3ce5`.

The production candidate is checked source → compiler-owned one-step form →
direct x86-64 ELF → Linux execution. Chez builds/runs the compiler only; it is
not an application execution fallback. No generated C or RefC route is accepted.
The backend's existing Python implementation is a foreign compiler substrate,
not a new consumer oracle and not an authoritative Dakota computation.

The pinned backend documents a closed scalar/one-byte-output surface. It lacks
external input, strings, heap values, recursion, arbitrary-precision integers,
and ordinary-file I/O. Its small-scalar target primitives are separate from the
checked-source handoff. Tests below must establish actual failures, not infer
capability from the style declaration or target primitive presence.

## Probes and evidence

`probes/` keeps minimal programs for input validation, stable source identity,
ordinary-file persistence, finite symbolic products, checked relationships,
Float32 operations and report rendering. `RouteControl` distinguishes a broken
compiler from a meaningful target limitation. `ConstraintRejection` deliberately
violates an equality and must be rejected for that relationship.

Each probe must retain core-check, handoff, lowering, executable and runtime
evidence separately. A rejected capability is BLOCKED, never a passing physical
mutant. The complete query and the twelve acquisition-to-report mutant groups
remain unexecuted until the necessary capability route exists.

## Reused owners

The reconciled integration commit retains PR #5's named Jacobians, source
loadings, overlap and group-resampling safeguards, reduced 14×26 oracle,
scalar/reconstruction chronology, source/census/failure ledgers, multilingual
kernels and structural example. Main's corrected CSV and compact-number
experiment remain unchanged. ASE's implicit equilibrium/curvature formulation
is retained as mathematical reference, not a calibrated truck model.

## Fallback

None for the authoritative answer. Existing regression oracles retain their
separate evidence labels. No report is emitted as current merely because a
closed structural probe checks or runs.
