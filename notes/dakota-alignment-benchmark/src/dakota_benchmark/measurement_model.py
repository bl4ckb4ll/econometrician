from __future__ import annotations
from dataclasses import dataclass
import numpy as np

TURNS = np.array([-1.59, -1.0, -0.5, 0.0, 0.5, 1.0, 1.59], dtype=float)

STATE_NAMES = (
    "driver.gamma0_deg", "driver.B_deg", "driver.K_deg",
    "passenger.gamma0_deg", "passenger.B_deg", "passenger.K_deg",
    "steering.ratio", "geometry.wheelbase_in", "geometry.front_track_in",
    "calibration.level_bias_deg", "calibration.driver_gauge_bias_deg",
    "calibration.passenger_gauge_bias_deg",
    *(f"driver.alpha_offset[{i}]_rad" for i in range(7)),
    *(f"passenger.alpha_offset[{i}]_rad" for i in range(7)),
)

STATE_UNITS = (
    "deg", "deg", "deg", "deg", "deg", "deg", "dimensionless", "in", "in",
    "deg", "deg", "deg", *("rad" for _ in range(14)),
)

OBSERVATION_NAMES = tuple(
    [f"driver.camber[{i}]_deg" for i in range(7)] +
    [f"passenger.camber[{i}]_deg" for i in range(7)]
)
OBSERVATION_UNITS = tuple("deg" for _ in range(14))


@dataclass(frozen=True)
class ModelSpec:
    state_names: tuple[str, ...] = STATE_NAMES
    state_units: tuple[str, ...] = STATE_UNITS
    observation_names: tuple[str, ...] = OBSERVATION_NAMES
    observation_units: tuple[str, ...] = OBSERVATION_UNITS
    interpretation: str = (
        "Candidate measurement-model state recovered from the saved sine/even caster-sweep model, "
        "augmented only with nuisance variables demanded by the observed uncertainty record. "
        "It is not a recovered full physical suspension state."
    )


def steering_map(alpha: np.ndarray, ratio: float, wheelbase: float, track: float, side: str) -> np.ndarray:
    if ratio <= 0 or wheelbase <= 0 or track <= 0:
        raise ValueError("ratio/wheelbase/track must be positive")
    delta = alpha / ratio
    k = track / (2.0 * wheelbase)
    if side == "passenger":
        k = -k
    elif side != "driver":
        raise ValueError("side must be driver or passenger")
    t = np.tan(delta)
    return np.arctan2(t, 1.0 + k * t)


def forward(x: np.ndarray) -> np.ndarray:
    """14-observation candidate sweep model from a 26-component state."""
    x = np.asarray(x, dtype=float)
    if x.shape != (26,):
        raise ValueError("state must have 26 components")
    ratio, wb, track = x[6], x[7], x[8]
    level, d_bias, p_bias = x[9], x[10], x[11]
    alpha0 = TURNS * 2.0 * np.pi
    d_alpha = alpha0 + x[12:19]
    p_alpha = alpha0 + x[19:26]
    d_theta = steering_map(d_alpha, ratio, wb, track, "driver")
    p_theta = steering_map(p_alpha, ratio, wb, track, "passenger")
    d = x[0] + x[1] * np.sin(d_theta) + x[2] * (1.0 - np.cos(d_theta)) + level + d_bias
    p = x[3] + x[4] * np.sin(p_theta) + x[5] * (1.0 - np.cos(p_theta)) + level + p_bias
    return np.concatenate([d, p])


def jacobian(x: np.ndarray, finite_difference_step: float = 1e-6) -> np.ndarray:
    """Hybrid analytic/numerical Jacobian with named rows and columns."""
    x = np.asarray(x, dtype=float)
    y = forward(x)
    J = np.zeros((14, 26), dtype=float)
    ratio, wb, track = x[6], x[7], x[8]
    alpha0 = TURNS * 2.0 * np.pi
    d_theta = steering_map(alpha0 + x[12:19], ratio, wb, track, "driver")
    p_theta = steering_map(alpha0 + x[19:26], ratio, wb, track, "passenger")
    J[:7, 0] = 1.0
    J[:7, 1] = np.sin(d_theta)
    J[:7, 2] = 1.0 - np.cos(d_theta)
    J[7:, 3] = 1.0
    J[7:, 4] = np.sin(p_theta)
    J[7:, 5] = 1.0 - np.cos(p_theta)
    J[:, 9] = 1.0
    J[:7, 10] = 1.0
    J[7:, 11] = 1.0
    # Geometry and per-reading steering offsets use centered numerical derivatives.
    for j in list(range(6, 9)) + list(range(12, 26)):
        scale = max(1.0, abs(x[j]))
        h = finite_difference_step * scale
        xp = x.copy(); xm = x.copy()
        xp[j] += h; xm[j] -= h
        J[:, j] = (forward(xp) - forward(xm)) / (2.0 * h)
    if not np.all(np.isfinite(J)) or y.shape != (14,):
        raise RuntimeError("non-finite Jacobian")
    return J


def finite_difference_jacobian(x: np.ndarray, step: float = 1e-6) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    J = np.empty((14, 26), dtype=float)
    for j in range(26):
        h = step * max(1.0, abs(x[j]))
        xp = x.copy(); xm = x.copy()
        xp[j] += h; xm[j] -= h
        J[:, j] = (forward(xp) - forward(xm)) / (2.0 * h)
    return J
