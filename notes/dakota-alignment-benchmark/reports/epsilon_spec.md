# Edriç epsilon specification recovered from the record

## What is established

The current benchmark intent is an unresolved-tolerance object: `x + epsilon` means that a value is only known up to some tolerance whose magnitude or distribution has not been justified. The intended nilpotent relation includes

`epsilon_i^2 = 0`.

The recovered language-design patches separately show that a nilpotent/dual-number epsilon satisfying `epsilon^2=0` and an ordered Robinson nonstandard infinitesimal are **different objects**. The older parser/design material reserved epsilon syntax without assigning one universal semantics.

Therefore this Dakota epsilon is not automatically:

- Gaussian noise;
- a standard deviation;
- an interval;
- machine epsilon;
- an ordered infinitesimal;
- a precision weight.

Distinct unresolved errors remain distinct labels and no ordering is defined.

## Mixed products are not recovered

No recovered source settles whether `epsilon_i epsilon_j` for `i != j` vanishes. Choosing either convention changes second-order propagation, so the benchmark refuses a default.

`src/dakota_benchmark/epsilon.py` exposes two explicit algebras:

1. `square_free`: `epsilon_i^2=0`, while products of distinct labels can survive. Algebraically this resembles a commutative quotient by each individual square relation.
2. `first_order_ideal`: every product of two or more epsilon factors vanishes, i.e. the entire epsilon ideal squares to zero.

Any Edriç implementation consuming the benchmark must choose one explicitly or leave the expression uninterpreted.

## Boundary with physical curvature

Nilpotent epsilon arithmetic and physical second-order behavior answer different questions.

If a first-order uncertainty calculation uses an algebra with `I^2=0`, it intentionally discards second-order products of **the symbolic perturbation representation**. That does not imply the truck's suspension or measurement map has zero Hessian. Physical curvature can remain nonzero and be studied by an ordinary second-order expansion

`f(x+dx) = f(x) + J dx + 1/2 H[dx,dx] + ...`.

Code and documentation must keep those layers separate.
