import allure
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from config import DEFAULT_TIMEOUT
from pages.base_page import BasePage
from locators.feed_locators import FeedLocators


class FeedPage(BasePage):

    @allure.step("Открыть ленту заказов")
    def open_feed(self) -> None:
        self.open(self.base_url + "/feed")
        self.wait_visible(FeedLocators.TITLE, timeout=DEFAULT_TIMEOUT)

    @allure.step("Проверить, что открыта лента заказов")
    def is_feed_page_opened(self, timeout: int = DEFAULT_TIMEOUT) -> bool:
        self.wait_url_contains("/feed", timeout=timeout)
        self.wait_visible(FeedLocators.TITLE, timeout=timeout)
        return True

    @allure.step("Кликнуть в навигации: Конструктор")
    def click_constructor_nav(self) -> None:
        self.click(FeedLocators.NAV_CONSTRUCTOR, timeout=DEFAULT_TIMEOUT)


    def _parse_int(self, text: str) -> int:
        t = "".join(ch for ch in text if ch.isdigit())
        return int(t) if t else 0

    @allure.step("Получить 'Выполнено за все время'")
    def get_all_time_total(self) -> int:
        el = self.wait_visible(FeedLocators.ALL_TIME, timeout=DEFAULT_TIMEOUT)
        return self._parse_int(el.text)

    @allure.step("Получить 'Выполнено за сегодня'")
    def get_today_total(self) -> int:
        el = self.wait_visible(FeedLocators.TODAY, timeout=DEFAULT_TIMEOUT)
        return self._parse_int(el.text)

    @allure.step("Дождаться увеличения 'Выполнено за все время'")
    def wait_all_time_increase(self, old_value: int, timeout: int = 90) -> int:
        def _cond(_):
            v = self.get_all_time_total()
            return v if v > old_value else False

        return WebDriverWait(self.driver, timeout).until(_cond)

    @allure.step("Дождаться увеличения 'Выполнено за сегодня'")
    def wait_today_increase(self, old_value: int, timeout: int = 90) -> int:
        
        state = {"next_refresh_at": time.monotonic() + 10}

        def _cond(_):
            current = self.get_today_total()
            if current > old_value:
                return current

            now = time.monotonic()
            if now >= state["next_refresh_at"]:
                self.driver.refresh()
                self.wait_visible(FeedLocators.TITLE, timeout=DEFAULT_TIMEOUT)
                state["next_refresh_at"] = now + 10
            return False

        return WebDriverWait(self.driver, timeout, poll_frequency=2).until(_cond)

    @staticmethod
    def _order_in_list_xpath(list_locator: tuple, order_number: str) -> str:
        
        list_xpath = list_locator[1]
        return f"{list_xpath}//*[contains(normalize-space(), '{order_number}')]"

    def get_order_status(self, order_number: str) -> str | None:
        work_xpath = self._order_in_list_xpath(FeedLocators.IN_WORK_LIST, order_number)
        done_xpath = self._order_in_list_xpath(FeedLocators.DONE_LIST, order_number)

        if self.exists((By.XPATH, work_xpath)):
            return "work"
        if self.exists((By.XPATH, done_xpath)):
            return "done"
        return None

    @allure.step("Дождаться, что заказ #{order_number} появится в разделе 'В работе'")
    def wait_order_in_work(self, order_number: str, timeout: int = 90) -> bool:
        def _cond(_):
            return self.get_order_status(order_number) == "work"

        return bool(WebDriverWait(self.driver, timeout, poll_frequency=0.2).until(_cond))
