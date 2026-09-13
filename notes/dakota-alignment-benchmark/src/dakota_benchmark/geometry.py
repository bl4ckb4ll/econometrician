from __future__ import annotations
import math
import numpy as np


def nominal_road_angle_deg(steering_wheel_turns: float, ratio: float = 17.4) -> float:
    """Equal-angle nominal road-wheel yaw from steering-wheel turns.

    This is a model conversion, not a measured Dakota steering angle.
    """
    if ratio <= 0:
        raise ValueError("ratio must be positive")
    return 360.0 * steering_wheel_turns / ratio


def symmetric_caster_multiplier(road_wheel_angle_deg: float) -> float:
    """1/(2 sin(theta)) for equal-and-opposite steering positions."""
    theta = math.radians(road_wheel_angle_deg)
    s = math.sin(theta)
    if abs(s) < 1e-15:
        raise ValueError("caster multiplier is singular at zero steering angle")
    return 1.0 / (2.0 * s)


def caster_from_symmetric_pair(
    gamma_plus_deg: float, gamma_minus_deg: float, road_wheel_angle_deg: float
) -> float:
    """Signed coefficient from a symmetric camber pair under the simple sine model."""
    return (gamma_plus_deg - gamma_minus_deg) * symmetric_caster_multiplier(road_wheel_angle_deg)


def caster_angle_relative_sensitivity_per_degree(road_wheel_angle_deg: float) -> float:
    """|dC/C| per one degree of road-wheel angle error for C ∝ csc(theta)."""
    theta = math.radians(road_wheel_angle_deg)
    return abs(1.0 / math.tan(theta)) * math.pi / 180.0


def caster_multiplier_range(
    nominal_angle_deg: float, bounded_angle_error_deg: float
) -> tuple[float, float, float]:
    """Return multiplier at nominal and extrema over a symmetric bounded angle error.

    Assumes the whole interval stays on the same side of zero.
    """
    lo = nominal_angle_deg - bounded_angle_error_deg
    hi = nominal_angle_deg + bounded_angle_error_deg
    if lo <= 0 <= hi:
        raise ValueError("angle-error interval crosses the caster singularity at zero")
    vals = [symmetric_caster_multiplier(a) for a in (lo, nominal_angle_deg, hi)]
    return vals[1], min(vals[0], vals[2]), max(vals[0], vals[2])


def ackermann_road_angles(
    equivalent_center_angle_rad: np.ndarray | float,
    wheelbase_in: float,
    track_in: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Ideal Ackermann left/right wheel angles from a center-angle parameter.

    Returns (left_wheel, right_wheel).  This is ideal geometry, not measured rack
    kinematics. Positive means a right turn under the benchmark convention.
    """
    if wheelbase_in <= 0 or track_in <= 0:
        raise ValueError("wheelbase and track must be positive")
    delta = np.asarray(equivalent_center_angle_rad, dtype=float)
    t = np.tan(delta)
    k = track_in / (2.0 * wheelbase_in)
    # Same parameterization as the recovered script: driver/left uses +k,
    # passenger/right uses -k.
    left = np.arctan2(t, 1.0 + k * t)
    right = np.arctan2(t, 1.0 - k * t)
    return left, right
