import random
import re
import time

from selenium.common.exceptions import NoAlertPresentException
from six import string_types

from browser import Browser
from settings import Settings
from utils import step, print_field_name, rnd, assert_equals, assert_in, assert_false, assert_true, assert_greater, assert_not_in


class BaseModel(object):
    locator = ''

    common_elements = {

        # Spinners:
        'loading_dots_1':       '//*[not(contains(@style, "display: none;"))]/*[contains(@class, "search-widget-loading-dots")]',   # Home

        # Common elements:
        'last_toaster':         '//*[(contains(@class, "ajax-alerts") and @style="display: block;") or @id="notification"][1]',
    }

    def __init__(self, parent_frame_locator=None, *args):
        if parent_frame_locator is not None:  # FrameModel gets any Model
            self.locator = parent_frame_locator + self.locator
        self.locator = '{}'.format(self.locator).format(*args)

        if not hasattr(self, 'elements'):
            self.elements = {}
        self.elements.update(self.common_elements)

        self.browser = Browser()
        self.open()

    def open(self):
        self.click()

    # BROWSER:
    def get_current_url(self):
        return self.browser.get_current_url()

    def get_uri(self, uri):
        self.get_url(f'{Settings().BASE_URL}{uri}')
        return self

    @step('Navigate {1}')
    def get_url(self, url):
        self.browser.get_url(url)
        return self

    @step('Page refresh')
    def refresh(self):
        self.browser.refresh()
        return self

    @step('Back')
    def back(self):
        self.browser.back()
        return self

    @step('Forward')
    def forward(self):
        self.browser.forward()
        return self

    # ALERTS:
    @step('Accept Alert (if present)')
    def accept_alert_if_present(self):
        try:
            self.browser.accept_alert()
        except NoAlertPresentException:
            pass
        return self

    @step('Accept Alert')
    def accept_alert(self):
        self.browser.accept_alert()
        return self

    # TABS:
    @step('Close extra tabs')
    def close_extra_tabs(self):
        for _ in range(self.browser.get_tabs_count() - 1):
            self.browser.switch_to_tab(0)
            self.browser.close_current_tab()
        self.browser.switch_to_tab(0)
        return self

    @step('Switch to previous tab')
    def switch_to_previous_tab(self):
        tabs = self.browser.get_tabs_count()
        self.browser.close_current_tab()
        self.browser.switch_to_tab(tabs - 2)
        return self

    # KEYBOARD:
    @step('Press [Tab]')
    def press_tab(self):
        self.browser.press_tab()
        return self

    @step('Press [Esc]')
    def press_escape(self):
        self.browser.press_escape()
        return self

    # NON-ELEMENTS:
    def click(self):
        self.wait_for_spinner_disappears()
        self.browser.click(self.locator)
        return self

    @step('Scroll Up')
    def scroll_up(self, pixels=50):
        self.browser.scroll_up(pixels)
        return self

    @step('Scroll Down')
    def scroll_down(self, pixels=50):
        self.browser.scroll_down(pixels)
        return self

    @step('Sleep {1}s')
    def sleep(self, seconds_to_sleep):
        time.sleep(seconds_to_sleep)
        return self

    def __getattr__(self, attr):

        keywords = {
            'get_':                            (self.get_model_or_widget,              'Get {element}'),
            'get_random_':                     (self.get_random_model_or_widget,       'Get random {element}'),
            'get_each_':                       (self.get_all_elements,                 'Get each {element}'),
            'show_':                           (self.show_element,                     'Show {element}'),
            'hide_':                           (self.hide_element,                     'Hide {element}'),
            'assert_count_of_':                (self.assert_elements_count,            'Assert count of {element} is {value}'),
            'count_of_':                       (self.get_elements_count,               'Count {element}'),
            'move_to_':                        (self.move_to_element,                  'Move to {element}'),
            'click_':                          (self.click_element,                    'Click {element}'),
            'click_random_':                   (self.click_random_element,             'Click random {element}'),
            'click_if_present_':               (self.click_element_if_present,         'Click {element} if present'),
            'click_each_':                     (self.click_all_elements,               'Click each {element}'),
            'download_':                       (self.click_element,                    'Download {element}'),

            'set_':                            (self.set_element_value,                "Set value '{value}' for {element}"),
            'filter_':                         (self.filter_element_value,             "Filter {element} by '{value}'"),
            'clear_':                          (self.clear_element_value,              "Clear value for {element}"),
            'upload_':                         (self.set_element_value,                "Upload '{value}' into {element}"),
            'assert_value_of_':                (self.assert_element_value,             "Assert value of {element} equals to '{value}'"),
            'assert_options_of_':              (self.assert_element_options,           "Assert options of {element} equals to {value}"),
            'assert_options_filtered_for_':    (self.assert_element_options_filtered,  "Assert each option of {element} contains {value}"),
            'assert_text_is_in_':              (self.assert_text_is_in_element,        "Assert text of {element} contains '{value}'"),
            'assert_text_not_in_':             (self.assert_text_not_in_element,       "Assert text of {element} not contains '{value}'"),
            'get_element_attribute':           (self.get_element_attribute,            'Get {attribute} of {element}'),

            'wait_for_':                       (self.wait_for_element,                 'Wait for {element}'),
            'wait_disappearance_of_':          (self.wait_for_element_disappearance,   'Wait for {element} disappearance'),
            'assert_is_present_':              (self.assert_element_is_present,        'Assert {element} present'),
            'assert_not_present_':             (self.assert_element_not_present,       'Assert {element} not present'),
            'is_present_':                     (self.is_element_present,               'Check if {element} present (condition)'),

            'assert_is_enabled_':              (self.assert_element_is_enabled,        'Assert {element} enabled'),
            'assert_not_enabled_':             (self.assert_element_not_enabled,       'Assert {element} disabled'),
            'is_enabled_':                     (self.is_element_enabled,               'Check if {element} enabled (condition)'),
            'assert_is_selected_':             (self.assert_element_is_selected,       'Assert {element} selected'),
            'assert_not_selected_':            (self.assert_element_not_selected,      'Assert {element} unselected'),
            'is_selected_':                    (self.is_element_selected,              'Check if {element} selected (condition)'),
            'assert_is_opened_':               (self.assert_element_is_opened,         'Assert {element} opened'),
            'assert_not_opened_':              (self.assert_element_not_opened,        'Assert {element} closed'),
            'is_opened_':                      (self.is_element_opened,                'Check if {element} opened (condition)'),

            'assert_tooltip_of_':              (self.assert_tooltip_on_element,        "Assert tooltip of {element} contains '{value}'"),
        }

        def wrapper(*args):
            key, func, step_ = max([(key, func, step_) for key, (func, step_) in keywords.items() if attr.startswith(key)])
            elem_name = attr[len(key):] if key != 'upload_' else attr

            if any(s in self.browser.get_test_name() for s in ['setup_class']):
                return func(elem_name, *args)
            else:
                if len(args) > 2:
                    AttributeError(f'Too much arguments ({len(args)})')
                if len(args) == 2:
                    elem_value = args[0]
                    elem_arg = args[1]
                elif len(args) == 1:
                    elem_value = args[0] if '{value}' in step_ else None
                    elem_arg = args[0] if '{value}' not in step_ else None
                else:
                    elem_value = None
                    elem_arg = None

                with step(step_.format(element=self._format_element_name(elem_name, elem_arg), value=elem_value)):
                    return func(elem_name, *args)

        if attr.startswith(tuple(keywords.keys())):
            return wrapper
        else:
            raise AttributeError(f"'{self.__class__.__name__}' instance has no attribute '{attr}'")

    # GET AND CLICK:
    def get_random_model_or_widget(self, element_name, *args):
        return self.get_model_or_widget(self._add_random_element(element_name, *args), *args)

    def get_all_elements(self, element_name, *args):
        locator = self._get_locator(element_name, *args)
        return [self.browser.get_widget(f'({locator})[{i}]') for i in range(1, self.get_elements_count(element_name, *args) + 1)]

    def get_model_or_widget(self, element_name, *args):
        element, is_model = self._get_element(element_name)
        if is_model:   # FrameModel get any Model
            return element(self.frame_locator, *args) if issubclass(self.__class__, FrameModel) else element(None, *args)
        else:
            return self._get_widget(element_name, *args)

    def show_element(self, element_name, *args):
        self._get_widget(element_name, *args).open()
        return self

    def hide_element(self, element_name, *args):
        self._get_widget(element_name, *args).close()
        return self

    def assert_elements_count(self, element_name, expected_count, *args):
        assert_equals(expected_count, self.get_elements_count(element_name, *args))

        self.browser.make_screenshot()
        return self

    def get_elements_count(self, element_name, *args):
        return self.browser.get_elements_count(self._get_locator(element_name, *args))

    def move_to_element(self, element_name, *args):
        self.wait_for_element(element_name,  *args)
        self.browser.move_to_element(self._get_locator(element_name, *args))
        return self

    def click_element(self, element_name, *args):
        self.browser.click(self._get_locator(element_name, *args))
        return self

    def click_random_element(self, element_name, *args):
        return self.click_element(self._add_random_element(element_name, *args), *args)

    def click_element_if_present(self, element_name, *args):
        self.browser.click_if_visible(self._get_locator(element_name, *args))
        return self

    def click_all_elements(self, element_name, *args):
        self.browser.click_all(self._get_locator(element_name, *args))
        return self

    def _add_random_element(self, element_name, *args):
        self.wait_for_element(element_name, *args)
        new_element_name = f'random_{element_name}'

        self.elements[new_element_name] = \
            f'({self._get_locator(element_name, *args)})[{random.randint(1, self.get_elements_count(element_name, *args))}]'
        return new_element_name

    # SET VALUE:
    def set_element_value(self, element_name, value, *args):
        self._get_widget(element_name, *args).set_value(value)
        return self

    def click_and_set_element_value(self, element_name, value, *args):
        self.browser.click_and_set_value(self._get_widget(element_name, *args).webelement, value)
        return self

    def filter_element_value(self, element_name, value, *args):
        self._get_widget(element_name, *args).filter_value(value)
        return self

    def clear_element_value(self, element_name, *args):
        self._get_widget(element_name, *args).clear_value()
        return self

    def assert_element_value(self, element_name, expected_value, *args):
        actual_value = self._get_widget(element_name, *args).value
        if isinstance(expected_value, str) and isinstance(actual_value, str):
            assert_equals(self._normalize_spaces(expected_value, case_sensitive=True),
                          self._normalize_spaces(actual_value,   case_sensitive=True))
        else:
            assert_equals(expected_value, actual_value)

        self.browser.make_screenshot()
        return self

    def assert_element_options(self, element_name, expected_options, *args):
        widget = self._get_widget(element_name, *args)
        assert_equals(set(widget.options), set(expected_options))
        return self

    def assert_element_options_filtered(self, element_name, filter_value, *args):
        options = self._get_widget(element_name, *args).options
        assert_greater(len(options), 0, f'No options shown for {self._format_element_name(element_name)}')

        assert_true(all(filter_value.lower() in option.lower() for option in options),
                    f"Some of {self._format_element_name(element_name)} options {options} do not contain '{filter_value}'")
        return self

    def assert_text_is_in_element(self, element_name, text_to_be_present, *args):
        widget = self._get_widget(element_name, *args)
        self.browser.wait_for_element_visible(widget.locator)
        assert_in(self._normalize_spaces(text_to_be_present), self._normalize_spaces(widget.text))

        self.browser.make_screenshot()
        return self

    def assert_text_not_in_element(self, element_name, text_to_be_absent, *args):
        widget = self._get_widget(element_name, *args)
        self.browser.wait_for_element_visible(widget.locator)
        assert_not_in(self._normalize_spaces(text_to_be_absent), self._normalize_spaces(widget.text))

        self.browser.make_screenshot()
        return self

    def get_element_attribute(self, attribute_name, element_name, *args):
        return self.browser.get_element_attribute(self._get_locator(element_name, *args), attribute_name)

    @staticmethod
    def _normalize_spaces(text, case_sensitive=False):
        text = (text.replace('\t', ' ')
                    .replace('\n', ' ')
                    .replace('•', '')
                    .replace('<u>', '')
                    .replace('</u>', '')
                    .replace('&#61;', '=')
                    .replace('&#39;', "'")
                    .replace('\xa0', '')
                    .replace('  ', ' ')
                    .replace('  ', ' ')
                    .replace(' .', '.')
                    .strip())

        return text if case_sensitive else text.lower()

    # PRESENCE:
    def wait_for_element(self, element_name, *args):
        self.browser.wait_for_element_visible(self._get_locator(element_name, *args))
        return self

    def wait_for_element_disappearance(self, element_name, *args):
        self.browser.wait_for_element_invisible(self._get_locator(element_name, *args))
        return self

    def assert_random_field_not_present(self, fields):
        field = rnd(fields)
        with step(f'Assert random field ({print_field_name(field)}) absent'):
            return self.assert_element_not_present(field)

    def assert_element_is_present(self, element_name, *args):
        assert_true(self.is_element_present(element_name, *args), f'Element {self._format_element_name(element_name)} not present')

        self.browser.make_screenshot()
        return self

    def assert_element_not_present(self, element_name, *args):
        assert_false(self.is_element_present(element_name, *args), f'Element {self._format_element_name(element_name)} is present')

        self.browser.make_screenshot()
        return self

    def is_element_present(self, element_name, *args):
        return self.browser.is_element_visible(self._get_locator(element_name, *args))

    # STATES:
    def assert_random_field_is_enabled(self, fields):
        field = rnd(fields)
        with step(f'Assert random field ({print_field_name(field)}) enabled'):
            return self.assert_element_is_enabled(field)

    def assert_random_field_not_enabled(self, fields):
        field = rnd(fields)
        with step(f'Assert random field ({print_field_name(field)}) disabled'):
            return self.assert_element_not_enabled(field)

    def assert_element_is_enabled(self, element_name, *args):
        assert_true(self.is_element_enabled(element_name, *args), f'Element {self._format_element_name(element_name)} disabled')

        self.browser.make_screenshot()
        return self

    def assert_element_not_enabled(self, element_name, *args):
        assert_false(self.is_element_enabled(element_name, *args), f'Element {self._format_element_name(element_name)} enabled')

        self.browser.make_screenshot()
        return self

    def is_element_enabled(self, element_name, *args):
        return self._get_widget(element_name, *args).is_enabled()

    def assert_element_is_selected(self, element_name, *args):
        assert_true(self.is_element_selected(element_name, *args), f'Element {self._format_element_name(element_name)} unselected')

        self.browser.make_screenshot()
        return self

    def assert_element_not_selected(self, element_name, *args):
        assert_false(self.is_element_selected(element_name, *args), f'Element {self._format_element_name(element_name)} selected')

        self.browser.make_screenshot()
        return self

    def is_element_selected(self, element_name, *args):
        return self._get_widget(element_name, *args).is_selected()

    def assert_element_is_opened(self, element_name, *args):
        assert_true(self.is_element_opened(element_name, *args), f'Element {self._format_element_name(element_name)} closed')

        self.browser.make_screenshot()
        return self

    def assert_element_not_opened(self, element_name, *args):
        assert_false(self.is_element_opened(element_name, *args), f'Element {self._format_element_name(element_name)} opened')

        self.browser.make_screenshot()
        return self

    def is_element_opened(self, element_name, *args):
        return self._get_widget(element_name, *args).is_opened()

    # TOOLTIPS:
    def assert_tooltip_on_element(self, element_name, expected_text, *args):
        locator = self._get_locator(element_name, *args)
        self.browser.move_to_element(locator)

        value = None
        for tooltip_attr in ['ngbtooltip', 'title', 'data-content']:
            attr_value = self.browser.get_element_attribute(locator, tooltip_attr)
            if attr_value and len(attr_value) > 0:
                value = attr_value

        if value is None:
            value = self._get_widget('popover').text

        assert_in(self._normalize_spaces(expected_text), self._normalize_spaces(value))
        self.browser.make_screenshot()

        return self

    # SERVICE METHODS:
    def _get_widget(self, element_name, *args):
        return self.browser.get_widget(self._get_locator(element_name, *args))

    def _get_locator(self, element_name, *args):
        self.wait_for_spinner_disappears()
        element, is_model = self._get_element(element_name)
        if is_model:
            if issubclass(self.__class__, FrameModel):  # FrameModel gets any Model.locator
                return self.frame_locator + element.locator.format(*args)
            else:
                return element.locator.format(*args)
        else:
            return element.format(*args)

    def _get_element(self, element_name):
        if element_name not in self.elements.keys():
            raise AttributeError(f"'{self.__class__.__name__}' model has no element '{element_name}'")
        element = self.elements[element_name]

        if isinstance(element, BaseModel) or (type(element) == type and issubclass(element, BaseModel)):
            return element, True
        else:
            return element, False

    @staticmethod
    def _format_element_name(element_name, element_arg=None):
        return f"[{' '.join(word.capitalize() for word in element_name.split('_'))}" \
               f"{f'={element_arg}' if element_arg else ''}]"

    # SPINNERS:
    def wait_for_spinner_disappears(self, timeout=90):
        for spinner_name in ['loading_dots_1']:
            self.browser.wait_for_all_elements_invisible(self.elements[spinner_name], timeout)
        return self

    # SCREENSHOTS
    @step('Screenshot')
    def make_screenshot(self, test_name=None, exception=None):
        self.browser.make_screenshot(test_name, exception)
        return self


class FrameModel(BaseModel):
    frame_locator = ''

    # Append frame locator as a prefix for each element
    def __new__(cls, parent_frame_locator=None, *args):
        inst = super(FrameModel, cls).__new__(cls)
        inst.frame_locator = cls.frame_locator.format(*args)

        if parent_frame_locator is not None:  # FrameMode get FrameModel
            inst.frame_locator = parent_frame_locator + cls.frame_locator.format(*args)

        inst.elements = cls.elements.copy()

        for key in inst.elements:
            value = inst.elements[key]
            if isinstance(value, string_types) and inst.frame_locator not in value:
                inst.elements[key] = inst.frame_locator + value

                value = inst.elements[key]
                match = re.compile('(^.*)(\\[[0-9]+\\]|\\[{}\\]|\\[last\\(\\)\\])$').match(value)
                if match:
                    inst.elements[key] = f'({match.groups()[0]}){match.groups()[1]}'
        return inst
