from __future__ import annotations

from eq_equiv import (
    BinaryExpr,
    EquationFailure,
    EquationFailureCode,
    EquationSymbolBinding,
    NumberExpr,
    SymbolExpr,
    parse_equation,
    render_equation,
)


def test_double_equals_is_invalid_relation() -> None:
    result = parse_equation("x == 2*y", _bindings())

    assert result == EquationFailure(
        code=EquationFailureCode.INVALID_RELATION,
        detail="equation must contain exactly one '=' and no other relation operators",
    )


def test_inequality_is_invalid_relation() -> None:
    result = parse_equation("x <= 2*y", _bindings())

    assert result == EquationFailure(
        code=EquationFailureCode.INVALID_RELATION,
        detail="equation must contain exactly one '=' and no other relation operators",
    )


def test_chained_equality_is_invalid_relation() -> None:
    result = parse_equation("x = y = 2", _bindings())

    assert result == EquationFailure(
        code=EquationFailureCode.INVALID_RELATION,
        detail="equation must contain exactly one '=' and no other relation operators",
    )


def test_unknown_symbol_is_explicit_failure() -> None:
    result = parse_equation("x = 2*z", _bindings())

    assert result == EquationFailure(
        code=EquationFailureCode.UNKNOWN_SYMBOL,
        detail="unknown symbol: z",
    )


def test_unsupported_function_surface_is_explicit() -> None:
    result = parse_equation("x = And(y, y)", _bindings())

    assert result == EquationFailure(
        code=EquationFailureCode.UNSUPPORTED_SURFACE,
        detail="unsupported function: And",
    )


def test_render_preserves_left_nested_exponentiation() -> None:
    expr = BinaryExpr(
        operator="^",
        left=BinaryExpr(
            operator="^",
            left=NumberExpr("2"),
            right=NumberExpr("3"),
        ),
        right=NumberExpr("4"),
    )

    assert render_equation(expr) == "(2 ^ 3) ^ 4"


def test_render_preserves_division_on_multiplication_rhs() -> None:
    expr = BinaryExpr(
        operator="*",
        left=SymbolExpr(symbol="y", concept_id="time"),
        right=BinaryExpr(
            operator="/",
            left=NumberExpr("2"),
            right=NumberExpr("3"),
        ),
    )

    assert render_equation(expr) == "y * (2 / 3)"


def _bindings() -> tuple[EquationSymbolBinding, ...]:
    return (
        EquationSymbolBinding(symbol="x", concept_id="length", role="dependent"),
        EquationSymbolBinding(symbol="y", concept_id="time", role="independent"),
    )
