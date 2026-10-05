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

## Executed result — 2026-10-05

Validation source commit: `d9ae5db5fae7f2eee8e64effab12b58df825a8fd`.
This receipt is historical exact-source evidence; later receipt-only changes
do not turn it into another head's receipt.

| Probe | Core/handoff | Direct target | Meaning |
| --- | --- | --- | --- |
| RouteControl | exit 0 | native exit 0, stdout `X` | Closed direct-ELF route works |
| CheckedConstraint | exit 0 | native exit 0, stdout `C` | Reflexive equality checks; no acquisition claim |
| RawAcquisition | exit 0 | exit 1, `unsupported_call: Prelude.IO.prim__getStr` | First target blocker: external input unavailable |
| InputParsing | exit 0 | exit 1, `duplicate_definition: Prelude.EqOrd.==` | Checked artifact has colliding rendered instance names |
| SourceIdentity | exit 0 | same artifact collision | No accepted runtime identity comparison |
| FilePersistence | exit 0 | same artifact collision | No ordinary-file persistence execution |
| FiniteExpression | exit 0 | unsupported `prim__getStr` | Finite syntax checks; no external symbolic ingestion |
| ConstraintRejection | exit 1, `wrong_revision` equality mismatch | not run | Correct relationship-specific core rejection |
| FiniteNumerics | exit 1, `Undefined name Float32` | not run | Source floating capability still absent |
| ReportRendering | exit 0 | exit 1, unsupported text literal | No accepted target report renderer |

The equality-negative probe initially had a syntax error; that failure did not
qualify. Its corrected source was rerun and rejects specifically the attempted
`1 = 2` proof. An initial launcher module-path leak and utility-path collision
were likewise repaired and rerun before the above target results were recorded.
Neither infrastructure failure is a physical mutant rejection.

The first capability required to unblock ingestion is an implemented checked
text/input operation lowering `Prelude.IO.prim__getStr` to the maintained
target, with an explicit bounded-buffer/encoding/error contract. Acceptance
must feed distinct valid and invalid records through the generated executable
and verify their checked outcomes. It must not compile a source recognizer,
hand-write the application artifact, or evaluate the query in the backend host.
That does not alone supply the missing source-graph/file-store runtime. The
artifact's overloaded-name collisions also require compiler-owned unique
identities, preserving both `==String` and `==Integer` definitions; dropping
one duplicate would corrupt the checked program. These are larger maintained
compiler/runtime capabilities than a consumer wiring repair.

All required command forms were invoked from `/tmp`; see
[`command-receipt.md`](command-receipt.md). `preflight` exited 0. `build`,
`test`, `replay`, `verify-reload`, `constraint-effects`, `mutants`, and
`all --require-authority idric --fallback none` exited 2. Neither a store nor
an authoritative October 5 report was created. Invalidation, selective closure
loading, conditioning, finite physical inference and all twelve end-to-end
mutant groups remain NOT IMPLEMENTED / NOT RUN, not completed uncertainty
queries. `benchmark/reports/persistent_uncertainty_replay.md` is deliberately
absent because no authoritative result exists from which to generate it.

## Identities and trusted boundaries

The exact compiler wrapper and compiled compiler, backend source, handoff,
target ELF and runner digests are retained in
[`receipts/2026-10-05/`](receipts/2026-10-05/). Compiler version output is
`Idris 2, version 0.8.0-1b5176dc9`; the separately fetched owning git revision
is the Idriç pin above. Compiler execution uses pinned threaded Chez 10.4.1,
digest `ff5773dd215b54697128a3fd61266b60f5c580634758d61ce8bffa31640254ce`.
Chez is the compiler runtime, not the target application runtime.

Successful compiler support rebuilding and the compact diagnostic use the
existing Android NDK r27c host Clang 18.0.3 (`r522817c`), digest
`a871130d810536f7bb924c8aeaff57c66de27bed9b13d0ccafba25fdcc8bd02d`.
The verified current target is disposable x86-64 Linux, not either Android
device. No qualified ICK host executable was available; no stock compiler was
substituted in the accepted support/diagnostic build. Target controls use
direct backend emission without a C compiler, assembler or linker.

The initial upstream aggregate bootstrap failed while building unused RefC
support at missing `gmp.h`. It was not used as acceptance. Reusing the existing
Chez-only support selector completed the compiler bootstrap. The maintained
Grease selector in `caster/_/make_chez.grease` now expresses that same narrow
build integration and was parsed and checked with a recursive dry run.

Grease owner: `dilapidated-shed/grease`
`f19c94c6df18cddbdc1e81463e5bd689533e3c13`; its source gitlink and exercised
engine are `dilapidated-shed/oils`
`6d29702a10ea9eb72a43950554dbcd4174d07a89`. The actual source development
runtime reports Oils 0.37.0 on CPython 2.7.13, interpreter digest
`38feede1a06b4142d1df8878c10fb5d72b6429485607b0014189ddec5a1ec101`.
It is the real pinned Grease engine, not a Bash execution of `.grease` source.
The runtime build outputs are local/generated; tracked engine code is not
relabeled as a clean native Grease build. The backend's inherited Python-3
substrate is invoked with its own module path and only emits the checked
target controls; it performs no Dakota inference.

New probe source contains no holes, postulates, unsafe coercions, partiality
directives or totality assertions. The generated main wrapper contains the
inherited `PrimIO.unsafePerformIO` entry machinery, which the scalar backend
handles explicitly as part of its trusted IO/world-token boundary. File
primitives' foreign declarations in failed artifacts have not executed and
are not an accepted trusted file boundary. The controls establish neither
physical adequacy nor empirical identification.

## Separate regressions and source coverage

On the reconciled source tree, 17 root unit tests, 40 benchmark tests, legacy
scientific-field/text replay and 38 scalar/reconstruction tests passed.
The existing compact-number diagnostic reran through the real corrected CSV
and reached `report_complete`; its unsupported E5M3-to-zero experiment remains
diagnostic only. Numeric definitions pin:
`dilapidated-shed/ick@90c003e042fa967872ed3408c25c55ec59315b9b`.
Local required multilingual replay failed at unavailable R; R, Haskell, Agda
and Ithon were not provisioned locally. It cannot be called a passing complete
multilingual suite.

| Historical source | Tests | Multilingual |
| --- | --- | --- |
| `8534505239ee897a66e43ad77567392bdd0ed975` | [35660298141](https://github.com/bl4ckb4ll/econometrician/actions/runs/35660298141) | [35660298082](https://github.com/bl4ckb4ll/econometrician/actions/runs/35660298082) |
| `181964f52a09a3843b33e6a09a1cf9ab9e5433e7` | [35883055512](https://github.com/bl4ckb4ll/econometrician/actions/runs/35883055512) | [35883055815](https://github.com/bl4ckb4ll/econometrician/actions/runs/35883055815) |

All four run job logs were fetched separately and match their listed source
heads. Both test runs record 17/40/38 component tests. Both multilingual runs
record R/Ithon/Haskell/Agda/Idriç component acceptance. Their historical-to-draft
diff contains only the 112-line passenger rear-cam report. None of these runs
executes persistent physical inference or the separate structural/Float32 probes.

The existing public derivative inventory contains 40 manifest records, 87
evidence-ledger rows and 38 source-census rows. These counts are not a denominator
for the unavailable original corpus. Public source manifests/ledger and
reconstruction fragments, issues #84/#85 and the required historical owners
were inspected; private originals were not reinspected or uploaded. Their
existing provenance/coverage qualifications remain authoritative.

The October 5 fixture preserves fourteen versioned public-fragment records,
including separate September 22 and September 29 states. Historical corrections,
cam move/return events and ambiguous mappings remain in their existing ledgers
and reconstruction owners. No new executable source dispositions are claimed:
the persistent importer and conditioning engine do not exist yet. The new
fixture is supplemental input awaiting ingestion, not a second inventory.

## Completion boundary

Implemented and executed: reconciliation, capability probes, fail-closed
Grease gate, narrow compiler-build selector, versioned replay input and mandatory
exact-head workflow wiring. The workflow is configured on this draft; a
configuration is not an executed hosted receipt. Source acquisition through
the authoritative persistent Dakota result remains BLOCKED and U2 is incomplete.
