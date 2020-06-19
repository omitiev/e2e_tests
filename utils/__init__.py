import os
import random
import re
from datetime import datetime

import allure
import jsonpath_rw_ext as jp
import pytest
from faker import Faker
from faker.providers import phone_number, internet, credit_card
from nose import tools as nose_tools

# DECORATORS

try:
    step = allure.step
    feature = allure.feature
    issue = allure.issue
    skip = pytest.mark.skip
    skipif = pytest.mark.skipif
except (AttributeError, ImportError):
    def options():
        def decorator(target):
            return target
        return decorator
    step = options


# ASSERTIONS

assert_is_none = nose_tools.assert_is_none
assert_is_not_none = nose_tools.assert_is_not_none

assert_true = nose_tools.assert_true
assert_false = nose_tools.assert_false

assert_equals = nose_tools.assert_equals
assert_set_equal = nose_tools.assert_set_equal

assert_less = nose_tools.assert_less
assert_less_equal = nose_tools.assert_less_equal
assert_greater = nose_tools.assert_greater
assert_greater_equal = nose_tools.assert_greater_equal

assert_in = nose_tools.assert_in
assert_not_in = nose_tools.assert_not_in


# FAKER

fake = Faker()
fake.add_provider(phone_number)
fake.add_provider(internet)
fake.add_provider(credit_card)


# FILES

def get_filepath(file_):
    return os.path.dirname(os.path.abspath(file_))


# JSON PARSER

def jpath_match(path, json, as_list=False):
    return jp.match(f'$.{path}', json) if as_list else jp.match(f'$.{path}', json)[0]


# DATES

def get_current_date_time(date_format='DATE %Y, %B %d, %A | TIME %H:%M:%S'):
    return date_to_string(datetime.utcnow(), date_format)


def date_to_datetime(date_):
    return datetime(date_.year, date_.month, date_.day)


def date_to_string(date_, date_format):
    return date_.strftime(date_format)


def date_range_to_string(start_date, end_date, date_format='%Y-%m-%d'):
    return f'{start_date.strftime(date_format)} - {end_date.strftime(date_format)}'


def string_to_date(date_string, date_format):
    return datetime.strptime(date_string, date_format)


# TEXT

def normalize_spaces(text):
    return re.sub(' +', ' ', text).strip()


def print_field_name(field_name):
    return field_name.replace('_', ' ').title()


# RANDOM

def rnd(list_):
    return random.choice(list_)
