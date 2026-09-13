# Evidence audit findings

## Status

This package is **not yet accepted as a reusable physical Dakota theory benchmark**. It is accepted as an audit package showing exactly what was recovered, what recomputes, and what remains blocked.

The strongest source limitation is itself documented in the prior audit: complete original mechanical conversation transcripts were not available there. This package supplements that material with recoverable conversation context, original images, generated files, and current repository evidence, but it does not pretend the missing transcript corpus has been restored.

## Highest-consequence findings

1. **The Sep10 passenger row order is conflicted.** The recovered timestamped verbal sequence runs maximum right `0°`, then `+0.25°`, `+0.5°`, straight `+1.125° to +1.25°`, `+2.5°`, `+4.25°`, maximum left `+6°`. The saved script labels its array `[0,0.25,0.5,1.125,2.5,4.25,6]` in the opposite left-to-right steering order. The old fit is therefore not a trustworthy physical caster result until the source mapping is rebuilt.
2. **A later passenger correction mentioning `4.75°` is not mapped to a unique row/generation.** It cannot simply overwrite the script's `4.25°`.
3. **The old script is internally reproducible.** Rerunning it reproduces the stored JSON byte-for-byte. That proves software repeatability only; its data mapping and illustrative error model remain disputed.
4. **Early caster is highly sensitive to steering-angle uncertainty.** At the nominal half-turn road-wheel angle, a `±5°` bounded road-wheel angle error changes the multiplier by roughly `−32%` to `+93%`. A narrow early caster error bar is not justified if road-wheel angle may be wrong by several degrees.
5. **The measurement generations are not exchangeable.** Sep11 and Sep12 values differ enough from earlier sweeps that state change, intervention, settling, transcription, or procedure changes must remain explicit.
6. **The passenger-front settling observation matters.** A roughly 0.5–1 cm downward change was physically observed after the cam was moved farther outward / steering was performed. The photos are qualitative; the observation is enough to motivate a latent state, not enough for precise photogrammetry.
7. **The recoverable large Jacobian is underdetermined.** The implemented 14×26 candidate measurement Jacobian has rank 14 and nullity 12 at the diagnostic point. A pseudoinverse cannot be called an identified state solution.
8. **The project-specific curvature Jacobian is not recovered.** The available curvature formula is general nearest-curve mathematics and does not establish truck curvature.
9. **Mixed epsilon products are historically unresolved.** The code has no default and exposes both `epsilon_i^2=0` with surviving mixed products and the stronger square-zero-ideal convention.

## Physical-action boundary

No value in this package should be used to choose a new cam adjustment solely because it appears in the old robust fit or paper eccentric model. The package preserves interventions already observed; it does not convert disputed calculations into mechanical instructions.
