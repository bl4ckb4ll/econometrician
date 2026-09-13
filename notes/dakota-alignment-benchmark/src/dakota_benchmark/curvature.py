from __future__ import annotations
import math


class CurvatureJacobianNotRecovered(RuntimeError):
    pass


def nearest_curve_second_derivative(normal_offset: float, signed_curvature: float) -> float:
    """Recovered general curve result E'' = 1 - r*kappa."""
    return 1.0 - normal_offset * signed_curvature


def nearest_curve_inverse_sensitivity(
    tangent_dot_observation_perturbation: float,
    normal_offset: float,
    signed_curvature: float,
    singular_tolerance: float = 1e-12,
) -> float:
    denominator = nearest_curve_second_derivative(normal_offset, signed_curvature)
    if abs(denominator) <= singular_tolerance:
        raise ZeroDivisionError("nearest-point inverse is singular/ill-conditioned at 1-r*kappa=0")
    return tangent_dot_observation_perturbation / denominator


def sweep_first_derivative(theta_rad: float, B_deg: float, K_deg: float) -> float:
    return B_deg * math.cos(theta_rad) + K_deg * math.sin(theta_rad)


def sweep_second_derivative(theta_rad: float, B_deg: float, K_deg: float) -> float:
    """Second derivative of the recovered candidate gamma(theta) basis.

    This is not asserted to be the project's intended 'curvature Jacobian'.
    """
    return -B_deg * math.sin(theta_rad) + K_deg * math.cos(theta_rad)


def project_curvature_jacobian_definition() -> None:
    """Refuse to invent a project-specific construction not recovered from evidence."""
    raise CurvatureJacobianNotRecovered(
        "No project-specific definition of 'curvature Jacobian' was recovered. "
        "Recovered material contains an ordinary sweep Jacobian idea, a general nearest-curve "
        "curvature sensitivity formula, and second derivatives, but not the named block/object."
    )
