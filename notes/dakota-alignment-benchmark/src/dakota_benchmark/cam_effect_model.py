from __future__ import annotations
import numpy as np


def paper_cam_effect_jacobian() -> np.ndarray:
    """Uncalibrated paper model, NOT a measured degrees-per-cam rule.

    Inputs: [driver_front_u, driver_rear_u, passenger_front_u, passenger_rear_u]
    Outputs: [driver_camber_deg, driver_caster_deg, passenger_camber_deg, passenger_caster_deg]
    u is normalized in/out position in the generated estimate: -1 inward, +1 outward.
    """
    block = np.array([[-1.3, -0.7], [-1.0, 1.0]], dtype=float)
    J = np.zeros((4, 4), dtype=float)
    J[:2, :2] = block
    J[2:, 2:] = block
    return J
