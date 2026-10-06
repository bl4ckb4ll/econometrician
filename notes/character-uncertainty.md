# Character uncertainty

Status: design note, 2026-10-06. This revives an older character-uncertainty idea from the author's vlog; the exact old recording is not yet linked here.

## Companion notes

- [Idriç](https://github.com/isomorphisms/Idric/blob/Idriç/_/character-uncertainty.md)
- [ARM Thumb](https://github.com/fuego-ironworks/idric-arm-thumb/blob/main/_/character-uncertainty.md)
- [ICK](https://github.com/dilapidated-shed/ick/blob/main/docs/character-uncertainty.md)

## Statistical object

An observed character need not be treated as an exact categorical value. When data support it, the target is something like

$$
P(\text{intended character}\mid\text{observation},\text{visual context},\text{input geometry},\text{user/device context}).
$$

Before calibration, keep candidate sets, distances, ranks, and provenance as such. Do not manufacture probabilities from adjacency.

At least two different neighborhood structures must remain distinct:

1. **Visual/glyph neighborhood.** Lowercase `b p q d` can be close as shapes because of reflections/rotations and shared stem/bowl structure, especially when the marks are being treated primarily as shapes.
2. **Physical input neighborhood.** A mistargeted key or touch is close because of geometry, not appearance. One deliberately broad QWERTY neighborhood centered on `D` is

   ```text
   W E R
   S D F
   Z X C
   ```

   so `w e r s f z x c` can be plausible physical alternatives to an observed `d` without being visually similar.

On a phone, touch coordinates, key rectangles, layout, orientation, and per-user offset are richer observations than the final wrong-key label and should be retained when available.

## Preserve the source of uncertainty

A candidate record should retain:

- observed character;
- candidate intended character;
- evidence channel;
- raw distance/cost/rank or calibrated probability;
- font/layout/device/user context when relevant;
- provenance of any learned confusion model;
- whether the value is empirical, assumed, or only a structural neighborhood.

Visual and input-geometry channels should not be collapsed into one edit-distance-like number prematurely. If several channels are combined, record the model used to combine them. Do not multiply likelihoods unless the dependence assumptions are justified.

## Initial empirical objects

Useful data products include:

- confusion counts `observed × intended`;
- confusion matrices conditional on font, keyboard layout, device, or user class;
- touch-offset distributions in key-relative coordinates;
- visual-confusion graphs or distances for a specified rendering;
- posterior candidate rankings for an explicit context;
- downstream inference that carries character uncertainty rather than forcing an early single-character decision.

## Acceptance fixtures

Until data exist, these remain structural fixtures rather than measured probabilities:

- observed `d`, visual channel → `{b,d,p,q}` as a close family;
- observed `d`, QWERTY physical channel → the eight surrounding positions above;
- combining the channels preserves which candidate came from which evidence;
- no numeric probability appears merely because two characters are neighbors.

## Project boundary

Econometrician in a Box owns calibration, dependence, statistical combination, and evidence provenance. Idriç owns high-level typed semantics. ARM Thumb owns compact target representations and kernels. ICK owns the C/compiler-facing representation and lowering experiments.
