import math
import numpy as np
from dakota_benchmark.geometry import (
    nominal_road_angle_deg, symmetric_caster_multiplier,
    ackermann_road_angles, caster_multiplier_range,
)


def test_nominal_multipliers():
    expected = {
        0.5: (10.3448275862, 2.784399371553343),
        1.0: (20.6896551724, 1.4152040484523252),
        1.5: (31.0344827586, 0.9698307810900904),
        1.59: (32.8965517241, 0.9206002238301603),
    }
    for turns, (angle, multiplier) in expected.items():
        got_angle = nominal_road_angle_deg(turns)
        assert math.isclose(got_angle, angle, rel_tol=0, abs_tol=1e-9)
        assert math.isclose(symmetric_caster_multiplier(got_angle), multiplier, rel_tol=0, abs_tol=1e-9)


def test_ackermann_lock_check():
    delta = math.radians(nominal_road_angle_deg(1.59))
    left, right = ackermann_road_angles(delta, 131.3, 62.8)
    vals = sorted([abs(math.degrees(float(left))), abs(math.degrees(float(right)))])
    assert np.allclose(vals, [29.2570, 37.4238], atol=5e-4)


def test_bounded_angle_error_is_not_symmetric_in_caster_multiplier():
    nominal, low, high = caster_multiplier_range(nominal_road_angle_deg(0.5), 5.0)
    assert low < nominal < high
    assert high / nominal > 1.9
    assert low / nominal < 0.7
