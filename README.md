# BIMTester

Gherkin based tests for BIM data (IFC). The package itself lives in
[src/ifcbimtester](src/ifcbimtester/README.md); see its README for usage.

## Origin

This repository is a standalone continuation of BIMTester, which was developed inside
[IfcOpenShell](https://github.com/IfcOpenShell/IfcOpenShell) at `src/ifcbimtester`.
It was removed from IfcOpenShell in commit
[4fe08e2a9430de7c4cd6159747dc1dcb29c09fa5](https://github.com/IfcOpenShell/IfcOpenShell/commit/4fe08e2a9430de7c4cd6159747dc1dcb29c09fa5)
on branch `v0.9.0`.

The history was extracted with `git filter-repo`, keeping every commit that touched
`src/ifcbimtester`, the `bimtester.rst` documentation page, the license files and
`.gitattributes`. Authors, dates and commit messages are preserved; commit hashes
differ from upstream.

## Installation

```sh
pip install ./src/ifcbimtester          # core
pip install "./src/ifcbimtester[gui]"   # with the PySide2 GUI
```

The only IFC dependency is the `ifcopenshell` package from PyPI.

## License

LGPL-3.0-or-later, see [COPYING](COPYING) and [COPYING.LESSER](COPYING.LESSER).
