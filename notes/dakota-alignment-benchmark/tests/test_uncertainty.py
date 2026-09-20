import math
import numpy as np
import pytest
from dakota_benchmark.uncertainty import (
    CovarianceUncertainty, LatentSystematic, IntervalUncertainty,
    NamedJacobian, ObservationIdentity, ResamplingPlan,
    SymbolicUncertainty, UncertaintyContractError,
    audit_resampling_plan, build_covariance_receipt,
    combine_correlated_estimates, nonlinear_box_receipt, odd_even_components,
    propagate_linear, require_compatible_observations,
)


DAKOTA_LABELS = (
    "theta_right_deg", "theta_left_deg",
    "gamma_right_deg", "gamma_left_deg",
)
DAKOTA_JACOBIAN = NamedJacobian(
    values=np.array([[-0.2662274831764701, 0.2662274831764701,
                      -2.784399371553343, 2.784399371553343]]),
    output_labels=("caster_magnitude_deg",),
    input_labels=DAKOTA_LABELS,
    output_units=("deg",),
    input_units=("deg", "deg", "deg", "deg"),
    provenance="Sep10 G2 passenger half-turn analytic Jacobian",
)


def test_correlated_error_is_not_naive_rss():
    J = np.array([[1.0, 1.0]])
    cov = np.array([[1.0, 0.8], [0.8, 1.0]])
    part = CovarianceUncertainty(cov, ("a", "b"), "test")
    out = propagate_linear(J, covariance_parts=[part])
    assert np.allclose(out.covariance_parts[0].covariance, [[3.6]])
    assert not np.allclose(out.covariance_parts[0].covariance, [[2.0]])


def test_shared_systematic_loadings_survive_as_a_named_source():
    J = np.eye(2)
    systematic = LatentSystematic(
        loadings=np.array([[1.0], [1.0]]),
        latent_covariance=np.array([[0.25]]),
        labels=("level_zero",), provenance="same level setup")
    out = propagate_linear(J, systematic_parts=[systematic])
    assert np.allclose(out.systematic_parts[0].loadings, [[1.0], [1.0]])


def test_interval_and_symbolic_stay_separate():
    J = np.array([[2.0, -1.0]])
    interval = IntervalUncertainty(np.zeros(2), np.array([0.5, 1.0]), ("x", "y"), "bounded")
    symbolic = SymbolicUncertainty(np.eye(2), ("e1", "e2"), "unknown tolerance")
    out = propagate_linear(J, interval_parts=[interval], symbolic_parts=[symbolic])
    assert np.allclose(out.interval_parts[0].radius, [2.0])
    assert np.allclose(out.symbolic_parts[0].coefficients, [[2.0, -1.0]])


def test_named_covariance_receipt_preserves_source_and_units():
    source = CovarianceUncertainty(
        covariance=np.diag([0.0, 0.0, 0.25**2, 0.25**2]),
        labels=DAKOTA_LABELS,
        provenance="historical illustrative independent read errors",
        source_id="historical_read_error",
        covered_effects=("gamma_right_read", "gamma_left_read"),
    )
    receipt = build_covariance_receipt(DAKOTA_JACOBIAN,
                                       covariance_parts=[source])
    expected_variance = 2 * (2.784399371553343 * 0.25) ** 2
    assert np.allclose(receipt.total_output_covariance, [[expected_variance]])
    rendered = receipt.as_dict()
    assert rendered["input_labels"] == list(DAKOTA_LABELS)
    assert rendered["input_units"] == ["deg"] * 4
    assert rendered["contributions"][0]["source_id"] == "historical_read_error"


def test_named_covariance_rejects_wrong_jacobian_variable_order():
    source = CovarianceUncertainty(
        covariance=np.eye(4),
        labels=("gamma_right_deg", "gamma_left_deg",
                "theta_right_deg", "theta_left_deg"),
        provenance="wrong historical order",
        source_id="wrong_order",
    )
    with pytest.raises(UncertaintyContractError,
                       match="jacobian_label_order_mismatch"):
        build_covariance_receipt(DAKOTA_JACOBIAN,
                                 covariance_parts=[source])


def test_common_camber_zero_is_one_systematic_and_cancels():
    shared_zero = LatentSystematic(
        loadings=np.array([[0.0], [0.0], [1.0], [1.0]]),
        latent_covariance=np.array([[0.25**2]]),
        labels=("camber_zero",),
        provenance="same gauge zero at both endpoints",
        source_id="camber_zero",
        covered_effects=("common_camber_zero",),
    )
    receipt = build_covariance_receipt(DAKOTA_JACOBIAN,
                                       systematic_parts=[shared_zero])
    assert np.allclose(receipt.total_output_covariance, [[0.0]], atol=1e-15)


def test_separate_sources_require_explicit_independence_assertion():
    first = CovarianceUncertainty(
        np.eye(4), DAKOTA_LABELS, "first", "first", ("first",))
    second = CovarianceUncertainty(
        np.eye(4), DAKOTA_LABELS, "second", "second", ("second",))
    with pytest.raises(UncertaintyContractError,
                       match="missing_independence_assertion"):
        build_covariance_receipt(DAKOTA_JACOBIAN,
                                 covariance_parts=[first, second])


def test_duplicate_effect_cannot_enter_two_error_sources():
    first = CovarianceUncertainty(
        np.eye(4), DAKOTA_LABELS, "first", "first", ("steering_calibration",))
    second = CovarianceUncertainty(
        np.eye(4), DAKOTA_LABELS, "second", "second", ("steering_calibration",))
    with pytest.raises(UncertaintyContractError,
                       match="double_counted_uncertainty"):
        build_covariance_receipt(
            DAKOTA_JACOBIAN,
            covariance_parts=[first, second],
            independence_assertion="claimed independent for regression test",
        )


def test_shared_systematic_does_not_shrink_like_independent_noise():
    independent_variance = 0.25
    shared_variance = 1.0
    covariance = (
        np.eye(3) * independent_variance
        + np.ones((3, 3)) * shared_variance
    )
    combined = combine_correlated_estimates(
        [5.5688, 5.6608, 5.5236], covariance,
        labels=("half", "full", "lock"),
        provenance="G2 three-pair dependence regression",
    )
    assert np.allclose(combined.weights, [1 / 3] * 3)
    assert combined.variance == pytest.approx(1.0 + 0.25 / 3)
    naive_independent_variance = (1.0 + 0.25) / 3
    assert combined.variance > 2.5 * naive_independent_variance


def test_measurements_from_different_adjustment_states_are_rejected():
    g2 = ObservationIdentity(
        "E-026", "G2", "pre_I1", "passenger", "sep10", "right_to_left")
    g4 = ObservationIdentity(
        "E-066", "G4", "post_I1_pre_I2", "passenger", "sep12", "left_to_right")
    with pytest.raises(UncertaintyContractError,
                       match="incompatible_observation_provenance"):
        require_compatible_observations([g2, g4])


def test_same_sweep_pair_has_compatible_provenance():
    rows = [
        ObservationIdentity("E-026", "G2", "pre_I1", "passenger",
                            "sep10", "right_to_left"),
        ObservationIdentity("E-028", "G2", "pre_I1", "passenger",
                            "sep10", "right_to_left"),
    ]
    receipt = require_compatible_observations(rows)
    assert receipt["generation"] == "G2"
    assert receipt["sweep_id"] == "sep10"


def test_half_turn_five_degree_bound_requires_asymmetric_nonlinear_interval():
    theta = 180.0 / 17.4

    def caster_magnitude(theta_right, theta_left, gamma_right, gamma_left):
        denominator = (
            math.sin(math.radians(theta_right))
            - math.sin(math.radians(theta_left))
        )
        return abs((gamma_right - gamma_left) / denominator)

    receipt = nonlinear_box_receipt(
        caster_magnitude,
        center=(theta, -theta, 0.5, 2.5),
        radii=(5.0, 5.0, 0.0, 0.0),
        jacobian=DAKOTA_JACOBIAN.values[0],
        input_labels=DAKOTA_LABELS,
        corner_extrema_complete=True,
        provenance="historical +/-5 deg road-wheel bound; monotone on this box",
    )
    assert receipt.center_output == pytest.approx(5.568798743106686)
    assert receipt.linear_interval == pytest.approx(
        (2.9065239113419845, 8.231073574871386))
    assert receipt.nonlinear_interval == pytest.approx(
        (3.778894920165921, 10.735418793944593))
    assert receipt.nonlinear_minus == pytest.approx(1.7899038229407647)
    assert receipt.nonlinear_plus == pytest.approx(5.166620050837907)
    assert receipt.as_dict()["coverage"] == "complete_box_interval"


def test_symmetric_pair_odd_and_even_components_are_both_retained():
    odd, even = odd_even_components(0.5, 2.5)
    assert odd == pytest.approx(-1.0)
    assert even == pytest.approx(1.5)


def test_dakota_steering_positions_are_not_bootstrap_units():
    plan = ResamplingPlan(
        sampling_structure="designed",
        resampling_unit="steering_position",
        group_ids=("max_left", "one_left", "half_left", "straight",
                   "half_right", "one_right", "max_right"),
        covered_effects=("between_position_variation",),
        provenance="one seven-position Dakota sweep",
    )
    with pytest.raises(UncertaintyContractError,
                       match="designed_positions_not_iid"):
        audit_resampling_plan(plan)


def test_bootstrap_and_explicit_measurement_error_cannot_cover_same_effect():
    plan = ResamplingPlan(
        sampling_structure="clustered",
        resampling_unit="sweep",
        group_ids=("sweep_1", "sweep_1", "sweep_2", "sweep_2"),
        covered_effects=("gauge_repeatability",),
        provenance="two complete independent sweeps",
    )
    source = CovarianceUncertainty(
        np.eye(2), ("a", "b"), "explicit repeatability covariance",
        "gauge_repeatability_covariance", ("gauge_repeatability",))
    with pytest.raises(UncertaintyContractError,
                       match="bootstrap_measurement_error_double_count"):
        audit_resampling_plan(plan, explicit_error_sources=[source])


def test_cluster_plan_retains_actual_independent_unit_count_and_odd_even_pairs():
    plan = ResamplingPlan(
        sampling_structure="clustered",
        resampling_unit="measurement_session",
        group_ids=("session_1", "session_1", "session_2", "session_2"),
        covered_effects=("between_session_variation",),
        provenance="two sessions; illustrative validation only",
        pair_ids=("half_turn", "half_turn", "half_turn", "half_turn"),
        pair_roles=("plus", "minus", "plus", "minus"),
    )
    receipt = audit_resampling_plan(plan)
    assert receipt.independent_group_count == 2
    assert receipt.pairing_status == "symmetric_odd_even_pairs_preserved"
    assert receipt.symmetric_pair_count == 1


def test_odd_even_pair_must_stay_inside_each_resampling_group():
    plan = ResamplingPlan(
        sampling_structure="clustered",
        resampling_unit="measurement_session",
        group_ids=("session_1", "session_2"),
        covered_effects=("between_session_variation",),
        provenance="invalid split pair regression",
        pair_ids=("half_turn", "half_turn"),
        pair_roles=("plus", "minus"),
    )
    with pytest.raises(UncertaintyContractError,
                       match="odd_even_pair_incomplete_within_resampling_group"):
        audit_resampling_plan(plan)


def test_single_sweep_cannot_be_promoted_to_odd_even_bootstrap():
    plan = ResamplingPlan(
        sampling_structure="clustered",
        resampling_unit="sweep",
        group_ids=("sep10", "sep10"),
        covered_effects=("between_sweep_variation",),
        provenance="surviving G2 Dakota sweep",
        pair_ids=("half_turn", "half_turn"),
        pair_roles=("plus", "minus"),
    )
    with pytest.raises(UncertaintyContractError,
                       match="insufficient_independent_resampling_groups"):
        audit_resampling_plan(plan)
