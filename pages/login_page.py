import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from config import DEFAULT_TIMEOUT
from pages.base_page import BasePage
from locators.login_locators import LoginLocators


class LoginPage(BasePage):
    @allure.step("Открыть страницу логина")
    def open_login(self) -> None:

        self.open(self.base_url + "/login")
        self.wait_login_opened(timeout=DEFAULT_TIMEOUT)

    @allure.step("Дождаться открытия страницы логина")
    def wait_login_opened(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        self.wait_url_contains("/login", timeout=timeout)
        self.wait_visible(LoginLocators.EMAIL, timeout=timeout)

    @allure.step("Дождаться ухода со страницы логина")
    def wait_left_login_page(self, timeout: int = 15) -> None:
        WebDriverWait(self.driver, timeout).until(lambda d: "/login" not in self.current_url())

    @allure.step("Логин пользователем")
    def login(self, email: str, password: str) -> None:
        email_el = self.wait_visible(LoginLocators.EMAIL, timeout=DEFAULT_TIMEOUT)
        self.scroll_into_view(email_el)
        email_el.clear()
        email_el.send_keys(email)

        pass_el = self.wait_visible(LoginLocators.PASSWORD, timeout=DEFAULT_TIMEOUT)
        self.scroll_into_view(pass_el)
        pass_el.clear()
        pass_el.send_keys(password)
        pass_el.send_keys(Keys.TAB)

        self.click(LoginLocators.SUBMIT, timeout=DEFAULT_TIMEOUT)

        self.wait_left_login_page(timeout=15)
