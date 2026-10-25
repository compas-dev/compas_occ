---
name: update-type-hints
description: Add, modernize, or review Python type hints in compas_occ while preserving Python 3.9 compatibility and OCC runtime behavior.
---

# Update compas_occ type hints

Apply the repository-wide rules in `AGENTS.md`, especially **Python and Typing**, **COMPAS and OCC Integration**, and **Tests and Validation**.

## Requirements

- Preserve Python 3.9 compatibility. Prefer built-in generics, but use `Optional[X]` and `Union[X, Y]` instead of PEP 604 syntax.
- Match annotations to the current neighboring COMPAS source contracts rather than legacy assumptions. Account for `Line` and `Polyline` not being subclasses of `Curve`.
- Model the values accepted by the existing runtime API. Do not add conversions or validation merely to satisfy an annotation.
- Prefer precise protocols, aliases, overloads, or corrected source annotations over `cast`, concrete runtime checks, or broad `Any`.
- Use `TYPE_CHECKING` for dependencies imported only for annotations. Do not make plugin discovery import OCC or other optional native dependencies.
- Keep native OCC types precise at backend boundaries and COMPAS types precise at the public boundary.
- Preserve subclass behavior, defaults, accepted inputs, return values, ordering, orientation, side effects, and exception behavior unless the task explicitly authorizes a change.

## Validation

Run the narrowest relevant tests first. Run focused Pyright and Ruff checks on touched Python files, followed by `git diff --check`. For plugin annotations, also verify that signatures bind to the corresponding COMPAS extension points.
