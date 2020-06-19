import os
import sys

import pytest
from _pytest.main import ExitCode

from settings import Settings

if __name__ == '__main__':

    if len(sys.argv) > 1:
        Settings.TESTS_PATH = sys.argv[1]

    if len(sys.argv) > 2:
        Settings.BASE_URL = sys.argv[2]

    args_common = [
        '--capture=no',
        '--log-level=WARN',
        '--tb=short',
        f'--alluredir={Settings().ALLURE_RESULTS_PATH}',
        Settings.TESTS_PATH
    ]

    args_run_1 = [f'--junit-xml={Settings().E2E_RESULTS_PATH}/junit.xml'] + args_common
    args_run_2 = ['--last-failed'] + args_common

    pytest.main(args=args_run_1)
    # if pytest.main(args=args_run_1) == ExitCode.TESTS_FAILED:
    #     pytest.main(args=args_run_2)

    if not Settings().IS_JENKINS:
        os.system(f'cd {Settings().ALLURE_RESULTS_PATH} && allure generate . && allure open -p 5000')
