from selenium.common.exceptions import StaleElementReferenceException


class BaseWidget(object):

    def __init__(self, browser, locator):
        self.browser = browser
        self.locator = locator
        self.webelement = browser.get_visible_element(locator)

    def __getattr__(self, item):
        try:
            return getattr(self.webelement, item)
        except StaleElementReferenceException:
            self.webelement = self.browser.get_visible_element(self.locator)
            return getattr(self.webelement, item)

    @property
    def value(self):
        return self.text.strip()

    def is_enabled(self):
        if self.browser.get_visible_element(self.locator).get_attribute('disabled'):
            return False
        else:
            return self.browser.get_elements_count(f'{self.locator}//ancestor-or-self::*[contains(@class, "disabled")]') == 0

    def open(self):
        if not self.is_opened():
            self.click()

    def close(self):
        if self.is_opened():
            self.click()

    def is_opened(self):
        if self.browser.get_element_attribute(self.locator, 'aria-expanded') == 'true':
            return True

        attr_class = self.browser.get_element_attribute(self.locator, 'class')
        if 'collapsed' in attr_class:
            return False
        return any(s in attr_class for s in ['open', 'active'])

    def click(self):
        self.browser.click(self.locator)
