import math
import pytest
from dakota_benchmark.curvature import (
    nearest_curve_second_derivative, nearest_curve_inverse_sensitivity,
    sweep_second_derivative, project_curvature_jacobian_definition,
    CurvatureJacobianNotRecovered,
)


def test_recovered_nearest_curve_formula():
    assert math.isclose(nearest_curve_second_derivative(2.0, 0.25), 0.5)
    assert math.isclose(nearest_curve_inverse_sensitivity(0.1, 2.0, 0.25), 0.2)


def test_nearest_curve_singularity_is_not_inverted():
    with pytest.raises(ZeroDivisionError):
        nearest_curve_inverse_sensitivity(1.0, 2.0, 0.5)


def test_sweep_second_derivative():
    assert math.isclose(sweep_second_derivative(0.0, 7.0, 3.0), 3.0)


def test_project_specific_curvature_jacobian_is_not_invented():
    with pytest.raises(CurvatureJacobianNotRecovered):
        project_curvature_jacobian_definition()
