import time
import allure

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from config import DEFAULT_TIMEOUT
from pages.base_page import BasePage


class FeedLocators:
    TITLE = (By.XPATH, "//*[normalize-space()='Лента заказов' or normalize-space()='Лента Заказов']")

    ALL_TIME = (By.XPATH, "//*[contains(normalize-space(),'Выполнено за все время')]/following::*[1]")
    TODAY = (By.XPATH, "//*[contains(normalize-space(),'Выполнено за сегодня')]/following::*[1]")

    IN_WORK_SECTION = (By.XPATH, "//*[normalize-space()='В работе:']/ancestor::section[1]")
    DONE_SECTION = (By.XPATH, "//*[normalize-space()='Готовы:']/ancestor::section[1]")

    ALL_DONE_MESSAGE = (By.XPATH, "//*[contains(normalize-space(),'Все текущие заказы готовы')]")

    NAV_CONSTRUCTOR = (By.XPATH, "//p[normalize-space()='Конструктор']/ancestor::a")


class FeedPage(BasePage):
    # -------------------------
    # Открытие / проверки страницы
    # -------------------------
    @allure.step("Открыть ленту заказов")
    def open_feed(self) -> None:
        self.open(self.base_url + "/feed")
        self.wait_visible(FeedLocators.TITLE, timeout=DEFAULT_TIMEOUT)

    @allure.step("Проверить, что открыта лента заказов")
    def is_feed_page_opened(self, timeout: int = DEFAULT_TIMEOUT) -> bool:
        ok_url = self.wait_url_contains("/feed", timeout=timeout)
        try:
            self.wait_visible(FeedLocators.TITLE, timeout=timeout)
            ok_title = True
        except Exception:
            ok_title = False
        return bool(ok_url and ok_title)

    @allure.step("Кликнуть в навигации: Конструктор")
    def click_constructor_nav(self) -> None:
        self.click(FeedLocators.NAV_CONSTRUCTOR, timeout=DEFAULT_TIMEOUT)

    # -------------------------
    # Счётчики
    # -------------------------
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
        """
        Иногда (особенно в Firefox) счётчик обновляется только после refresh,
        поэтому периодически обновляем страницу.
        """
        end = time.time() + timeout
        last_value = old_value
        next_refresh_at = time.time() + 10

        while time.time() < end:
            self.wait_visible(FeedLocators.TODAY, timeout=DEFAULT_TIMEOUT)

            current = self.get_today_total()
            last_value = current

            if current > old_value:
                return current

            time.sleep(2)

            if time.time() >= next_refresh_at:
                self.driver.refresh()
                self.wait_visible(FeedLocators.TITLE, timeout=DEFAULT_TIMEOUT)
                next_refresh_at = time.time() + 10

        return last_value

    # -------------------------
    # Заказ в "В работе"
    # -------------------------
    @staticmethod
    def _order_in_section_xpath(section_locator: tuple, order_number: str) -> str:
        section_xpath = section_locator[1]
        return f"{section_xpath}//*[contains(normalize-space(), '{order_number}')]"

    @allure.step("Дождаться, что заказ #{order_number} появится в 'В работе' (или успеет перейти в 'Готовы')")
    def wait_order_in_work(self, order_number: str, timeout: int = 90) -> str:
        """
        Возвращает:
        - 'work' если номер найден в 'В работе'
        - 'done' если номер найден в 'Готовы' или показано 'Все текущие заказы готовы'
        """
        work_xpath = self._order_in_section_xpath(FeedLocators.IN_WORK_SECTION, order_number)
        done_xpath = self._order_in_section_xpath(FeedLocators.DONE_SECTION, order_number)

        def _cond(_):
            if self.exists((By.XPATH, work_xpath)):
                return "work"
            if self.exists((By.XPATH, done_xpath)):
                return "done"
            if self.exists(FeedLocators.ALL_DONE_MESSAGE):
                return "done"
            return False

        return WebDriverWait(self.driver, timeout).until(_cond)
