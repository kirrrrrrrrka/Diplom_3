import allure
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    JavascriptException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    def __init__(self, driver, base_url: str):
        self.driver = driver
        self.base_url = base_url.rstrip("/")

    def open(self, url: str) -> None:
        self.driver.get(url)

    def current_url(self) -> str:
        return self.driver.current_url

    def wait_url_contains(self, part: str, timeout: int = 10) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(EC.url_contains(part))
            return True
        except TimeoutException:
            return False

    def wait_visible(self, locator, timeout: int = 10):
        return WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))

    def wait_present(self, locator, timeout: int = 10):
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))

    def wait_clickable(self, locator, timeout: int = 10):
        return WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator))

    def wait_invisible(self, locator, timeout: int = 10) -> bool:
        return WebDriverWait(self.driver, timeout).until(EC.invisibility_of_element_located(locator))

    def exists(self, locator) -> bool:
        try:
            self.driver.find_element(*locator)
            return True
        except Exception:
            return False

    def scroll_into_view(self, element) -> None:
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        except JavascriptException:
            pass

    def click_js(self, element) -> None:
        self.driver.execute_script("arguments[0].click();", element)

    @allure.step("Click element")
    def click(self, locator, timeout: int = 10) -> None:
        """
        Safe click:
        1) wait clickable -> normal click
        2) if intercepted/stale -> scroll -> js click
        """
        try:
            el = self.wait_clickable(locator, timeout)
            self.scroll_into_view(el)
            el.click()
            return
        except (ElementClickInterceptedException, StaleElementReferenceException):
            el = self.wait_present(locator, timeout)
            self.scroll_into_view(el)
            self.click_js(el)

    @allure.step("Type text")
    def type(self, locator, text: str, timeout: int = 10) -> None:
        el = self.wait_visible(locator, timeout)
        self.scroll_into_view(el)
        el.clear()
        el.send_keys(text)
