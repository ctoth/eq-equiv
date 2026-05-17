from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from eq_equiv import (
    BinaryExpr,
    EquationExpr,
    EquationFailure,
    EquationSymbolBinding,
    FunctionExpr,
    NumberExpr,
    SymbolExpr,
    UnaryExpr,
    parse_equation,
    render_equation,
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
