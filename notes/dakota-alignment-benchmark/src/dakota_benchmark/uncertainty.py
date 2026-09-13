from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np


@dataclass(frozen=True)
class CovarianceUncertainty:
    covariance: np.ndarray
    labels: tuple[str, ...]
    provenance: str


@dataclass(frozen=True)
class LatentSystematic:
    """Shared/correlated source represented by state loadings times latent errors."""
    loadings: np.ndarray  # state_dim x latent_dim
    latent_covariance: np.ndarray
    labels: tuple[str, ...]
    provenance: str


@dataclass(frozen=True)
class IntervalUncertainty:
    center: np.ndarray
    radius: np.ndarray
    labels: tuple[str, ...]
    provenance: str


@dataclass(frozen=True)
class SymbolicUncertainty:
    # state_dim x number_of_epsilon_labels coefficient matrix
    coefficients: np.ndarray
    epsilon_labels: tuple[str, ...]
    provenance: str


@dataclass(frozen=True)
class FeasibleRegion:
    description: str
    constraints: tuple[str, ...]
    provenance: str


@dataclass(frozen=True)
class ModelUncertainty:
    description: str
    provenance: str


@dataclass
class ForwardUncertainty:
    covariance_parts: list[CovarianceUncertainty] = field(default_factory=list)
    systematic_parts: list[LatentSystematic] = field(default_factory=list)
    interval_parts: list[IntervalUncertainty] = field(default_factory=list)
    symbolic_parts: list[SymbolicUncertainty] = field(default_factory=list)
    feasible_regions: list[FeasibleRegion] = field(default_factory=list)
    model_uncertainty: list[ModelUncertainty] = field(default_factory=list)


def propagate_linear(
    J: np.ndarray,
    *,
    covariance_parts: list[CovarianceUncertainty] | None = None,
    systematic_parts: list[LatentSystematic] | None = None,
    interval_parts: list[IntervalUncertainty] | None = None,
    symbolic_parts: list[SymbolicUncertainty] | None = None,
    feasible_regions: list[FeasibleRegion] | None = None,
    model_uncertainty: list[ModelUncertainty] | None = None,
) -> ForwardUncertainty:
    """First-order forward propagation without collapsing heterogeneous uncertainty."""
    J = np.asarray(J, dtype=float)
    out = ForwardUncertainty()
    for part in covariance_parts or []:
        cov = np.asarray(part.covariance, dtype=float)
        out.covariance_parts.append(
            CovarianceUncertainty(J @ cov @ J.T, tuple(), part.provenance)
        )
    for part in systematic_parts or []:
        L = np.asarray(part.loadings, dtype=float)
        out.systematic_parts.append(
            LatentSystematic(J @ L, np.asarray(part.latent_covariance, dtype=float), part.labels, part.provenance)
        )
    for part in interval_parts or []:
        center = np.asarray(part.center, dtype=float)
        radius = np.asarray(part.radius, dtype=float)
        out.interval_parts.append(
            IntervalUncertainty(J @ center, np.abs(J) @ radius, tuple(), part.provenance)
        )
    for part in symbolic_parts or []:
        C = np.asarray(part.coefficients, dtype=float)
        out.symbolic_parts.append(
            SymbolicUncertainty(J @ C, part.epsilon_labels, part.provenance)
        )
    out.feasible_regions.extend(feasible_regions or [])
    out.model_uncertainty.extend(model_uncertainty or [])
    return out


def combine_independent_covariances(parts: list[CovarianceUncertainty]) -> np.ndarray:
    """Combine only parts explicitly asserted independent by the caller."""
    if not parts:
        raise ValueError("at least one covariance part is required")
    shapes = {np.asarray(p.covariance).shape for p in parts}
    if len(shapes) != 1:
        raise ValueError("covariance shapes differ")
    return sum((np.asarray(p.covariance, dtype=float) for p in parts), start=np.zeros(next(iter(shapes))))
