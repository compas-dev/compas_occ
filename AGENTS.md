# COMPAS OCC Agent Guide

## Scope and Principles

These instructions apply to the entire repository.

- Keep `compas_occ` focused on Open CASCADE integration through `pythonocc-core` and the `OCC` Python package.
- Follow the current contracts in the neighboring COMPAS source repository. Do not preserve a legacy backend API when COMPAS has intentionally changed its plugin or geometry architecture.
- Preserve unrelated working-tree changes and keep patches focused.
- Prefer the simplest implementation that expresses the required contract. Avoid speculative abstractions and compatibility layers.
- Update affected tests, documentation, serialization contracts, and change notes together with public or behavioral changes.

## COMPAS and OCC Integration

- Register plugins through the `compas.plugins` package entry point declared in `pyproject.toml`. Do not restore legacy `__all_plugins__` discovery.
- Keep `compas_occ.plugins` lightweight. Import OCC and backend implementation modules inside plugin functions so COMPAS can discover plugins without loading optional native dependencies.
- Use `requires=["OCC"]` for plugins that depend on `pythonocc-core`.
- Match the extension-point name, category, signature, and return contract in the current COMPAS source. Use `pluggable_name` when a locally descriptive function name differs from the COMPAS extension-point name.
- COMPAS Brep and NURBS types are stable public wrappers. Prefer operation-level adapters around native OCC payloads over replacing public COMPAS classes with backend-specific subclasses when migrating code to the current architecture.
- Keep conversions between COMPAS and OCC centralized in `compas_occ.conversions`. Preserve native parameter domains, orientation, topology, knot multiplicities, and the documented U/V layout.
- Distinguish `OCC` from `OCP`; this repository uses the `OCC.Core` namespace.

## Python and Typing

- Support Python 3.9 and newer, as declared in `pyproject.toml`. Do not use syntax introduced after Python 3.9 unless the supported range is deliberately changed in the same patch.
- Use built-in generics such as `list[str]`. Use `typing.Optional` and `typing.Union` where Python 3.9 compatibility rules out PEP 604 unions.
- Annotate the values accepted by the runtime API. Do not change runtime behavior merely to satisfy a type checker.
- Prefer precise annotations and protocols over broad `Any` or casts. Use overloads for argument-dependent public return types.
- Use `TYPE_CHECKING` for imports needed only by annotations, especially heavy or optional dependencies.
- Keep annotations aligned with current COMPAS contracts. In particular, `Line` and `Polyline` are geometry primitives rather than `Curve` subclasses.
- Preserve subclass behavior, accepted inputs, return values, ordering, orientation, mutation, and documented exceptions unless a change is intentional and scoped.

## Class Organization

Organize substantial class bodies in this order:

1. data and serialization hooks
2. dunder methods
3. properties
4. alternative constructors
5. conversions
6. regular public methods
7. transformations
8. private helpers

Keep property accessors and overload groups together. Use specialized sections for OCC properties or topology when they improve navigation.

## Documentation and Public API

- Write MkDocs/mkdocstrings-compatible NumPy-style docstrings using Markdown.
- Package initializers should expose intentional public names explicitly; imports and `__all__` together define the supported API.
- Omit parameter types already present in signatures. Keep explicit canonical Python types in `Returns` sections.
- Document tuple returns as one tuple matching the annotation. Omit `Returns` for functions returning `None`, and remove empty sections.
- Use backticks for identifiers, Markdown links and footnotes, and `$...$` or `$$...$$` for mathematics. Do not introduce Sphinx roles or directives.
- Keep executable examples valid as doctests. Do not add manual `Attributes` sections when mkdocstrings can generate them.
- Except for single-line docstrings, leave a blank line before closing quotes.

## Tests and Validation

- Use the `compas3` Conda environment when available.
- Run the smallest relevant tests first, then broaden validation in proportion to risk.
- Use the repository Invoke tasks: `invoke test`, `invoke check`, `invoke lint`, `invoke format`, and `invoke docs` as applicable. Focused Pytest, Ruff, and Pyright commands are appropriate during development.
- Always run `git diff --check` for changed patches.
- Verify plugin changes both through a focused `PluginManager` test and through built distribution metadata. Plugin discovery must not import `OCC`.
- For typing work, supplement runtime tests with a focused static check.
- Build relevant MkDocs pages when docstrings, signatures, or public API pages change.
