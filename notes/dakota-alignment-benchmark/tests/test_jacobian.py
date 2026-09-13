import numpy as np
from dakota_benchmark.measurement_model import forward, jacobian, finite_difference_jacobian, STATE_NAMES, OBSERVATION_NAMES
from dakota_benchmark.inverse import svd_diagnostics


def reference_state():
    x = np.zeros(26)
    x[:6] = [-2.029899191589185, -8.06428261283, 5.875744070846088,
             1.3341515392720393, 5.047094321147211, 8.682128431656844]
    x[6:9] = [17.4, 131.3, 62.8]
    return x


def test_dimensions_and_names():
    x = reference_state()
    assert forward(x).shape == (14,)
    J = jacobian(x)
    assert J.shape == (14, 26)
    assert len(STATE_NAMES) == 26
    assert len(OBSERVATION_NAMES) == 14


def test_hybrid_jacobian_matches_full_finite_difference():
    x = reference_state()
    assert np.max(np.abs(jacobian(x) - finite_difference_jacobian(x))) < 2e-6


def test_structural_nonidentifiability_is_retained():
    x = reference_state()
    d = svd_diagnostics(jacobian(x))
    assert d.rank <= 14
    assert d.nullity >= 12
    assert d.cols == 26


def test_expected_bias_dependency():
    x = reference_state()
    J = jacobian(x)
    # driver gamma0 and driver gauge bias are exactly the same observation direction.
    assert np.array_equal(J[:, 0], J[:, 10])
    # passenger gamma0 and passenger gauge bias likewise.
    assert np.array_equal(J[:, 3], J[:, 11])
