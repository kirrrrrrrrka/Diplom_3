import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from pages.base_page import BasePage


class LoginLocators:
    # Кнопка на главной: "Войти в аккаунт"
    ENTER_FROM_MAIN = (By.XPATH, "//button[contains(normalize-space(), 'Войти в аккаунт')]")

    # Инпут Email
    EMAIL = (
        By.XPATH,
        "//form//label[normalize-space()='Email']/following::input[1]"
        " | //form//input[@placeholder='Email' or @placeholder='E-mail']"
        " | //form//input[@name='name' and (@type='text' or @type='email')]",
    )

    # Инпут Пароль
    PASSWORD = (
        By.XPATH,
        "//form//label[normalize-space()='Пароль']/following::input[1]"
        " | //form//input[@type='password' or @placeholder='Пароль']",
    )

    SUBMIT = (By.XPATH, "//button[normalize-space()='Войти']")


class LoginPage(BasePage):
    def open_login(self) -> None:
        """
        Открываем логин:
        """
        self.open(self.base_url + "/")
        try:
            self.click(LoginLocators.ENTER_FROM_MAIN, timeout=7)
            self.wait_url_contains("/login", timeout=10)
        except Exception:
            self.open(self.base_url + "/login")

        self.wait_visible(LoginLocators.EMAIL, timeout=10)

    @allure.step("Login as user")
    def login(self, email: str, password: str) -> None:
        # Вводим email
        email_el = self.wait_visible(LoginLocators.EMAIL, timeout=10)
        self.scroll_into_view(email_el)
        email_el.clear()
        email_el.send_keys(email)

        # Вводим пароль
        pass_el = self.wait_visible(LoginLocators.PASSWORD, timeout=10)
        self.scroll_into_view(pass_el)
        pass_el.clear()
        pass_el.send_keys(password)
        pass_el.send_keys(Keys.TAB)

        # Кликаем по кнопке 
        self.click(LoginLocators.SUBMIT, timeout=10)

        self.wait_url_contains("/login", timeout=2)  # если вдруг не ушли — ок
        WebDriverWait = __import__("selenium.webdriver.support.ui", fromlist=["WebDriverWait"]).WebDriverWait

        def _left_login(_):
            return "/login" not in self.current_url()

        WebDriverWait(self.driver, 15).until(_left_login)
