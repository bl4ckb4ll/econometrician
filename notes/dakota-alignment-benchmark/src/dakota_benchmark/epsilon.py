from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class EpsilonAlgebra:
    """Explicit choice for products of unresolved epsilon labels.

    mode='square_free': epsilon_i^2=0, but epsilon_i*epsilon_j survives for i != j.
    mode='first_order_ideal': every product of two or more epsilon factors vanishes.

    There is intentionally no default mode: the historical Edric record recovered
    epsilon_i^2=0 as a discussed semantics but did not settle mixed products.
    """
    mode: str

    def __post_init__(self) -> None:
        if self.mode not in {"square_free", "first_order_ideal"}:
            raise ValueError("mode must be 'square_free' or 'first_order_ideal'")


@dataclass
class EpsilonExpression:
    constant: float
    # monomial key is a sorted tuple of distinct epsilon labels.
    terms: dict[tuple[str, ...], float]
    algebra: EpsilonAlgebra

    @classmethod
    def scalar(cls, value: float, algebra: EpsilonAlgebra) -> "EpsilonExpression":
        return cls(float(value), {}, algebra)

    @classmethod
    def epsilon(cls, label: str, coefficient: float, algebra: EpsilonAlgebra) -> "EpsilonExpression":
        return cls(0.0, {(label,): float(coefficient)}, algebra)

    def _clean(self) -> "EpsilonExpression":
        self.terms = {k: v for k, v in self.terms.items() if v != 0.0}
        return self

    def __add__(self, other: "EpsilonExpression") -> "EpsilonExpression":
        self._same_algebra(other)
        out = dict(self.terms)
        for key, value in other.terms.items():
            out[key] = out.get(key, 0.0) + value
        return EpsilonExpression(self.constant + other.constant, out, self.algebra)._clean()

    def __mul__(self, other: "EpsilonExpression") -> "EpsilonExpression":
        self._same_algebra(other)
        out: dict[tuple[str, ...], float] = {}
        constant = self.constant * other.constant
        for key, value in self.terms.items():
            out[key] = out.get(key, 0.0) + value * other.constant
        for key, value in other.terms.items():
            out[key] = out.get(key, 0.0) + value * self.constant
        for k1, v1 in self.terms.items():
            for k2, v2 in other.terms.items():
                if self.algebra.mode == "first_order_ideal":
                    continue
                # epsilon_i^2 = 0 in square-free mode.
                if set(k1).intersection(k2):
                    continue
                key = tuple(sorted(k1 + k2))
                out[key] = out.get(key, 0.0) + v1 * v2
        return EpsilonExpression(constant, out, self.algebra)._clean()

    def _same_algebra(self, other: "EpsilonExpression") -> None:
        if self.algebra != other.algebra:
            raise ValueError("cannot combine expressions from different epsilon algebras")

    def as_mapping(self) -> Mapping[str, float]:
        result = {"1": self.constant}
        for key, value in sorted(self.terms.items()):
            result["*".join(f"epsilon[{x}]" for x in key)] = value
        return result
