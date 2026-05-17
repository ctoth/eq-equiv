from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from eq_equiv import (
    BinaryExpr,
    BoundEquation,
    EquationComparisonStatus,
    EquationExpr,
    EquationFailure,
    EquationFailureCode,
    EquationNormalization,
    EquationSymbolBinding,
    FunctionExpr,
    NumberExpr,
    SymbolExpr,
    UnaryExpr,
    canonicalize_equation,
    compare_equations,
    parse_equation,
    render_equation,
    structural_signature,
)

_number_tokens = st.sampled_from(["0", "1", "2", "3", "0.5", "1.25"])
_symbol_exprs = st.sampled_from([
    SymbolExpr(symbol="y", concept_id="time"),
    SymbolExpr(symbol="z", concept_id="task"),
])
_simple_exprs = st.recursive(
    st.one_of(
        _number_tokens.map(NumberExpr),
        _symbol_exprs,
    ),
    lambda children: st.one_of(
        st.builds(UnaryExpr, st.sampled_from(["+", "-"]), children),
        st.builds(BinaryExpr, st.sampled_from(["+", "-", "*", "^"]), children, children),
        st.builds(FunctionExpr, st.sampled_from(["log", "exp", "sqrt"]), st.tuples(children)),
    ),
    max_leaves=6,
)
_polynomial_exprs = st.recursive(
    st.one_of(_number_tokens.map(NumberExpr), st.just(SymbolExpr(symbol="y", concept_id="time"))),
    lambda children: st.one_of(
        st.builds(UnaryExpr, st.sampled_from(["+", "-"]), children),
        st.builds(BinaryExpr, st.sampled_from(["+", "-", "*"]), children, children),
    ),
    max_leaves=6,
)


@pytest.mark.property
@given(expr=_simple_exprs)
@settings(deadline=None, max_examples=40)
def test_render_parse_round_trip(expr: EquationExpr) -> None:
    text = render_equation(expr)
    parsed = parse_equation(
        f"x = {text}",
        (
            EquationSymbolBinding(symbol="x", concept_id="length", role="dependent"),
            EquationSymbolBinding(symbol="y", concept_id="time", role="independent"),
            EquationSymbolBinding(symbol="z", concept_id="task", role="independent"),
        ),
    )

    assert not isinstance(parsed, EquationFailure)
    assert render_equation(parsed.rhs) == text


@pytest.mark.property
@given(expr=_polynomial_exprs)
@settings(deadline=None, max_examples=40)
def test_canonicalization_is_idempotent(expr: EquationExpr) -> None:
    equation = _equation_from_expr(expr)
    first = canonicalize_equation(equation)
    second = canonicalize_equation(equation)

    assert isinstance(first, EquationNormalization)
    assert second == first


@pytest.mark.property
@given(expr=_polynomial_exprs)
@settings(deadline=None, max_examples=40)
def test_structural_signature_is_invariant_under_alpha_renaming(expr: EquationExpr) -> None:
    renamed_expr = _rename_expr(
        expr,
        mapping={"y": "b", "z": "c"},
        concept_mapping={"y": "time", "z": "task"},
    )
    base = _equation_from_expr(expr)
    renamed = _equation_from_expr(
        renamed_expr,
        dependent_symbol="a",
        dependent_concept="length",
        independent_symbol="b",
        independent_concept="time",
    )

    assert structural_signature(base) == structural_signature(renamed)


@pytest.mark.property
@given(
    coeff_a=st.integers(min_value=1, max_value=5),
    coeff_b=st.integers(min_value=1, max_value=5),
)
@settings(deadline=None, max_examples=25)
def test_equivalent_rewrites_normalize_identically(coeff_a: int, coeff_b: int) -> None:
    left = _equation_from_expr(
        BinaryExpr(
            operator="+",
            left=BinaryExpr(
                operator="*",
                left=NumberExpr(str(coeff_a)),
                right=SymbolExpr(symbol="y", concept_id="time"),
            ),
            right=BinaryExpr(
                operator="*",
                left=NumberExpr(str(coeff_b)),
                right=SymbolExpr(symbol="y", concept_id="time"),
            ),
        ),
    )
    right = _equation_from_expr(
        BinaryExpr(
            operator="*",
            left=NumberExpr(str(coeff_a + coeff_b)),
            right=SymbolExpr(symbol="y", concept_id="time"),
        ),
    )

    comparison = compare_equations(left, right)
    assert comparison.status == EquationComparisonStatus.EQUIVALENT


@pytest.mark.property
@given(
    relation=st.sampled_from(["==", "<=", ">=", "=", "="]),
    unsupported_function=st.sampled_from(["And", "Piecewise", "Eq"]),
)
@settings(deadline=None, max_examples=20)
def test_invalid_or_unsupported_surfaces_fail_honestly(
    relation: str,
    unsupported_function: str,
) -> None:
    if relation == "=":
        text = f"x = {unsupported_function}(y)"
        expected_code = EquationFailureCode.UNSUPPORTED_SURFACE
    else:
        text = f"x {relation} y"
        expected_code = EquationFailureCode.INVALID_RELATION

    template = _equation_from_expr(SymbolExpr(symbol="y", concept_id="time"))
    result = canonicalize_equation(BoundEquation(
        expression=text,
        variables=template.variables,
    ))

    assert isinstance(result, EquationFailure)
    assert result.code == expected_code


def _equation_from_expr(
    expr: EquationExpr,
    *,
    dependent_symbol: str = "x",
    dependent_concept: str = "length",
    independent_symbol: str = "y",
    independent_concept: str = "time",
) -> BoundEquation:
    return BoundEquation(
        expression=f"{dependent_symbol} = {render_equation(expr)}",
        variables=(
            EquationSymbolBinding(
                concept_id=dependent_concept,
                symbol=dependent_symbol,
                role="dependent",
            ),
            EquationSymbolBinding(
                concept_id=independent_concept,
                symbol=independent_symbol,
                role="independent",
            ),
        ),
    )


def _rename_expr(
    expr: EquationExpr,
    mapping: dict[str, str],
    concept_mapping: dict[str, str],
) -> EquationExpr:
    if isinstance(expr, NumberExpr):
        return expr
    if isinstance(expr, SymbolExpr):
        return SymbolExpr(
            symbol=mapping.get(expr.symbol, expr.symbol),
            concept_id=concept_mapping.get(expr.symbol, expr.concept_id),
        )
    if isinstance(expr, UnaryExpr):
        return UnaryExpr(operator=expr.operator, operand=_rename_expr(expr.operand, mapping, concept_mapping))
    if isinstance(expr, BinaryExpr):
        return BinaryExpr(
            operator=expr.operator,
            left=_rename_expr(expr.left, mapping, concept_mapping),
            right=_rename_expr(expr.right, mapping, concept_mapping),
        )
    if isinstance(expr, FunctionExpr):
        return FunctionExpr(
            name=expr.name,
            arguments=tuple(
                _rename_expr(argument, mapping, concept_mapping)
                for argument in expr.arguments
            ),
        )
    raise TypeError(f"unsupported expression: {expr!r}")
