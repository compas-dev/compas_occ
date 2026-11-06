# Candidate artifacts

The Linux Python 3.12 build produces the COMPAS OCC wheel used by the COMPAS
Framework candidate-integration gate. The build creates the wheel once from a
clean archive of the tested commit, verifies its PEP 561 marker and an installed
type-checking consumer, and uploads exactly one `py3-none-any` wheel.

The artifact contract is:

- artifact name: `candidate-linux-py312`;
- contents: exactly one `compas_occ` wheel and no source distribution or
  auxiliary files;
- target: Linux x86-64 with Python 3.12; and
- retention: seven days.

The framework manifest records the successful workflow run, exact commit,
artifact identifier and digest, wheel filename, and wheel digest. The
integration workflow downloads that immutable artifact; it does not rebuild
COMPAS OCC from a source URL.

Producing this artifact does not publish it. Release and publication remain
separate maintainer-controlled workflows.
