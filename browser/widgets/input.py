from selenium.common.exceptions import InvalidElementStateException
from selenium.webdriver.common.keys import Keys

from browser.widgets import BaseWidget


class Input(BaseWidget):

    def set_value(self, value):
        if value != Keys.ENTER:
            self.clear_value()
        self.webelement.send_keys(Keys.CONTROL, 'a')
        self.webelement.send_keys(value)

    def clear_value(self):
        try:
            self.webelement.clear()
        except InvalidElementStateException as e:
            self.browser.make_screenshot('input_clear_value', e)
            self.webelement = self.browser.get_element(self.locator)
            self.webelement.clear()

    @property
    def value(self):
        return self.browser.driver.execute_script("return arguments[0].value", self.webelement)

    @property
    def text(self):
        return self.value


class Textarea(Input):

    def clear_value(self):
        self.click()
        self.webelement.clear()


class Editor(Textarea):

    def set_value(self, value):
        self.webelement.send_keys(Keys.CONTROL, 'a')
        self.webelement.send_keys(value)

    @property
    def text(self):
        return self.webelement.text
