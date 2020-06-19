import os
from datetime import datetime

from constants.common import BrowserType


class Settings(object):
    instance = None

    IS_JENKINS = True
    BROWSER = BrowserType.CHROME_HEADLESS

    TESTS_PATH = 'tests'
    BASE_URL = 'http://161.35.132.42/'

    BASE_URL_ADMIN = ''
    MARKETPLACE = ''
    COMMAND_EXECUTOR = ''
    BROWSER_DOWNLOAD_PATH = ''
    DOWNLOAD_PATH = ''
    SCREENSHOT_PATH = ''
    ALLURE_RESULTS_PATH = ''

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(Settings, cls).__new__(cls)

            cls.BASE_URL_ADMIN = cls.BASE_URL.replace('//', '//admin.')
            cls.MARKETPLACE = cls.BASE_URL.lstrip('http://').replace('.', '-')

            chromedriver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                             'chromedriver%s' % ('' if cls.IS_JENKINS else '.exe'))
            cls.COMMAND_EXECUTOR = {
                cls.BROWSER == BrowserType.CHROME_NATIVE:                           chromedriver_path,
                cls.BROWSER == BrowserType.CHROME_HEADLESS:                         chromedriver_path,
                cls.BROWSER == BrowserType.CHROME_REMOTE and cls.IS_JENKINS:        'http://hub:4444/wd/hub',
                cls.BROWSER == BrowserType.CHROME_REMOTE and not cls.IS_JENKINS:    'http://192.168.99.100:4444/wd/hub',
            }[True]

            if cls.IS_JENKINS:
                cls.E2E_RESULTS_PATH = 'e2e_results'
                cls.BROWSER_DOWNLOAD_PATH = 'e2e_results/downloads'
            else:
                e2e_results_dir = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                cls.E2E_RESULTS_PATH = os.path.join(os.environ.get('USERPROFILE'), 'e2e_results', e2e_results_dir)
                cls.BROWSER_DOWNLOAD_PATH = '/e2e_results/%s/downloads' % e2e_results_dir

            cls.DOWNLOAD_PATH = os.path.join(cls.E2E_RESULTS_PATH, 'downloads')
            cls.SCREENSHOT_PATH = os.path.join(cls.E2E_RESULTS_PATH, 'screenshots')
            cls.ALLURE_RESULTS_PATH = os.path.join(cls.E2E_RESULTS_PATH, 'allure')

            for folder in [cls.E2E_RESULTS_PATH, cls.DOWNLOAD_PATH, cls.SCREENSHOT_PATH, cls.ALLURE_RESULTS_PATH]:
                try:
                    os.makedirs(folder, 0o777)
                    os.chmod(folder, 0o777)
                    print('- bash       | makedirs %s' % folder)
                except OSError:
                    os.chmod(folder, 0o777)
                    print('- bash       | chmod %s' % folder)

            print('')

        return cls.instance
