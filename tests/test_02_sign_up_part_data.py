from faker import Faker

from tests import TestBase
from utils import feature, step, rnd, issue

fake = Faker()


class TestBaseSignUpPartData(TestBase):

    @issue('https://mav-swt.atlassian.net/browse/WS-45')
    @feature('Sign Up > 01. Empty required field')
    def test_1_sign_up_failed_empty_required_field(self):
        with step('1. Open Main page'):
            home = self.home

        with step(f'2. Open Registration form'):
            home.click_register()

            first_name = fake.first_name()
            last_name = fake.last_name()
            username = "{}{}".format(first_name, last_name).lower()
            email = fake.email()
            password = "12345"

            random_field = rnd([username, email, password])
            username = "" if random_field == username else username
            email = "" if random_field == email else email
            password = "" if random_field == password else password

        with step(f'3. Fill in Registration form, leave one of required fields empty and confirm Registration'):
            (home
             .set_register_username(username)
             .set_register_first_name(first_name)
             .set_register_last_name(last_name)
             .set_register_email(email)
             .set_register_password(password)
             .click_confirm_registration())

        with step(f'4. Check results > Sign Up failed'):
            (home
             .assert_element_not_present('registration_message', "Registration and login successful.")
             .assert_element_is_present('registration_message', "There was a problem with your registration: Internal Server Error"))
