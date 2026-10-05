# Published-head command replay — 2026-10-05

Source revision: `14bf8a9152ee009fb9e911dcf1733ea37744c026`.
Every command ran from `/tmp`. This is capability/blocked-stage evidence, not persistent inference acceptance. Local-source and GitHub commit identities differ because connector publication preserved Git trees with new commit metadata; the mapping is in the pull-request description. No authoritative store or report exists.

## preflight

```text
/usr/bin/env PATH=/usr/local/bin:/usr/bin:/bin:/workspace/scratch/55c171ff5399/oils/bin:/workspace/scratch/6d14aa5b3867/tools/bin DAKOTA_COMPILER_ROOT=/workspace/scratch/658519a32229/Idric DAKOTA_COMPILER_REVISION=ef83e1627e0a8b84567ec1f461d3a85c26580019 DAKOTA_BACKEND_ROOT=/workspace/scratch/6d14aa5b3867/idric-x86 DAKOTA_BACKEND_REVISION=e185d326df5d63f93c7675cb51fde9a8cb4d3ce5 DAKOTA_RECEIPTS=/workspace/scratch/6d14aa5b3867/published-receipts /workspace/scratch/55c171ff5399/oils/bin/grease /workspace/scratch/6d14aa5b3867/econometrician-published/caster/check_persistent_uncertainty.grease preflight
exit_status=0
PASS preflight identities; application capabilities not yet accepted
```

## build

```text
/usr/bin/env PATH=/usr/local/bin:/usr/bin:/bin:/workspace/scratch/55c171ff5399/oils/bin:/workspace/scratch/6d14aa5b3867/tools/bin DAKOTA_COMPILER_ROOT=/workspace/scratch/658519a32229/Idric DAKOTA_COMPILER_REVISION=ef83e1627e0a8b84567ec1f461d3a85c26580019 DAKOTA_BACKEND_ROOT=/workspace/scratch/6d14aa5b3867/idric-x86 DAKOTA_BACKEND_REVISION=e185d326df5d63f93c7675cb51fde9a8cb4d3ce5 DAKOTA_RECEIPTS=/workspace/scratch/6d14aa5b3867/published-receipts /workspace/scratch/55c171ff5399/oils/bin/grease /workspace/scratch/6d14aa5b3867/econometrician-published/caster/check_persistent_uncertainty.grease build
exit_status=2
PASS preflight identities; application capabilities not yet accepted
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/scratch/6d14aa5b3867/idric-x86/backend/idric_x86.py", line 511, in call
    raise UnsupportedError("unsupported_call", name)
UnsupportedError: unsupported_call: Prelude.IO.prim__getStr
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/scratch/6d14aa5b3867/idric-x86/backend/idric_x86.py", line 192, in parse_checked_artifact_bytes
    raise ArtifactError(code, name)
ArtifactError: duplicate_definition: Prelude.EqOrd.==
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/scratch/6d14aa5b3867/idric-x86/backend/idric_x86.py", line 192, in parse_checked_artifact_bytes
    raise ArtifactError(code, name)
ArtifactError: duplicate_definition: Prelude.EqOrd.==
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/scratch/6d14aa5b3867/idric-x86/backend/idric_x86.py", line 192, in parse_checked_artifact_bytes
    raise ArtifactError(code, name)
ArtifactError: duplicate_definition: Prelude.EqOrd.==
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/scratch/6d14aa5b3867/idric-x86/backend/idric_x86.py", line 511, in call
    raise UnsupportedError("unsupported_call", name)
UnsupportedError: unsupported_call: Prelude.IO.prim__getStr
Error: While processing right hand side of wrong_revision. When unifying:
    the Nat 2 = the Nat 2
and:
    the Nat 1 = the Nat 2
Mismatch between: 1 and 0.

ConstraintRejection:5:18--5:22
 1 | module ConstraintRejection
 2 |
 3 | -- Expected core rejection: an unequal revision cannot receive Refl.
 4 | wrong_revision : (the Number 1) = (the Number 2)
 5 | wrong_revision = Refl
                      ^^^^

Error: While processing type of physical_sine. Undefined name Float32. 

FiniteNumerics:3:17--3:24
 1 | module FiniteNumerics
 2 |
 3 | physical_sine : Float32 → Float32
                     ^^^^^^^

                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/scratch/6d14aa5b3867/idric-x86/backend/idric_x86.py", line 383, in parse_expression
    raise UnsupportedError("unsupported_one_step_expression", text)
UnsupportedError: unsupported_one_step_expression: "unresolved source revision: "
probe	core_handoff_exit	backend_exit	execution
RouteControl	0	0	PASS_CLOSED_CONTROL
RawAcquisition	0	1	NOT_RUN
InputParsing	0	1	NOT_RUN
SourceIdentity	0	1	NOT_RUN
FilePersistence	0	1	NOT_RUN
FiniteExpression	0	1	NOT_RUN
CheckedConstraint	0	0	PASS_CLOSED_CONTROL
ConstraintRejection	1	NOT_RUN	NOT_RUN
FiniteNumerics	1	NOT_RUN	NOT_RUN
ReportRendering	0	1	NOT_RUN
BLOCKED persistent authority is not implemented: external input, finite source graph and file I/O require checked target support; closed controls do not pass acquisition
```

## test

```text
/usr/bin/env PATH=/usr/local/bin:/usr/bin:/bin:/workspace/scratch/55c171ff5399/oils/bin:/workspace/scratch/6d14aa5b3867/tools/bin DAKOTA_COMPILER_ROOT=/workspace/scratch/658519a32229/Idric DAKOTA_COMPILER_REVISION=ef83e1627e0a8b84567ec1f461d3a85c26580019 DAKOTA_BACKEND_ROOT=/workspace/scratch/6d14aa5b3867/idric-x86 DAKOTA_BACKEND_REVISION=e185d326df5d63f93c7675cb51fde9a8cb4d3ce5 DAKOTA_RECEIPTS=/workspace/scratch/6d14aa5b3867/published-receipts /workspace/scratch/55c171ff5399/oils/bin/grease /workspace/scratch/6d14aa5b3867/econometrician-published/caster/check_persistent_uncertainty.grease test
exit_status=2
PASS preflight identities; application capabilities not yet accepted
BLOCKED stage test has no accepted persistent Idriç executable; historical/oracle receipts cannot satisfy it
```

## replay --fixture oct05 --store /workspace/scratch/6d14aa5b3867/published-oct05-store --output /workspace/scratch/6d14aa5b3867/published-oct05-output.md

```text
/usr/bin/env PATH=/usr/local/bin:/usr/bin:/bin:/workspace/scratch/55c171ff5399/oils/bin:/workspace/scratch/6d14aa5b3867/tools/bin DAKOTA_COMPILER_ROOT=/workspace/scratch/658519a32229/Idric DAKOTA_COMPILER_REVISION=ef83e1627e0a8b84567ec1f461d3a85c26580019 DAKOTA_BACKEND_ROOT=/workspace/scratch/6d14aa5b3867/idric-x86 DAKOTA_BACKEND_REVISION=e185d326df5d63f93c7675cb51fde9a8cb4d3ce5 DAKOTA_RECEIPTS=/workspace/scratch/6d14aa5b3867/published-receipts /workspace/scratch/55c171ff5399/oils/bin/grease /workspace/scratch/6d14aa5b3867/econometrician-published/caster/check_persistent_uncertainty.grease replay --fixture oct05 --store /workspace/scratch/6d14aa5b3867/published-oct05-store --output /workspace/scratch/6d14aa5b3867/published-oct05-output.md
exit_status=2
PASS preflight identities; application capabilities not yet accepted
BLOCKED stage replay has no accepted persistent Idriç executable; historical/oracle receipts cannot satisfy it
```

## verify-reload --store /workspace/scratch/6d14aa5b3867/published-oct05-store

```text
/usr/bin/env PATH=/usr/local/bin:/usr/bin:/bin:/workspace/scratch/55c171ff5399/oils/bin:/workspace/scratch/6d14aa5b3867/tools/bin DAKOTA_COMPILER_ROOT=/workspace/scratch/658519a32229/Idric DAKOTA_COMPILER_REVISION=ef83e1627e0a8b84567ec1f461d3a85c26580019 DAKOTA_BACKEND_ROOT=/workspace/scratch/6d14aa5b3867/idric-x86 DAKOTA_BACKEND_REVISION=e185d326df5d63f93c7675cb51fde9a8cb4d3ce5 DAKOTA_RECEIPTS=/workspace/scratch/6d14aa5b3867/published-receipts /workspace/scratch/55c171ff5399/oils/bin/grease /workspace/scratch/6d14aa5b3867/econometrician-published/caster/check_persistent_uncertainty.grease verify-reload --store /workspace/scratch/6d14aa5b3867/published-oct05-store
exit_status=2
PASS preflight identities; application capabilities not yet accepted
BLOCKED stage verify-reload has no accepted persistent Idriç executable; historical/oracle receipts cannot satisfy it
```

## constraint-effects

```text
/usr/bin/env PATH=/usr/local/bin:/usr/bin:/bin:/workspace/scratch/55c171ff5399/oils/bin:/workspace/scratch/6d14aa5b3867/tools/bin DAKOTA_COMPILER_ROOT=/workspace/scratch/658519a32229/Idric DAKOTA_COMPILER_REVISION=ef83e1627e0a8b84567ec1f461d3a85c26580019 DAKOTA_BACKEND_ROOT=/workspace/scratch/6d14aa5b3867/idric-x86 DAKOTA_BACKEND_REVISION=e185d326df5d63f93c7675cb51fde9a8cb4d3ce5 DAKOTA_RECEIPTS=/workspace/scratch/6d14aa5b3867/published-receipts /workspace/scratch/55c171ff5399/oils/bin/grease /workspace/scratch/6d14aa5b3867/econometrician-published/caster/check_persistent_uncertainty.grease constraint-effects
exit_status=2
PASS preflight identities; application capabilities not yet accepted
BLOCKED stage constraint-effects has no accepted persistent Idriç executable; historical/oracle receipts cannot satisfy it
```

## mutants

```text
/usr/bin/env PATH=/usr/local/bin:/usr/bin:/bin:/workspace/scratch/55c171ff5399/oils/bin:/workspace/scratch/6d14aa5b3867/tools/bin DAKOTA_COMPILER_ROOT=/workspace/scratch/658519a32229/Idric DAKOTA_COMPILER_REVISION=ef83e1627e0a8b84567ec1f461d3a85c26580019 DAKOTA_BACKEND_ROOT=/workspace/scratch/6d14aa5b3867/idric-x86 DAKOTA_BACKEND_REVISION=e185d326df5d63f93c7675cb51fde9a8cb4d3ce5 DAKOTA_RECEIPTS=/workspace/scratch/6d14aa5b3867/published-receipts /workspace/scratch/55c171ff5399/oils/bin/grease /workspace/scratch/6d14aa5b3867/econometrician-published/caster/check_persistent_uncertainty.grease mutants
exit_status=2
PASS preflight identities; application capabilities not yet accepted
BLOCKED stage mutants has no accepted persistent Idriç executable; historical/oracle receipts cannot satisfy it
```

## all --require-authority idric --fallback none

```text
/usr/bin/env PATH=/usr/local/bin:/usr/bin:/bin:/workspace/scratch/55c171ff5399/oils/bin:/workspace/scratch/6d14aa5b3867/tools/bin DAKOTA_COMPILER_ROOT=/workspace/scratch/658519a32229/Idric DAKOTA_COMPILER_REVISION=ef83e1627e0a8b84567ec1f461d3a85c26580019 DAKOTA_BACKEND_ROOT=/workspace/scratch/6d14aa5b3867/idric-x86 DAKOTA_BACKEND_REVISION=e185d326df5d63f93c7675cb51fde9a8cb4d3ce5 DAKOTA_RECEIPTS=/workspace/scratch/6d14aa5b3867/published-receipts /workspace/scratch/55c171ff5399/oils/bin/grease /workspace/scratch/6d14aa5b3867/econometrician-published/caster/check_persistent_uncertainty.grease all --require-authority idric --fallback none
exit_status=2
PASS preflight identities; application capabilities not yet accepted
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/scratch/6d14aa5b3867/idric-x86/backend/idric_x86.py", line 511, in call
    raise UnsupportedError("unsupported_call", name)
UnsupportedError: unsupported_call: Prelude.IO.prim__getStr
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/scratch/6d14aa5b3867/idric-x86/backend/idric_x86.py", line 192, in parse_checked_artifact_bytes
    raise ArtifactError(code, name)
ArtifactError: duplicate_definition: Prelude.EqOrd.==
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/scratch/6d14aa5b3867/idric-x86/backend/idric_x86.py", line 192, in parse_checked_artifact_bytes
    raise ArtifactError(code, name)
ArtifactError: duplicate_definition: Prelude.EqOrd.==
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/scratch/6d14aa5b3867/idric-x86/backend/idric_x86.py", line 192, in parse_checked_artifact_bytes
    raise ArtifactError(code, name)
ArtifactError: duplicate_definition: Prelude.EqOrd.==
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/scratch/6d14aa5b3867/idric-x86/backend/idric_x86.py", line 511, in call
    raise UnsupportedError("unsupported_call", name)
UnsupportedError: unsupported_call: Prelude.IO.prim__getStr
Error: While processing right hand side of wrong_revision. When unifying:
    the Nat 2 = the Nat 2
and:
    the Nat 1 = the Nat 2
Mismatch between: 1 and 0.

ConstraintRejection:5:18--5:22
 1 | module ConstraintRejection
 2 |
 3 | -- Expected core rejection: an unequal revision cannot receive Refl.
 4 | wrong_revision : (the Number 1) = (the Number 2)
 5 | wrong_revision = Refl
                      ^^^^

Error: While processing type of physical_sine. Undefined name Float32. 

FiniteNumerics:3:17--3:24
 1 | module FiniteNumerics
 2 |
 3 | physical_sine : Float32 → Float32
                     ^^^^^^^

                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/scratch/6d14aa5b3867/idric-x86/backend/idric_x86.py", line 383, in parse_expression
    raise UnsupportedError("unsupported_one_step_expression", text)
UnsupportedError: unsupported_one_step_expression: "unresolved source revision: "
probe	core_handoff_exit	backend_exit	execution
RouteControl	0	0	PASS_CLOSED_CONTROL
RawAcquisition	0	1	NOT_RUN
InputParsing	0	1	NOT_RUN
SourceIdentity	0	1	NOT_RUN
FilePersistence	0	1	NOT_RUN
FiniteExpression	0	1	NOT_RUN
CheckedConstraint	0	0	PASS_CLOSED_CONTROL
ConstraintRejection	1	NOT_RUN	NOT_RUN
FiniteNumerics	1	NOT_RUN	NOT_RUN
ReportRendering	0	1	NOT_RUN
BLOCKED persistent authority is not implemented: external input, finite source graph and file I/O require checked target support; closed controls do not pass acquisition
```

