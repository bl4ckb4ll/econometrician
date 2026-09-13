# Curvature Jacobian status

**Result: the project-specific object was not recovered.**

Searches of the available Dakota artifacts, saved mathematical screenshots, and accessible repository records found:

- ordinary Jacobian/sensitivity discussion;
- the candidate sweep model and its first/second derivatives;
- a general nearest-curve inverse-sensitivity formula involving curvature;
- broader Gromov/curvature work in other branches.

They did **not** recover an equation, type, module, or note defining what this project called the “curvature Jacobian”: a Jacobian of curvature, a curvature-dependent Jacobian, a block first/second-order matrix, or another construction.

`src/dakota_benchmark/curvature.py` therefore implements the recovered scalar/second-derivative formulas and deliberately raises `CurvatureJacobianNotRecovered` for the project-specific definition. This is an acceptance failure, not an invitation to rename a convenient matrix.

To close the gap, recover the original note/code that first named the object or restate its domain/codomain and blocks explicitly. Only then should a numeric implementation be added and tested against Dakota interventions.
