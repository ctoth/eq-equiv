# eq-equiv

Equation parsing and equivalence comparison for typed symbolic equations.

`eq-equiv` parses a deliberately small equation surface, binds authored
symbols to stable concept identifiers, renders typed expression trees, and
compares equations through deterministic structural and SymPy-backed
normalization.

## Supported Surface

Equations must contain exactly one `=` relation. Expressions support:

- symbols declared by `EquationSymbolBinding`;
- integers, decimals, and exponent notation;
- unary `+` and `-`;
- binary `+`, `-`, `*`, `/`, and `^`;
- one-argument functions `abs`, `log`, `ln`, `exp`, and `sqrt`.

Unsupported functions, unknown symbols, inequalities, chained equalities, and
raw executable SymPy surfaces return typed `EquationFailure` values instead of
being evaluated.

## Comparison Outcomes

- `EQUIVALENT`: the equations are proven equivalent under the declared domain.
- `DIFFERENT`: the equations are proven different for the supported theory.
- `INCOMPARABLE`: parsing or normalization failed.
- `UNKNOWN`: both equations parsed, but the available algebraic procedure
  cannot make a sound equivalence or difference decision.

Domain-sensitive identities return `UNKNOWN` unless the caller supplies the
needed assumptions. For example, `log(x * y) = z` and
`log(x) + log(y) = z` require positive assumptions for `x` and `y`.

## SymPy Generation

`generate_sympy_rhs` and `generate_sympy_rhs_with_error` intentionally return a
right-hand-side expression. `generate_sympy_equation` preserves both sides when
callers need equation identity.

## Example

```python
from eq_equiv import (
    BoundEquation,
    EquationComparisonStatus,
    EquationSymbolBinding,
    Positive,
    compare_equations,
)

bindings = (
    EquationSymbolBinding(symbol="x", concept_id="x"),
    EquationSymbolBinding(symbol="y", concept_id="y"),
    EquationSymbolBinding(symbol="z", concept_id="z"),
)

left = BoundEquation("log(x * y) = z", variables=bindings)
right = BoundEquation("log(x) + log(y) = z", variables=bindings)

result = compare_equations(
    left,
    right,
    domain_assumptions=(Positive("x"), Positive("y")),
)

assert result.status == EquationComparisonStatus.EQUIVALENT
```
