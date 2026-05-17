from __future__ import annotations

from eq_equiv import (
    BoundEquation,
    EquationComparisonStatus,
    EquationSymbolBinding,
    compare_equations,
)


def _equation(expression: str) -> BoundEquation:
    return BoundEquation(
        expression=expression,
        variables=(
            EquationSymbolBinding(concept_id="x", symbol="x", role="dependent"),
            EquationSymbolBinding(concept_id="y", symbol="y", role="independent"),
            EquationSymbolBinding(concept_id="z", symbol="z", role="independent"),
        ),
    )


def test_equation_comparison_is_orientation_invariant() -> None:
    comparison = compare_equations(_equation("x = y"), _equation("y = x"))

    assert comparison.status == EquationComparisonStatus.EQUIVALENT


def test_equation_comparison_keeps_different_equations_distinct() -> None:
    comparison = compare_equations(_equation("x = y"), _equation("x = z"))

    assert comparison.status == EquationComparisonStatus.DIFFERENT


def test_equation_comparison_normalizes_scaled_orientation() -> None:
    comparison = compare_equations(
        _equation("x = y"),
        _equation("2 * y = 2 * x"),
    )

    assert comparison.status == EquationComparisonStatus.EQUIVALENT
