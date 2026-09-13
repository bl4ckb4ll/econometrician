import numpy as np
from dakota_benchmark.uncertainty import (
    CovarianceUncertainty, LatentSystematic, IntervalUncertainty,
    SymbolicUncertainty, propagate_linear,
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
