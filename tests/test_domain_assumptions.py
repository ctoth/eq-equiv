from __future__ import annotations

from eq_equiv import (
    BoundEquation,
    EquationComparisonStatus,
    EquationSymbolBinding,
    NonNegative,
    Positive,
    Real,
    compare_equations,
)


def _equation(expression: str, *bindings: EquationSymbolBinding) -> BoundEquation:
    return BoundEquation(expression=expression, variables=bindings)


def test_log_product_equivalence_under_positive_reals() -> None:
    bindings = (
        EquationSymbolBinding(concept_id="x", symbol="x", role="dependent"),
        EquationSymbolBinding(concept_id="y", symbol="y", role="independent"),
        EquationSymbolBinding(concept_id="z", symbol="z", role="independent"),
    )
    comparison = compare_equations(
        _equation("log(x * y) = z", *bindings),
        _equation("log(x) + log(y) = z", *bindings),
        domain_assumptions=(Positive("x"), Positive("y")),
    )

    assert comparison.status == EquationComparisonStatus.EQUIVALENT


def test_log_product_without_positive_reals_is_unknown() -> None:
    bindings = (
        EquationSymbolBinding(concept_id="x", symbol="x", role="dependent"),
        EquationSymbolBinding(concept_id="y", symbol="y", role="independent"),
        EquationSymbolBinding(concept_id="z", symbol="z", role="independent"),
    )
    comparison = compare_equations(
        _equation("log(x * y) = z", *bindings),
        _equation("log(x) + log(y) = z", *bindings),
    )

    assert comparison.status == EquationComparisonStatus.UNKNOWN


def test_wrong_log_product_identity_under_positive_reals_is_different() -> None:
    bindings = (
        EquationSymbolBinding(concept_id="x", symbol="x", role="dependent"),
        EquationSymbolBinding(concept_id="y", symbol="y", role="independent"),
        EquationSymbolBinding(concept_id="z", symbol="z", role="independent"),
    )
    comparison = compare_equations(
        _equation("log(x * y) = z", *bindings),
        _equation("log(x) - log(y) = z", *bindings),
        domain_assumptions=(Positive("x"), Positive("y")),
    )

    assert comparison.status == EquationComparisonStatus.DIFFERENT


def test_exp_sum_product_equivalence_under_reals() -> None:
    bindings = (
        EquationSymbolBinding(concept_id="a", symbol="a", role="independent"),
        EquationSymbolBinding(concept_id="b", symbol="b", role="independent"),
        EquationSymbolBinding(concept_id="z", symbol="z", role="dependent"),
    )
    comparison = compare_equations(
        _equation("exp(a + b) = z", *bindings),
        _equation("exp(a) * exp(b) = z", *bindings),
        domain_assumptions=(Real("a"), Real("b")),
    )

    assert comparison.status == EquationComparisonStatus.EQUIVALENT


def test_exp_sum_product_without_declared_domain_is_unknown() -> None:
    bindings = (
        EquationSymbolBinding(concept_id="a", symbol="a", role="independent"),
        EquationSymbolBinding(concept_id="b", symbol="b", role="independent"),
        EquationSymbolBinding(concept_id="z", symbol="z", role="dependent"),
    )
    comparison = compare_equations(
        _equation("exp(a + b) = z", *bindings),
        _equation("exp(a) * exp(b) = z", *bindings),
    )

    assert comparison.status == EquationComparisonStatus.UNKNOWN


def test_sqrt_square_equivalence_under_nonnegative_reals() -> None:
    bindings = (
        EquationSymbolBinding(concept_id="x", symbol="x", role="dependent"),
        EquationSymbolBinding(concept_id="z", symbol="z", role="independent"),
    )
    comparison = compare_equations(
        _equation("sqrt(x * x) = z", *bindings),
        _equation("x = z", *bindings),
        domain_assumptions=(NonNegative("x"),),
    )

    assert comparison.status == EquationComparisonStatus.EQUIVALENT


def test_sqrt_square_without_nonnegative_domain_is_unknown() -> None:
    bindings = (
        EquationSymbolBinding(concept_id="x", symbol="x", role="dependent"),
        EquationSymbolBinding(concept_id="z", symbol="z", role="independent"),
    )
    comparison = compare_equations(
        _equation("sqrt(x * x) = z", *bindings),
        _equation("x = z", *bindings),
    )

    assert comparison.status == EquationComparisonStatus.UNKNOWN


def test_sqrt_square_abs_equivalence_under_reals() -> None:
    bindings = (
        EquationSymbolBinding(concept_id="x", symbol="x", role="dependent"),
        EquationSymbolBinding(concept_id="z", symbol="z", role="independent"),
    )
    comparison = compare_equations(
        _equation("sqrt(x * x) = z", *bindings),
        _equation("abs(x) = z", *bindings),
        domain_assumptions=(Real("x"),),
    )

    assert comparison.status == EquationComparisonStatus.EQUIVALENT


def test_sqrt_square_abs_without_real_domain_is_unknown() -> None:
    bindings = (
        EquationSymbolBinding(concept_id="x", symbol="x", role="dependent"),
        EquationSymbolBinding(concept_id="z", symbol="z", role="independent"),
    )
    comparison = compare_equations(
        _equation("sqrt(x * x) = z", *bindings),
        _equation("abs(x) = z", *bindings),
    )

    assert comparison.status == EquationComparisonStatus.UNKNOWN
