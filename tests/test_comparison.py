from __future__ import annotations

import eq_equiv.comparison as equation_comparison
from eq_equiv import (
    BoundEquation,
    EquationComparisonStatus,
    EquationFailure,
    EquationFailureCode,
    EquationNormalization,
    EquationSymbolBinding,
    canonicalize_equation,
    compare_equations,
    equation_signature,
    structural_signature,
)


def _make_equation(
    *,
    expression: str | None = None,
    sympy: str | None = None,
    variables: tuple[EquationSymbolBinding, ...] | None = None,
) -> BoundEquation:
    resolved_variables: tuple[EquationSymbolBinding, ...]
    if variables is None:
        resolved_variables = (
            EquationSymbolBinding(concept_id="length", symbol="x", role="dependent"),
            EquationSymbolBinding(concept_id="time", symbol="y", role="independent"),
        )
    else:
        resolved_variables = variables
    return BoundEquation(
        expression=expression,
        sympy=sympy,
        variables=resolved_variables,
    )


def test_signature_uses_typed_variables() -> None:
    equation = _make_equation()
    assert equation_signature(equation) == ("length", ("time",))


def test_supported_equation_returns_typed_normalization() -> None:
    result = canonicalize_equation(_make_equation(expression="x = 2*y"))

    assert isinstance(result, EquationNormalization)
    assert result.canonical == "length - 2*time"


def test_missing_variables_is_explicit_failure() -> None:
    result = canonicalize_equation(_make_equation(expression="x = 2*y", variables=()))

    assert result == EquationFailure(
        code=EquationFailureCode.MISSING_VARIABLES,
        detail="equation has no declared symbol bindings",
    )


def test_missing_equation_text_is_explicit_failure() -> None:
    result = canonicalize_equation(_make_equation(expression=None, sympy=None))

    assert result == EquationFailure(
        code=EquationFailureCode.MISSING_EQUATION_TEXT,
        detail="equation has neither expression nor sympy text",
    )


def test_raw_sympy_eq_text_is_not_executable_input() -> None:
    result = canonicalize_equation(_make_equation(expression=None, sympy="Eq(x, 2*y)"))

    assert result == EquationFailure(
        code=EquationFailureCode.INVALID_RELATION,
        detail="equation must contain exactly one '=' and no other relation operators",
    )


def test_equivalent_equations_return_typed_comparison() -> None:
    comparison = compare_equations(
        _make_equation(expression="x = y + y"),
        _make_equation(expression="x = 2*y"),
    )

    assert comparison.status == EquationComparisonStatus.EQUIVALENT


def test_failed_normalization_returns_incomparable_comparison() -> None:
    comparison = compare_equations(
        _make_equation(expression="x = 2*y"),
        _make_equation(expression="x == 2*y"),
    )

    assert comparison.status == EquationComparisonStatus.INCOMPARABLE
    assert isinstance(comparison.right, EquationFailure)


def test_structural_signature_is_alpha_invariant() -> None:
    base = _make_equation(expression="x = y + y")
    renamed = _make_equation(
        expression="a = b + b",
        variables=(
            EquationSymbolBinding(concept_id="length", symbol="a", role="dependent"),
            EquationSymbolBinding(concept_id="time", symbol="b", role="independent"),
        ),
    )

    assert structural_signature(base) == structural_signature(renamed)


def test_normalization_cache_reuses_same_equation_key() -> None:
    equation_comparison._normalize_equation_text.cache_clear()

    equation = _make_equation(expression="x = 2*y")
    first = canonicalize_equation(equation)
    second = canonicalize_equation(equation)

    assert isinstance(first, EquationNormalization)
    assert second == first
    assert equation_comparison._normalize_equation_text.cache_info().hits >= 1


def test_sympy_is_lazy_loaded() -> None:
    original_sympy = equation_comparison._sympy
    equation_comparison._sympy = None
    equation_comparison._normalize_equation_text.cache_clear()
    assert equation_comparison._sympy is None

    loaded_sympy = None
    try:
        result = equation_comparison.canonicalize_equation(_make_equation(expression="x = 2*y"))
        loaded_sympy = equation_comparison._sympy
    finally:
        equation_comparison._normalize_equation_text.cache_clear()
        equation_comparison._sympy = original_sympy

    assert isinstance(result, EquationNormalization)
    assert loaded_sympy is not None
