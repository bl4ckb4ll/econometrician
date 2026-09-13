from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.optimize import linprog


@dataclass(frozen=True)
class SVDDiagnostics:
    rank: int
    rows: int
    cols: int
    nullity: int
    singular_values: np.ndarray
    condition_nonzero: float
    tolerance: float


def svd_diagnostics(J: np.ndarray, rtol: float | None = None) -> SVDDiagnostics:
    J = np.asarray(J, dtype=float)
    s = np.linalg.svd(J, compute_uv=False)
    tol = (max(J.shape) * np.finfo(float).eps * s[0]) if rtol is None else rtol * s[0]
    rank = int(np.sum(s > tol))
    cond = float(s[0] / s[rank - 1]) if rank else float("inf")
    return SVDDiagnostics(rank, J.shape[0], J.shape[1], J.shape[1] - rank, s, cond, tol)


def pseudoinverse_solution(J: np.ndarray, dy: np.ndarray) -> dict:
    """Return min-norm linearized solution, explicitly retaining non-identifiability."""
    J = np.asarray(J, dtype=float)
    dy = np.asarray(dy, dtype=float)
    diag = svd_diagnostics(J)
    U, s, Vt = np.linalg.svd(J, full_matrices=True)
    pinv = np.linalg.pinv(J)
    dx = pinv @ dy
    null_basis = Vt[diag.rank:, :].T
    return {
        "minimum_norm_dx": dx,
        "residual": J @ dx - dy,
        "rank": diag.rank,
        "nullity": diag.nullity,
        "identified_unique": bool(diag.rank == J.shape[1]),
        "nullspace_basis": null_basis,
    }


def inverse_interval_bounds(
    J: np.ndarray,
    y_center: np.ndarray,
    y_radius: np.ndarray,
    state_bounds: list[tuple[float | None, float | None]] | None = None,
) -> dict:
    """Coordinate-wise feasible bounds for |J x - y_center| <= y_radius.

    Infinite/unbounded coordinates are reported as such. This is a linearized
    feasible-set calculation, not a posterior distribution.
    """
    J = np.asarray(J, dtype=float)
    c = np.asarray(y_center, dtype=float)
    r = np.asarray(y_radius, dtype=float)
    m, n = J.shape
    if c.shape != (m,) or r.shape != (m,) or np.any(r < 0):
        raise ValueError("incompatible interval observation")
    A = np.vstack([J, -J])
    b = np.concatenate([c + r, -c + r])
    bounds = state_bounds or [(None, None)] * n
    lows, highs, status = [], [], []
    for j in range(n):
        obj = np.zeros(n); obj[j] = 1.0
        lo = linprog(obj, A_ub=A, b_ub=b, bounds=bounds, method="highs")
        hi = linprog(-obj, A_ub=A, b_ub=b, bounds=bounds, method="highs")
        lows.append(float(lo.fun) if lo.success else None)
        highs.append(float(-hi.fun) if hi.success else None)
        status.append((lo.status, hi.status))
    return {"lower": lows, "upper": highs, "solver_status": status}
