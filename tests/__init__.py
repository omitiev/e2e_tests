import inspect
import json
import os
import re

from models.home import Home
from settings import Settings
from utils import step

TEST_CLASS_COUNTER = 1
ALLURE_ENV_SAVED = False


class TestBase:

    home = None

    @classmethod
    def setup_class(cls):
        global TEST_CLASS_COUNTER, ALLURE_ENV_SAVED

        test_class_name = re.sub(r"(\w)([A-Z])", r"\1 \2", cls.__name__).upper().replace('TEST ', '')
        print(f'\n%02d. {test_class_name}' % TEST_CLASS_COUNTER)
        TEST_CLASS_COUNTER += 1

        cls.home = Home(parent_frame_locator=None)

        if not ALLURE_ENV_SAVED:
            _save_allure_environment(cls.home.browser.driver)
            ALLURE_ENV_SAVED = True

    @step('0. Setup > Base Test')
    def setup(self):
        print('')
        (self.home
             .close_extra_tabs()
             .go_to_base_url())

    def teardown(self):
        test_report = [fi.frame.f_locals['reports'][-1] for fi in inspect.stack() if 'reports' in fi.frame.f_locals][0]
        if test_report.failed:
            test_name = test_report.head_line.split('.')[-1]
            exception_name = test_report.longreprtext.split('E   ')[1].split(':')[0].split('.')[-1].strip()

            with step('FAILED'):
                print('')
                self.home.accept_alert_if_present()
                self.home.browser.make_screenshot(test_name, exception_name)
                self.home.browser.attach_url()
                self.home.browser.attach_html_source()
                print(f'FAILED with {exception_name}')
        else:
            print(' PASSED')

    @classmethod
    def teardown_class(cls):
        cls.home.browser.close()


def _save_allure_environment(driver):
    chrome_version = driver.capabilities['browserVersion' if Settings().IS_JENKINS else 'version']
    driver_version = driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]
    window_size = driver.get_window_size()

    environment = {
        'SUT':          Settings().BASE_URL,
        'BROWSER':      f"Chrome {chrome_version} | Driver {driver_version} | {window_size['width']} x {window_size['height']} ",
    }

    with open(os.path.join(Settings().ALLURE_RESULTS_PATH, 'environment.properties'), 'w') as file:
        file.write(json.dumps(environment, separators=('\n', '=')).lstrip('{').rstrip('}').replace('"', ''))
