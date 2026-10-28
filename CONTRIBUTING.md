# Contribute

Overall guidance on contributing to a PyAnsys library appears in the
[Contributing] topic in the *PyAnsys developer's guide*. Ensure that you
are thoroughly familiar with this guide before attempting to contribute to
PyMotorCAD.

[Contributing]: https://dev.docs.pyansys.com/how-to/contributing.html

<!-- Begin content specific to your library here. -->

## Running tests headlessly

Run `python -m pytest tests --headless` to enforce the fully headless Motor-CAD
build for local launches (Motor-CAD 2027R1 or later). A session-scoped autouse
fixture patches executable resolution, so direct `MotorCAD(...)` calls in new
tests are covered without passing `full_headless` individually. GUI executable
overrides are rejected. Without `--headless`, launch behavior is unchanged.

Tests marked `headless_incompatible`, including the UI module and tests of
manual executable override behavior, are skipped before fixture setup.
The policy does not change existing or remote instances, launches in separate
Python processes, or tests that replace executable resolution with a mock.
