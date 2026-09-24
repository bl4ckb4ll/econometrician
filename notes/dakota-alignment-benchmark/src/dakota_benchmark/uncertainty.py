"""Reference uncertainty machinery for the Dakota caster audit.

NumPy's default ``float`` is binary64. This module therefore validates
Jacobian/covariance structure, nonlinear bounds, dependence, and odd/even
resampling contracts; it is not the measurement-facing numeric carrier.
The physical receipt path is ``caster/haskell/CasterReceipt.hs`` and uses
IEEE-754 binary32.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from itertools import product
from typing import Callable, Sequence
import numpy as np


class UncertaintyContractError(ValueError):
    """The requested uncertainty calculation has an unsupported provenance model."""


@dataclass(frozen=True)
class CovarianceUncertainty:
    covariance: np.ndarray
    labels: tuple[str, ...]
    provenance: str
    source_id: str | None = None
    covered_effects: tuple[str, ...] = ()


@dataclass(frozen=True)
class LatentSystematic:
    """Shared/correlated source represented by state loadings times latent errors."""
    loadings: np.ndarray  # state_dim x latent_dim
    latent_covariance: np.ndarray
    labels: tuple[str, ...]
    provenance: str
    source_id: str | None = None
    covered_effects: tuple[str, ...] = ()


@dataclass(frozen=True)
class IntervalUncertainty:
    center: np.ndarray
    radius: np.ndarray
    labels: tuple[str, ...]
    provenance: str


@dataclass(frozen=True)
class SymbolicUncertainty:
    # state_dim x number_of_epsilon_labels coefficient matrix
    coefficients: np.ndarray
    epsilon_labels: tuple[str, ...]
    provenance: str


@dataclass(frozen=True)
class FeasibleRegion:
    description: str
    constraints: tuple[str, ...]
    provenance: str


@dataclass(frozen=True)
class ModelUncertainty:
    description: str
    provenance: str


@dataclass(frozen=True)
class NamedJacobian:
    values: np.ndarray
    output_labels: tuple[str, ...]
    input_labels: tuple[str, ...]
    output_units: tuple[str, ...]
    input_units: tuple[str, ...]
    provenance: str


@dataclass(frozen=True)
class CovarianceContribution:
    source_id: str
    kind: str
    provenance: str
    covered_effects: tuple[str, ...]
    output_covariance: np.ndarray


@dataclass(frozen=True)
class CovarianceReceipt:
    output_labels: tuple[str, ...]
    output_units: tuple[str, ...]
    input_labels: tuple[str, ...]
    input_units: tuple[str, ...]
    jacobian_provenance: str
    independence_assertion: str | None
    contributions: tuple[CovarianceContribution, ...]
    total_output_covariance: np.ndarray

    def as_dict(self) -> dict:
        return {
            "output_labels": list(self.output_labels),
            "output_units": list(self.output_units),
            "input_labels": list(self.input_labels),
            "input_units": list(self.input_units),
            "jacobian_provenance": self.jacobian_provenance,
            "independence_assertion": self.independence_assertion,
            "contributions": [
                {
                    "source_id": part.source_id,
                    "kind": part.kind,
                    "provenance": part.provenance,
                    "covered_effects": list(part.covered_effects),
                    "output_covariance": part.output_covariance.tolist(),
                }
                for part in self.contributions
            ],
            "total_output_covariance": self.total_output_covariance.tolist(),
        }


@dataclass(frozen=True)
class ObservationIdentity:
    observation_id: str
    generation: str
    adjustment_state: str
    side: str
    sweep_id: str
    approach_direction: str


@dataclass(frozen=True)
class NonlinearBoxReceipt:
    input_labels: tuple[str, ...]
    center: np.ndarray
    radii: np.ndarray
    center_output: float
    linear_interval: tuple[float, float]
    nonlinear_interval: tuple[float, float]
    nonlinear_minus: float
    nonlinear_plus: float
    lower_edge_gap: float
    upper_edge_gap: float
    corner_extrema_complete: bool
    provenance: str

    def as_dict(self) -> dict:
        return {
            "input_labels": list(self.input_labels),
            "center": self.center.tolist(),
            "radii": self.radii.tolist(),
            "center_output": self.center_output,
            "linear_interval": list(self.linear_interval),
            "nonlinear_interval": list(self.nonlinear_interval),
            "nonlinear_minus": self.nonlinear_minus,
            "nonlinear_plus": self.nonlinear_plus,
            "lower_edge_gap": self.lower_edge_gap,
            "upper_edge_gap": self.upper_edge_gap,
            "corner_extrema_complete": self.corner_extrema_complete,
            "coverage": (
                "complete_box_interval"
                if self.corner_extrema_complete
                else "corner_envelope_only"
            ),
            "provenance": self.provenance,
        }


@dataclass(frozen=True)
class ResamplingPlan:
    sampling_structure: str
    resampling_unit: str
    group_ids: tuple[str, ...]
    covered_effects: tuple[str, ...]
    provenance: str
    pair_ids: tuple[str, ...] = ()
    pair_roles: tuple[str, ...] = ()


@dataclass(frozen=True)
class ResamplingReceipt:
    sampling_structure: str
    resampling_unit: str
    independent_group_count: int
    covered_effects: tuple[str, ...]
    provenance: str
    pairing_status: str = "not_declared"
    symmetric_pair_count: int = 0


@dataclass(frozen=True)
class OddEvenBootstrapReplicate:
    sampled_group_ids: tuple[str, ...]
    pair_ids: tuple[str, ...]
    odd_components: tuple[float, ...]
    even_components: tuple[float, ...]


@dataclass(frozen=True)
class EstimateCombinationReceipt:
    labels: tuple[str, ...]
    estimate: float
    variance: float
    standard_error: float
    weights: np.ndarray
    covariance: np.ndarray
    provenance: str


@dataclass
class ForwardUncertainty:
    covariance_parts: list[CovarianceUncertainty] = field(default_factory=list)
    systematic_parts: list[LatentSystematic] = field(default_factory=list)
    interval_parts: list[IntervalUncertainty] = field(default_factory=list)
    symbolic_parts: list[SymbolicUncertainty] = field(default_factory=list)
    feasible_regions: list[FeasibleRegion] = field(default_factory=list)
    model_uncertainty: list[ModelUncertainty] = field(default_factory=list)


def _square_matrix(value: np.ndarray, size: int, name: str) -> np.ndarray:
    matrix = np.asarray(value, dtype=float)
    if matrix.shape != (size, size):
        raise UncertaintyContractError(
            f"{name}_shape_mismatch: expected {(size, size)}, got {matrix.shape}"
        )
    if not np.all(np.isfinite(matrix)):
        raise UncertaintyContractError(f"{name}_contains_nonfinite_value")
    if not np.allclose(matrix, matrix.T, rtol=0.0, atol=1e-12):
        raise UncertaintyContractError(f"{name}_is_not_symmetric")
    if np.min(np.linalg.eigvalsh(matrix)) < -1e-12:
        raise UncertaintyContractError(f"{name}_is_not_positive_semidefinite")
    return matrix


def _validate_named_jacobian(jacobian: NamedJacobian) -> np.ndarray:
    values = np.asarray(jacobian.values, dtype=float)
    expected = (len(jacobian.output_labels), len(jacobian.input_labels))
    if values.shape != expected:
        raise UncertaintyContractError(
            f"jacobian_shape_mismatch: expected {expected}, got {values.shape}"
        )
    if len(jacobian.output_units) != expected[0]:
        raise UncertaintyContractError("jacobian_output_unit_count_mismatch")
    if len(jacobian.input_units) != expected[1]:
        raise UncertaintyContractError("jacobian_input_unit_count_mismatch")
    if len(set(jacobian.output_labels)) != expected[0]:
        raise UncertaintyContractError("duplicate_jacobian_output_label")
    if len(set(jacobian.input_labels)) != expected[1]:
        raise UncertaintyContractError("duplicate_jacobian_input_label")
    if not np.all(np.isfinite(values)):
        raise UncertaintyContractError("jacobian_contains_nonfinite_value")
    return values


def _source_identity(source) -> str:
    source_id = source.source_id
    if source_id is None or not source_id.strip():
        raise UncertaintyContractError(
            "missing_error_source_id: every source in a final covariance receipt needs a stable id"
        )
    return source_id


def _check_source_overlap(sources: Sequence[object]) -> None:
    ids: set[str] = set()
    effects: dict[str, str] = {}
    for source in sources:
        source_id = _source_identity(source)
        if source_id in ids:
            raise UncertaintyContractError(
                f"duplicate_error_source_id: {source_id}"
            )
        ids.add(source_id)
        for effect in source.covered_effects:
            if effect in effects:
                raise UncertaintyContractError(
                    "double_counted_uncertainty: "
                    f"effect {effect!r} appears in {effects[effect]!r} and {source_id!r}"
                )
            effects[effect] = source_id


def build_covariance_receipt(
    jacobian: NamedJacobian,
    *,
    covariance_parts: Sequence[CovarianceUncertainty] = (),
    systematic_parts: Sequence[LatentSystematic] = (),
    independence_assertion: str | None = None,
) -> CovarianceReceipt:
    """Propagate named covariance sources and retain how every term entered.

    Adding separate covariance contributions asserts zero cross-covariance between
    those sources.  The caller must state that assertion whenever more than one
    source is supplied.  Correlated effects belong in one joint covariance or one
    latent-systematic block.
    """
    J = _validate_named_jacobian(jacobian)
    sources = [*covariance_parts, *systematic_parts]
    if not sources:
        raise UncertaintyContractError("at_least_one_error_source_is_required")
    if len(sources) > 1 and (independence_assertion is None or not independence_assertion.strip()):
        raise UncertaintyContractError(
            "missing_independence_assertion: adding covariance sources assumes zero cross-covariance"
        )
    _check_source_overlap(sources)

    contributions: list[CovarianceContribution] = []
    output_size, input_size = J.shape
    for part in covariance_parts:
        if tuple(part.labels) != tuple(jacobian.input_labels):
            raise UncertaintyContractError(
                "jacobian_label_order_mismatch: covariance labels must exactly match Jacobian input order"
            )
        covariance = _square_matrix(part.covariance, input_size, "input_covariance")
        output_covariance = J @ covariance @ J.T
        contributions.append(CovarianceContribution(
            source_id=_source_identity(part),
            kind="covariance",
            provenance=part.provenance,
            covered_effects=part.covered_effects,
            output_covariance=output_covariance,
        ))

    for part in systematic_parts:
        loadings = np.asarray(part.loadings, dtype=float)
        latent_size = len(part.labels)
        if loadings.shape != (input_size, latent_size):
            raise UncertaintyContractError(
                "systematic_loading_shape_mismatch: "
                f"expected {(input_size, latent_size)}, got {loadings.shape}"
            )
        latent_covariance = _square_matrix(
            part.latent_covariance, latent_size, "latent_covariance"
        )
        input_covariance = loadings @ latent_covariance @ loadings.T
        output_covariance = J @ input_covariance @ J.T
        contributions.append(CovarianceContribution(
            source_id=_source_identity(part),
            kind="shared_systematic",
            provenance=part.provenance,
            covered_effects=part.covered_effects,
            output_covariance=output_covariance,
        ))

    total = sum(
        (part.output_covariance for part in contributions),
        start=np.zeros((output_size, output_size)),
    )
    return CovarianceReceipt(
        output_labels=jacobian.output_labels,
        output_units=jacobian.output_units,
        input_labels=jacobian.input_labels,
        input_units=jacobian.input_units,
        jacobian_provenance=jacobian.provenance,
        independence_assertion=independence_assertion,
        contributions=tuple(contributions),
        total_output_covariance=total,
    )


def require_compatible_observations(
    observations: Sequence[ObservationIdentity],
    *,
    match_fields: tuple[str, ...] = (
        "generation", "adjustment_state", "side", "sweep_id", "approach_direction"
    ),
) -> dict[str, str]:
    """Reject a derived estimate assembled from incompatible measurement states."""
    if not observations:
        raise UncertaintyContractError("no_observations_supplied")
    for field_name in match_fields:
        values = {getattr(row, field_name) for row in observations}
        if "" in values:
            raise UncertaintyContractError(
                f"missing_observation_provenance: {field_name}"
            )
        if len(values) != 1:
            detail = ", ".join(
                f"{row.observation_id}={getattr(row, field_name)!r}"
                for row in observations
            )
            raise UncertaintyContractError(
                f"incompatible_observation_provenance: {field_name}: {detail}"
            )
    return {field_name: getattr(observations[0], field_name) for field_name in match_fields}


def nonlinear_box_receipt(
    function: Callable[..., float],
    *,
    center: Sequence[float],
    radii: Sequence[float],
    jacobian: Sequence[float],
    input_labels: Sequence[str],
    corner_extrema_complete: bool,
    provenance: str,
) -> NonlinearBoxReceipt:
    """Compare first-order box propagation with the nonlinear corner envelope.

    A corner envelope is a complete interval only when the caller has separately
    established that each extremum occurs at a corner over this box.  Otherwise
    the receipt labels it as a diagnostic sample, not a bound.
    """
    x = np.asarray(center, dtype=float)
    r = np.asarray(radii, dtype=float)
    J = np.asarray(jacobian, dtype=float)
    labels = tuple(input_labels)
    if x.ndim != 1 or r.shape != x.shape or J.shape != x.shape or len(labels) != len(x):
        raise UncertaintyContractError("nonlinear_box_dimension_mismatch")
    if np.any(r < 0) or not np.all(np.isfinite(x)) or not np.all(np.isfinite(r)):
        raise UncertaintyContractError("invalid_nonlinear_box")
    center_output = float(function(*x.tolist()))
    linear_radius = float(np.abs(J) @ r)
    corner_values = [
        float(function(*[value + sign * radius
                         for value, radius, sign in zip(x, r, signs)]))
        for signs in product((-1.0, 1.0), repeat=len(x))
    ]
    nonlinear_interval = (min(corner_values), max(corner_values))
    linear_interval = (center_output - linear_radius, center_output + linear_radius)
    return NonlinearBoxReceipt(
        input_labels=labels,
        center=x,
        radii=r,
        center_output=center_output,
        linear_interval=linear_interval,
        nonlinear_interval=nonlinear_interval,
        nonlinear_minus=center_output - nonlinear_interval[0],
        nonlinear_plus=nonlinear_interval[1] - center_output,
        lower_edge_gap=nonlinear_interval[0] - linear_interval[0],
        upper_edge_gap=nonlinear_interval[1] - linear_interval[1],
        corner_extrema_complete=corner_extrema_complete,
        provenance=provenance,
    )


def odd_even_components(gamma_plus: float, gamma_minus: float) -> tuple[float, float]:
    """Return the odd and even camber components for one symmetric steering pair."""
    if not np.isfinite(gamma_plus) or not np.isfinite(gamma_minus):
        raise UncertaintyContractError("nonfinite_odd_even_input")
    return ((gamma_plus - gamma_minus) / 2.0,
            (gamma_plus + gamma_minus) / 2.0)


def audit_resampling_plan(
    plan: ResamplingPlan,
    *,
    explicit_error_sources: Sequence[CovarianceUncertainty | LatentSystematic] = (),
) -> ResamplingReceipt:
    """Validate the sampling unit, odd/even pairing, and uncertainty coverage."""
    if plan.sampling_structure == "designed":
        raise UncertaintyContractError(
            "designed_positions_not_iid: steering positions are design points, not sampling units"
        )
    if plan.sampling_structure not in {"iid", "clustered"}:
        raise UncertaintyContractError("unsupported_sampling_structure")
    if plan.sampling_structure == "iid" and plan.resampling_unit != "observation":
        raise UncertaintyContractError(
            "wrong_resampling_unit: IID sampling requires observation units"
        )
    if plan.sampling_structure == "clustered" and plan.resampling_unit == "observation":
        raise UncertaintyContractError(
            "wrong_resampling_unit: clustered sampling must resample declared groups"
        )
    if not plan.group_ids:
        raise UncertaintyContractError("missing_resampling_groups")
    group_count = len(set(plan.group_ids))
    if group_count < 2:
        raise UncertaintyContractError("insufficient_independent_resampling_groups")
    if plan.sampling_structure == "iid" and group_count != len(plan.group_ids):
        raise UncertaintyContractError(
            "dependent_observations_labeled_iid: repeated group id found"
        )

    pairing_status = "not_declared"
    symmetric_pair_count = 0
    if bool(plan.pair_ids) != bool(plan.pair_roles):
        raise UncertaintyContractError("incomplete_odd_even_pair_metadata")
    if plan.pair_ids:
        if len(plan.pair_ids) != len(plan.group_ids) or len(plan.pair_roles) != len(plan.group_ids):
            raise UncertaintyContractError("odd_even_pair_metadata_length_mismatch")
        if any(not pair_id for pair_id in plan.pair_ids):
            raise UncertaintyContractError("missing_odd_even_pair_id")
        if any(role not in {"plus", "minus"} for role in plan.pair_roles):
            raise UncertaintyContractError("invalid_odd_even_pair_role")

        by_group: dict[str, dict[str, list[str]]] = {}
        for group_id, pair_id, role in zip(plan.group_ids, plan.pair_ids, plan.pair_roles):
            by_group.setdefault(group_id, {}).setdefault(pair_id, []).append(role)
        reference_pairs: tuple[str, ...] | None = None
        for group_id, pairs in by_group.items():
            pair_set = tuple(sorted(pairs))
            if reference_pairs is None:
                reference_pairs = pair_set
            elif pair_set != reference_pairs:
                raise UncertaintyContractError(
                    "odd_even_pair_set_mismatch_between_resampling_groups"
                )
            for pair_id, roles in pairs.items():
                if sorted(roles) != ["minus", "plus"]:
                    raise UncertaintyContractError(
                        "odd_even_pair_incomplete_within_resampling_group: "
                        f"group={group_id!r} pair={pair_id!r}"
                    )
        symmetric_pair_count = len(reference_pairs or ())
        pairing_status = "symmetric_odd_even_pairs_preserved"

    explicit_effects: dict[str, str] = {}
    for source in explicit_error_sources:
        source_id = _source_identity(source)
        for effect in source.covered_effects:
            explicit_effects[effect] = source_id
    for effect in plan.covered_effects:
        if effect in explicit_effects:
            raise UncertaintyContractError(
                "bootstrap_measurement_error_double_count: "
                f"effect {effect!r} is in the resampling plan and {explicit_effects[effect]!r}"
            )
    return ResamplingReceipt(
        sampling_structure=plan.sampling_structure,
        resampling_unit=plan.resampling_unit,
        independent_group_count=group_count,
        covered_effects=plan.covered_effects,
        provenance=plan.provenance,
        pairing_status=pairing_status,
        symmetric_pair_count=symmetric_pair_count,
    )


def replay_odd_even_bootstrap(
    plan: ResamplingPlan,
    gamma_values: Sequence[float],
    group_draws: Sequence[Sequence[str]],
) -> tuple[OddEvenBootstrapReplicate, ...]:
    """Replay explicit cluster-bootstrap draws and recompute odd/even components.

    The draws are explicit rather than RNG-generated so a receipt can record the
    exact resampled groups.  Each replicate must draw exactly the original
    number of independent groups, with replacement.
    """
    receipt = audit_resampling_plan(plan)
    if receipt.pairing_status != "symmetric_odd_even_pairs_preserved":
        raise UncertaintyContractError("odd_even_pairing_required_for_bootstrap")
    if len(gamma_values) != len(plan.group_ids):
        raise UncertaintyContractError("bootstrap_value_count_mismatch")
    values = np.asarray(gamma_values, dtype=float)
    if not np.all(np.isfinite(values)):
        raise UncertaintyContractError("nonfinite_bootstrap_value")

    lookup: dict[tuple[str, str, str], float] = {}
    for group_id, pair_id, role, value in zip(
        plan.group_ids, plan.pair_ids, plan.pair_roles, values.tolist()
    ):
        key = (group_id, pair_id, role)
        if key in lookup:
            raise UncertaintyContractError("duplicate_odd_even_bootstrap_member")
        lookup[key] = value

    pair_ids = tuple(sorted(set(plan.pair_ids)))
    known_groups = set(plan.group_ids)
    replicates: list[OddEvenBootstrapReplicate] = []
    for draw in group_draws:
        sampled = tuple(draw)
        if len(sampled) != receipt.independent_group_count:
            raise UncertaintyContractError("bootstrap_draw_wrong_group_count")
        if any(group_id not in known_groups for group_id in sampled):
            raise UncertaintyContractError("bootstrap_draw_unknown_group")
        odd_values = []
        even_values = []
        for pair_id in pair_ids:
            components = [
                odd_even_components(
                    lookup[(group_id, pair_id, "plus")],
                    lookup[(group_id, pair_id, "minus")],
                )
                for group_id in sampled
            ]
            odd_values.append(float(np.mean([part[0] for part in components])))
            even_values.append(float(np.mean([part[1] for part in components])))
        replicates.append(OddEvenBootstrapReplicate(
            sampled_group_ids=sampled,
            pair_ids=pair_ids,
            odd_components=tuple(odd_values),
            even_components=tuple(even_values),
        ))
    return tuple(replicates)


def combine_correlated_estimates(
    estimates: Sequence[float],
    covariance: np.ndarray,
    *,
    labels: Sequence[str],
    provenance: str,
) -> EstimateCombinationReceipt:
    """Generalized least-squares mean for estimates with a declared covariance."""
    values = np.asarray(estimates, dtype=float)
    names = tuple(labels)
    if values.ndim != 1 or len(names) != len(values):
        raise UncertaintyContractError("estimate_label_count_mismatch")
    cov = _square_matrix(covariance, len(values), "estimate_covariance")
    if np.min(np.linalg.eigvalsh(cov)) <= 1e-12:
        raise UncertaintyContractError(
            "estimate_covariance_is_singular: retain the shared source or add justified independent variation"
        )
    ones = np.ones(len(values))
    solved = np.linalg.solve(cov, ones)
    normalizer = float(ones @ solved)
    weights = solved / normalizer
    variance = 1.0 / normalizer
    return EstimateCombinationReceipt(
        labels=names,
        estimate=float(weights @ values),
        variance=variance,
        standard_error=float(np.sqrt(variance)),
        weights=weights,
        covariance=cov,
        provenance=provenance,
    )


def propagate_linear(
    J: np.ndarray,
    *,
    covariance_parts: list[CovarianceUncertainty] | None = None,
    systematic_parts: list[LatentSystematic] | None = None,
    interval_parts: list[IntervalUncertainty] | None = None,
    symbolic_parts: list[SymbolicUncertainty] | None = None,
    feasible_regions: list[FeasibleRegion] | None = None,
    model_uncertainty: list[ModelUncertainty] | None = None,
) -> ForwardUncertainty:
    """First-order forward propagation without collapsing heterogeneous uncertainty."""
    J = np.asarray(J, dtype=float)
    out = ForwardUncertainty()
    for part in covariance_parts or []:
        cov = np.asarray(part.covariance, dtype=float)
        out.covariance_parts.append(
            CovarianceUncertainty(J @ cov @ J.T, tuple(), part.provenance)
        )
    for part in systematic_parts or []:
        L = np.asarray(part.loadings, dtype=float)
        out.systematic_parts.append(
            LatentSystematic(J @ L, np.asarray(part.latent_covariance, dtype=float), part.labels, part.provenance)
        )
    for part in interval_parts or []:
        center = np.asarray(part.center, dtype=float)
        radius = np.asarray(part.radius, dtype=float)
        out.interval_parts.append(
            IntervalUncertainty(J @ center, np.abs(J) @ radius, tuple(), part.provenance)
        )
    for part in symbolic_parts or []:
        C = np.asarray(part.coefficients, dtype=float)
        out.symbolic_parts.append(
            SymbolicUncertainty(J @ C, part.epsilon_labels, part.provenance)
        )
    out.feasible_regions.extend(feasible_regions or [])
    out.model_uncertainty.extend(model_uncertainty or [])
    return out


def combine_independent_covariances(parts: list[CovarianceUncertainty]) -> np.ndarray:
    """Combine only parts explicitly asserted independent by the caller."""
    if not parts:
        raise ValueError("at least one covariance part is required")
    shapes = {np.asarray(p.covariance).shape for p in parts}
    if len(shapes) != 1:
        raise ValueError("covariance shapes differ")
    return sum((np.asarray(p.covariance, dtype=float) for p in parts), start=np.zeros(next(iter(shapes))))
