import hashlib
import inspect
import logging
import os
import re
import time

import allure
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException, NoAlertPresentException, \
                                       NoSuchElementException, MoveTargetOutOfBoundsException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from browser.widgets import create_widget
from constants.common import BrowserType
from settings import Settings
from utils import assert_is_not_none, assert_greater, assert_equals

BROWSER_PREFIX, ATTACHMENT_PREFIX = '- Browser    |', '- Attachment |'
SCREENSHOT_COUNTER = 1

chrome_options = Options()
chrome_options.add_experimental_option("prefs", {'profile.default_content_setting_values.automatic_downloads': 1,
                                                 'download.default_directory': Settings().BROWSER_DOWNLOAD_PATH})

if Settings().BROWSER == BrowserType.CHROME_HEADLESS:
    chrome_options.add_argument("--headless")

chrome_capabilities = chrome_options.to_capabilities()
chrome_capabilities['recreateChromeDriverSessions'] = True
chrome_capabilities['loggingPrefs'] = {'browser': 'SEVERE'}


class Browser(object):
    driver = None

    @classmethod
    def __init__(cls):
        if not cls.driver:
            if Settings().BROWSER == BrowserType.CHROME_REMOTE:
                cls.driver = webdriver.Remote(Settings().COMMAND_EXECUTOR, desired_capabilities=chrome_capabilities)
            else:
                cls.driver = webdriver.Chrome(Settings().COMMAND_EXECUTOR, desired_capabilities=chrome_capabilities)
            cls.driver.implicitly_wait(0.1)
            cls.driver.set_page_load_timeout(150)
            cls.driver.logger = logging.getLogger('browser')

            if Settings().BROWSER == BrowserType.CHROME_HEADLESS:
                cls.driver.set_window_size(1600, 900)
            else:
                cls.driver.maximize_window()

            cls.driver.get(Settings().BASE_URL)

    # BROWSER:
    def get_current_url(self):
        return self.driver.current_url

    def get_url(self, url):
        self.attach_url(url)
        self.driver.get(url)

    def refresh(self):
        try:
            self.driver.refresh()
            self.accept_alert()
        except NoAlertPresentException:
            pass

    def back(self):
        self.driver.back()

    def forward(self):
        self.driver.forward()

    def get_tabs_count(self):
        return len(self.driver.window_handles)

    def switch_to_tab(self, tab_index):
        print(f'{BROWSER_PREFIX} Switch to tab #{tab_index + 1}')
        self.driver.switch_to.window(self.driver.window_handles[tab_index])

    def close_current_tab(self):
        print(f'{BROWSER_PREFIX} Close tab')
        self.driver.close()

    def accept_alert(self):
        self.driver.switch_to.alert.accept()

    @classmethod
    def close(cls):
        if cls.driver:
            cls.driver.quit()
            cls.driver = None

    # KEYBOARD:
    def press_tab(self):
        self.get_element('//html').send_keys(Keys.TAB)

    def press_escape(self):
        self.get_element('//html').send_keys(Keys.ESCAPE)

    # GET AND CLICK:
    def get_all_elements(self, locator):
        return self.driver.find_elements_by_xpath(locator)

    def get_all_visible_elements(self, locator):
        self.wait_for_element_present(locator)
        return self.get_all_elements(locator)

    def get_element(self, locator):
        return self.driver.find_element_by_xpath(locator)

    def get_visible_element(self, locator):
        self.wait_for_element_present(locator)
        return self.get_element(locator)

    def get_widget(self, locator):
        try:
            return create_widget(self, locator)
        except StaleElementReferenceException:
            return create_widget(self, locator)

    def get_elements_count(self, locator):
        return len(self.get_all_elements(locator))

    def move_to_element(self, locator):
        try:
            self.move_to_webelement(self.get_visible_element(locator))
        except StaleElementReferenceException:
            self.move_to_webelement(self.get_visible_element(locator))

    def move_to_webelement(self, element, attempt_number=1):
        try:
            (ActionChains(self.driver)
             .move_to_element(element)
             .perform())

        except MoveTargetOutOfBoundsException as e:
            if attempt_number > 2:
                raise e

            self.make_screenshot('move_out_of_bounds', e)
            self.scroll_down(pixels=500)
            self.move_to_webelement(element, attempt_number=(attempt_number + 1))

    def scroll_up(self, pixels=50):
        self.driver.execute_script(f'window.scrollBy(0, -{pixels});')

    def scroll_down(self, pixels=100):
        self.driver.execute_script(f'window.scrollBy(0, {pixels});')
        self.make_screenshot(f'after_scroll_down_{pixels}_pixels')

    def click(self, locator):
        self._click_attempt(locator)

    def _click_attempt(self, locator, attempt_number=1):
        self.move_to_element(locator)
        self.wait_for_element_visible(locator)
        self.wait_for_element_clickable(locator)

        try:
            self.get_visible_element(locator).click()

        except WebDriverException as e:

            if attempt_number > 5:
                raise e

            if 'Other element would receive the click' in e.msg:
                self.make_screenshot('click_overlapped', e)

            if 'Element is not clickable' in e.msg:
                self.make_screenshot('not_clickable', e)
                self.scroll_down(pixels=100)

            time.sleep(1)
            self._click_attempt(locator, attempt_number=(attempt_number + 1))

    def click_if_visible(self, locator):
        if self.is_element_visible(locator):
            try:
                self.click(locator)
            except NoSuchElementException:
                pass

    def click_all(self, locator):
        try:
            self._click_all(locator)
        except StaleElementReferenceException:
            self._click_all(locator)
        except WebDriverException as e:
            if 'Other element would receive the click' in str(e):
                self._click_all(locator)
            else:
                raise e

    def _click_all(self, locator):
        try:
            [e.click() for e in self.get_all_elements(locator)]
        except StaleElementReferenceException as e:
            self.make_screenshot('click_all', e)
            [e.click() for e in self.get_all_elements(locator)]

    # SET VALUE:
    def click_and_set_value(self, element, value):
        (ActionChains(self.driver)
         .move_to_element(element)
         .click()
         .send_keys(value)
         .perform())

    # WAIT:
    def wait_for_element_present(self, locator, timeout=60):
        self._wait_for(ec.presence_of_element_located, locator, timeout, 'Element not present: {}')

    def wait_for_element_visible(self, locator, timeout=60):
        self._wait_for(ec.visibility_of_element_located, locator, timeout, 'Element not visible: {}')

    def wait_for_all_elements_invisible(self, locator, timeout=30):
        for i in range(len(self.get_all_elements(locator))):
            self.wait_for_element_invisible(f'({locator})[{i + 1}]', timeout)

    def wait_for_element_invisible(self, locator, timeout=60):
        self._wait_for(ec.invisibility_of_element_located, locator, timeout, 'Element still visible: {}')

    def wait_for_element_clickable(self, locator, timeout=30):
        self._wait_for(ec.element_to_be_clickable, locator, timeout, 'Element not clickable: {}')

    def _wait_for(self, expected_condition, locator, timeout, message):
        try:
            WebDriverWait(self.driver, timeout).until(
                expected_condition((By.XPATH, locator)), message=message.format(locator))
        except StaleElementReferenceException:
            self._wait_for(expected_condition, locator, timeout, message)

    # VISIBILITY:
    def is_element_visible(self, locator):
        try:
            elements = self.get_all_elements(locator)
            if len(elements) > 0:
                element = elements[0]
                self.move_to_webelement(element)
                return element.is_displayed()
            else:
                return False
        except StaleElementReferenceException:
            return self.is_element_visible(locator)

    # ATTRIBUTES:
    def get_element_attribute(self, locator, attribute_name):
        try:
            return self.get_element(locator).get_attribute(attribute_name)
        except StaleElementReferenceException:
            return self.get_element(locator).get_attribute(attribute_name)

    # ATTACHMENTS:
    def make_screenshot(self, test_name=None, exception=None):
        make_screenshot(self.driver, test_name, exception)

    def attach_html_source(self):
        allure.attach(self.driver.page_source, 'HTML Source (may brake when opened)', allure.attachment_type.HTML)

    def attach_url(self, url=None):
        url = self.get_current_url() if url is None else url
        print(f'{ATTACHMENT_PREFIX} {url}')
        allure.attach(url, 'URL', allure.attachment_type.URI_LIST)

    # TESTS:
    @staticmethod
    def get_test_name():
        return get_test_name()


def make_screenshot(driver, name=None, exception=None):
    global SCREENSHOT_COUNTER

    if not name:
        name = get_test_name()

    exception_name = {
        exception is None:                  '',
        isinstance(exception, str):         f'_{exception}',
        isinstance(exception, Exception):   f'_{type(exception).__name__}',
    }[True]

    screenshot_filename = f'%03d_{name}{exception_name}.png' % SCREENSHOT_COUNTER

    try:
        allure.attach(driver.get_screenshot_as_png(), name=screenshot_filename, attachment_type=allure.attachment_type.PNG)
        print(f'{ATTACHMENT_PREFIX} {screenshot_filename}')
    except IndexError:
        print(f'{ATTACHMENT_PREFIX} {screenshot_filename} (BYPASSING ALLURE REPORT)')

    screenshot_filename = os.path.join(Settings().SCREENSHOT_PATH, screenshot_filename)
    driver.get_screenshot_as_file(screenshot_filename)

    SCREENSHOT_COUNTER += 1


def get_test_name():
    stack = inspect.stack()
    for frame in stack:
        if frame[3].startswith('test_'):
            return frame[3]
    for frame in stack:
        if frame[3].lower().startswith(('setup', 'teardown')):
            return '{}_{}'.format(os.path.basename(frame[1]), frame[3])
    return None
