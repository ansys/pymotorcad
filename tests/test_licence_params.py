"""Live pytest integration tests for MotorCAD constructor parameter combinations.

These tests exercise real licence acquisition behaviour and therefore remain opt-in.
Set ``PYMOTORCAD_RUN_LIVE_LICENCE_TESTS=1`` to execute them.
"""

import os

import pytest

from ansys.motorcad.core import MotorCAD
from ansys.motorcad.core.rpc_client_core import MotorCADError

# Environment variables used to gate live tests and isolate constructor behaviour.
LIVE_LICENCE_TEST_ENV_VAR = "PYMOTORCAD_RUN_LIVE_LICENCE_TESTS"
MOTORCAD_ENV_VARS = (
    "MOTORDES_BLACKBOX",
    "MOTORCAD_LICENCE_TYPE",
    "MOTORCAD_HEADLESS",
)


def _live_licence_tests_enabled():
    return os.getenv(LIVE_LICENCE_TEST_ENV_VAR, "").strip().lower() in {"1", "true", "yes", "on"}


# Skip the whole module unless explicitly enabled for live licence validation.
pytestmark = pytest.mark.skipif(
    not _live_licence_tests_enabled(),
    reason=(
        f"Live Motor-CAD licence tests are disabled. "
        f"Set {LIVE_LICENCE_TEST_ENV_VAR}=1 to run them."
    ),
)


@pytest.fixture()
def clean_motorcad_env(monkeypatch):
    """Clear Motor-CAD constructor environment overrides before each scenario."""
    for env_var in MOTORCAD_ENV_VARS:
        monkeypatch.delenv(env_var, raising=False)


def _start_motorcad_and_probe(**motorcad_kwargs):
    """Create a Motor-CAD instance and perform a minimal smoke test."""
    mc = MotorCAD(**motorcad_kwargs)
    assert mc.is_open()
    assert mc.get_licence() is None
    mc.get_messages(1)
    return mc


# Run the same smoke test across the legacy/new licence modes and UI/headless variants.
@pytest.mark.parametrize(
    ("motorcad_kwargs", "scenario"),
    [  # should attempt to use old 'motorcad' and motorcad_pm licence
        # if not available then will fallback to new 'motorcad_gui' licence
        pytest.param(
            {"licence_type": 0},
            "old licence type with UI",
            id="old-licence-ui",

        ),
        # should attempt to use old 'motorcad' and motorcad_pm licences in headless mode
        # if no 'motorcad' licence then will fail with no fallback
        pytest.param(
            {"licence_type": 0, "headless": 1},
            "old licence type without UI",
            id="old-licence-headless",
            marks=pytest.mark.xfail(
                reason="No motorcad licence available",
                strict=True,
            ),
        ),
        # should be in blackbox mode using blackbox licence, ignores licence_type setting
        # should not fallback
        pytest.param(
            {"use_blackbox_licence": 1, "licence_type": 1},
            "blackbox licence mode",
            id="blackbox-licence",
            marks=pytest.mark.xfail(
                reason="No Blackbox licence available",
                strict=True,
            ),
        ),
        # should show UI using motor_gui, motorcad_pm and elec_solve_level1 licences
        # should fallback to 'motorcad' and motorcad_pm licences
        pytest.param(
            {"use_blackbox_licence": 0, "licence_type": 1},
            "new licence type with UI",
            id="new-licence-ui",

        ),
        # should not show UI and will use motorcad_pm and elec_solve_level1 licences
        # should not fallback
        pytest.param(
            {"use_blackbox_licence": 0, "licence_type": 1, "headless": 1},
            "new licence type without UI",
            id="new-licence-headless",
        ),
    ],
)
def test_motorcad_constructor_parameter_combinations(clean_motorcad_env, motorcad_kwargs, scenario):
    """Validate that each constructor parameter combination can start and respond."""
    mc = None
    try:
        mc = _start_motorcad_and_probe(**motorcad_kwargs)
    except MotorCADError as exc:
        pytest.fail(f"{scenario} failed with MotorCADError: {exc}")
    except Exception as exc:
        pytest.fail(f"{scenario} failed with unexpected error: {exc}")
    finally:
        if mc is not None:
            mc.quit()
