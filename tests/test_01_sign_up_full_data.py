from faker import Faker

from tests import TestBase
from utils import feature, step

fake = Faker()
FIRST_NAME = fake.first_name()
LAST_NAME = fake.last_name()
USER_NAME = "{}{}".format(FIRST_NAME, LAST_NAME).lower()
EMAIL = fake.email()
PASSWORD = fake.bban()


class TestBaseSignUpFullData(TestBase):

    @feature('Sign Up > 01. Success')
    def test_1_sign_up_success(self):
        self.check_sign_up(True)

    @feature('Sign Up > 02. Failed - same user')
    def test_2_sign_up_failed_same_user(self):
        self.check_sign_up(False)

    def check_sign_up(self, valid_data):
        with step('1. Open Main page'):
            home = self.home

        with step(f'2. Open Registration form'):
            home.click_register()

        with step(f'3. Fill in Registration form and confirm Registration'):
            (home
             .set_register_username(USER_NAME)
             .set_register_first_name(FIRST_NAME)
             .set_register_last_name(LAST_NAME)
             .set_register_email(EMAIL)
             .set_register_password(PASSWORD)
             .click_confirm_registration())

        with step(f'4. Check results [valid data - {valid_data}]'):
            if valid_data:
                (home
                 .assert_element_is_present('registration_message', "Registration and login successful.")
                 .wait_for_element('logged_as', FIRST_NAME, LAST_NAME)
                 .assert_element_is_present('logged_as', FIRST_NAME, LAST_NAME)

                 .click_logout())
            else:
                (home
                 .assert_element_not_present('registration_message', "Registration and login successful.")
                 .assert_element_is_present('registration_message', "There was a problem with your registration: Internal Server Error"))
