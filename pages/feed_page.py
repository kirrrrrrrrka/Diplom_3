import time
import allure

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from config import DEFAULT_TIMEOUT
from pages.base_page import BasePage


class FeedLocators:
    TITLE = (By.XPATH, "//*[normalize-space()='Лента заказов' or normalize-space()='Лента Заказов']")

    ALL_TIME = (
        By.XPATH,
        "//*[contains(normalize-space(),'Выполнено за все время')]/following::*[1]",
    )
    TODAY = (
        By.XPATH,
        "//*[contains(normalize-space(),'Выполнено за сегодня')]/following::*[1]",
    )

    IN_WORK_SECTION = (
        By.XPATH,
        "//*[normalize-space()='В работе:']/ancestor::section[1]",
    )
    DONE_SECTION = (
        By.XPATH,
        "//*[normalize-space()='Готовы:']/ancestor::section[1]",
    )

    ALL_DONE_MESSAGE = (By.XPATH, "//*[contains(normalize-space(),'Все текущие заказы готовы')]")

    NAV_CONSTRUCTOR = (By.XPATH, "//p[normalize-space()='Конструктор']/ancestor::a")


class FeedPage(BasePage):
    def open_feed(self) -> None:
        self.open(self.base_url + "/feed")
        self.wait_visible(FeedLocators.TITLE, timeout=10)

    def click_constructor_nav(self) -> None:
        self.click(FeedLocators.NAV_CONSTRUCTOR)

    def _parse_int(self, text: str) -> int:
        t = "".join(ch for ch in text if ch.isdigit())
        return int(t) if t else 0

    def get_all_time_total(self) -> int:
        el = self.wait_visible(FeedLocators.ALL_TIME, timeout=10)
        return self._parse_int(el.text)

    def get_today_total(self) -> int:
        el = self.wait_visible(FeedLocators.TODAY, timeout=10)
        return self._parse_int(el.text)

    def wait_all_time_increase(self, old_value: int, timeout: int = 90) -> int:
        def _cond(_):
            v = self.get_all_time_total()
            return v if v > old_value else False

        return WebDriverWait(self.driver, timeout).until(_cond)

    def wait_today_increase(self, old_value: int, timeout: int = 90) -> int:
        """
        Ждём увеличения "Выполнено за сегодня".
        Иногда (особенно в Firefox) счётчик обновляется только после refresh,
        поэтому периодически обновляем страницу.
        """
        end = time.time() + timeout
        last_value = old_value
        next_refresh_at = time.time() + 10  # refresh раз в 10 секунд

        while time.time() < end:
            # гарантируем, что элемент счётчика видим
            self.wait_visible(FeedLocators.TODAY, timeout=DEFAULT_TIMEOUT)

            current = self.get_today_total()
            last_value = current

            if current > old_value:
                return current

            time.sleep(2)

            # refresh не чаще, чем раз в 10 секунд
            if time.time() >= next_refresh_at:
                self.driver.refresh()
                self.wait_visible(FeedLocators.TITLE, timeout=10)
                next_refresh_at = time.time() + 10

        return last_value

    @allure.step("Wait order #{order_number} appears in 'В работе' (or moved to 'Готовы')")
    def wait_order_in_work(self, order_number: str, timeout: int = 90) -> str:
        """
        Возвращает:
        - "work" если номер найден в 'В работе'
        - "done" если номер уже успел перейти в 'Готовы' / или показано "Все текущие заказы готовы!"
        """
        work_xpath = f"{FeedLocators.IN_WORK_SECTION[1]}//*[contains(normalize-space(), '{order_number}')]"
        done_xpath = f"{FeedLocators.DONE_SECTION[1]}//*[contains(normalize-space(), '{order_number}')]"

        def _cond(_):
            if self.exists((By.XPATH, work_xpath)):
                return "work"
            if self.exists((By.XPATH, done_xpath)):
                return "done"
            if self.exists(FeedLocators.ALL_DONE_MESSAGE):
                return "done"
            return False

        return WebDriverWait(self.driver, timeout).until(_cond)
