"""Live integration tests for MotorCAD constructor parameter combinations."""
# licence_type, use_blackbox_licence and headless
# ideally run this 2 times. 1st time with single licence of Motor-CAD enterprise, 2nd time with single licence of Motor-CAD enterprise plus
# check on licence server log for the licence requests and failures and also view Motor-CAD instance to confirm if visible or not.

import os

from ansys.motorcad.core import MotorCAD
from ansys.motorcad.core.rpc_client_core import MotorCADError


def runTest(**motorcad_kwargs):
    # ensure clean environment for each test
    os.environ.pop('MOTORDES_BLACKBOX', None)
    os.environ.pop('MOTORCAD_LICENCE_TYPE', None)
    os.environ.pop('MOTORCAD_HEADLESS', None)
    try:
      mc = MotorCAD(**motorcad_kwargs)
    except MotorCADError as e:
      print(f"  FAIL  MotorCADError: {e}")
      return None# {"name": name, "status": "FAIL", "error": str(e)}
    except Exception as e:
        print(f"  ERROR  Unexpected: {e}")
        return None# {"name": name, "status": "ERROR", "error": str(e)}

    try:
      is_open_result = mc.is_open()
      licence_result = mc.get_licence()
      messages_result = mc.get_messages(1)
    except MotorCADError as e:
      print(f"  FAIL  MotorCADError: {e}")
      return mc# {"name": name, "status": "FAIL", "error": str(e)}
    except Exception as e:
        print(f"  ERROR  Unexpected: {e}")
        return mc# {"name": name, "status": "ERROR", "error": str(e)}

    return mc


if __name__ == "__main__":
    # enable to run test
    test1 = True
    test2 = True
    test3 = True
    test4 = True
    test5 = True

    # old licence type with UI
    if test1 == True:
        mc = runTest(licence_type=0)
        # should have attempted to use old 'motorcad' and motorcad_pm licence
        # if not available then will fallback to new 'motorcad_gui' licence
        if mc is not None:
            mc.quit()

    # old licence type without UI
    if test2 == True:
        mc = runTest(licence_type=0, headless=1)
        # should have attempted to use old 'motorcad' and motorcad_pm licences in headless mode
        # if no 'motorcad' licence then will fail with no fallback
        if mc is not None:
            mc.quit()

    # using black box licence (also setting new licence method)
    if test3 == True:
        mc = runTest(use_blackbox_licence=1, licence_type=1)
        # should be in blackbox mode using blackbox licence, ignores licence_type setting
        # should not fallback
        if mc is not None:
            mc.quit()

    # new licence type with UI (not using black box licence)
    if test4 == True:
        mc = runTest(use_blackbox_licence=0, licence_type=1)
        # should show UI using motor_gui, motorcad_pm and elec_solve_level1 licences
        # should fallback to 'motorcad' and motorcad_pm licences
        if mc is not None:
            mc.quit()

    # new licence type without UI (not using black box licence)
    if test5 == True:
        mc = runTest(use_blackbox_licence=0, licence_type=1, headless=1)
        # should not show UI and will use motorcad_pm and elec_solve_level1 licences
        # should not fallback
        if mc is not None:
            mc.quit()
