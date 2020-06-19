from collections import OrderedDict

from selenium.common.exceptions import WebDriverException

from browser.widgets.base_widget import BaseWidget
from browser.widgets.input import *


class TooManyElementsException(WebDriverException):
    pass


def create_widget(browser, locator):
    element = browser.get_visible_element(locator)

    tag = element.tag_name
    attr_content_editable = element.get_attribute('contenteditable')

    try:
        widget = OrderedDict({
            'true' == attr_content_editable:                    Editor,
        })[True]

    except KeyError:
        try:
            widget = eval(tag.capitalize())
        except NameError:
            widget = BaseWidget

    return widget(browser, locator)
