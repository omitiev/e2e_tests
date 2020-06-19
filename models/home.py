from models import BaseModel
from settings import Settings
from utils import step


class Home(BaseModel):

    elements = {

        # Top menu
        'navbar':       '//*[@class="navbar-brand home"]',
        'login':        '//*[@id="login"]',
        'register':     '//*[@id="register"]',
        'logged_as':    '//a[normalize-space(.)="Logged in as {} {}"]',
        'logout':       '//*[@id="logout"]',
        'cart':         '//*[@id="numItemsInCart"]',

        # Login
        'login_username': '//*[@id="username-modal"]',
        'login_password': '//*[@id="password-modal"]',
        'confirm_login':  '//button[normalize-space(.)="Log in"]',

        # Sign Up
        'register_username':    '//*[@id="register-username-modal"]',
        'register_first_name':  '//*[@id="register-first-modal"]',
        'register_last_name':   '//*[@id="register-last-modal"]',
        'register_email':       '//*[@id="register-email-modal"]',
        'register_password':    '//*[@id="register-password-modal"]',
        'confirm_registration': '//button[normalize-space(.)="Register"]',
        'registration_message': '//*[@id="registration-message" and normalize-space(.)="{}"]',
    }

    def open(self):
        pass

    # NAVIGATION
    def go_to_base_url(self):
        if self.get_current_url().rstrip('/') != Settings().BASE_URL:
            (self.get_uri('')
                 .wait_for_navbar())
        return self

    # LOGIN

    @step('Register {1}')
    def register(self, user_name, first_name, last_name, email, password):
        return (self.click_register()
                    .set_register_username(user_name)
                    .set_register_first_name(first_name)
                    .set_register_last_name(last_name)
                    .set_register_email(email)
                    .set_register_password(password)
                    .click_confirm_registration()
                    .sleep(3))

    @step('Sign In')
    def sign_in(self, user_name, password):
        return (self.click_login()
                    .set_login_username(user_name)
                    .set_login_password(password)
                    .click_confirm_login()
                    .sleep(3))

    @step('Sign Out')
    def sign_out(self):
        return self.click_logout()
