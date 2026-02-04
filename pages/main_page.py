import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from config import DEFAULT_TIMEOUT
from pages.base_page import BasePage
from locators.main_locators import MainLocators
from utils import drag_and_drop_html5


class MainPage(BasePage):

    @staticmethod
    def ingredient_card_locator(name: str):
        """Карточка ингредиента по названию."""
        return (
            By.XPATH,
            f"//a[contains(@class,'BurgerIngredient')][.//*[normalize-space()='{name}']]",
        )

    @staticmethod
    def ingredient_counter_locator(name: str):
        """Счётчик на карточке ингредиента по названию."""
        return (
            By.XPATH,
            f"//a[contains(@class,'BurgerIngredient')][.//*[normalize-space()='{name}']]"
            "//p[contains(@class,'counter') or contains(@class,'Counter')]/.."
            "//*[contains(@class,'counter') or contains(@class,'Counter')]",
        )

    @staticmethod
    def modal_ingredient_name_locator(name: str):
        """
        Название ингредиента в модалке деталей ингредиента.
        Вынесено в Page Object, чтобы в тестах не было By.XPATH.
        """
        return (
            By.XPATH,
            "//section[contains(@class,'Modal') or contains(@class,'modal')]"
            f"//*[self::p or self::h2][normalize-space()='{name}']",
        )


    @allure.step("Проверить, что открыт конструктор")
    def is_constructor_page_opened(self, timeout: int = DEFAULT_TIMEOUT) -> bool:
        """
        Явная проверка для теста: URL + заголовок на странице.
        """
        self.wait_url_contains("/", timeout=timeout)
        self.wait_visible(MainLocators.TITLE, timeout=timeout)
        return True


    @allure.step("Открыть конструктор")
    def open_constructor(self) -> None:
        self.open(self.base_url + "/")
        self.wait_visible(MainLocators.TITLE, timeout=DEFAULT_TIMEOUT)

    @allure.step("Кликнуть в навигации: Конструктор")
    def click_constructor_nav(self) -> None:
        self.click(MainLocators.NAV_CONSTRUCTOR, timeout=DEFAULT_TIMEOUT)

    @allure.step("Кликнуть в навигации: Лента заказов")
    def click_feed_nav(self) -> None:
        self.click(MainLocators.NAV_FEED, timeout=DEFAULT_TIMEOUT)


    @allure.step("Открыть модалку ингредиента: {name}")
    def open_ingredient_details(self, name: str) -> None:

        locator = self.ingredient_card_locator(name)

        card = self.wait_visible(locator, timeout=DEFAULT_TIMEOUT)
        self.scroll_into_view(card)

        self.click(locator, timeout=DEFAULT_TIMEOUT)

        self.wait_visible(MainLocators.INGREDIENT_DETAILS_TITLE, timeout=DEFAULT_TIMEOUT)
        self.wait_ingredient_name_in_modal(name, timeout=DEFAULT_TIMEOUT)

    @allure.step("Подождать, что в модалке отображается ингредиент: {name}")
    def wait_ingredient_name_in_modal(self, name: str, timeout: int = DEFAULT_TIMEOUT) -> None:
        self.wait_visible(self.modal_ingredient_name_locator(name), timeout=timeout)

    @allure.step("Проверить, что в модалке отображается ингредиент: {name}")
    def is_ingredient_name_visible_in_modal(self, name: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
        self.wait_visible(self.modal_ingredient_name_locator(name), timeout=timeout)
        return True

    @allure.step("Закрыть модалку")
    def close_modal(self) -> None:
        """
        Закрывает модалку по крестику или кликом по оверлею.
        """
        if self.exists(MainLocators.MODAL_CLOSE):
            close_btn = self.wait_clickable(MainLocators.MODAL_CLOSE, timeout=DEFAULT_TIMEOUT)
            self.scroll_into_view(close_btn)
            self.wait_not_obscured(close_btn, timeout=DEFAULT_TIMEOUT)
            close_btn.click()
        else:
            overlay = self.wait_clickable(MainLocators.MODAL_OVERLAY, timeout=DEFAULT_TIMEOUT)
            self.scroll_into_view(overlay)
            overlay.click()

        self.wait_invisible(MainLocators.MODAL, timeout=DEFAULT_TIMEOUT)
        self.wait_no_visible_overlays(timeout=DEFAULT_TIMEOUT)

    @allure.step("Получить значение счётчика ингредиента: {name}")
    def get_ingredient_counter(self, name: str) -> int:
        locator = self.ingredient_counter_locator(name)
        if not self.exists(locator):
            return 0

        text = self.driver.find_element(*locator).text.strip()
        return int(text) if text.isdigit() else 0

    @allure.step("Дождаться значения счётчика ингредиента {name}: {expected}")
    def wait_ingredient_counter_equals(self, name: str, expected: int, timeout: int = DEFAULT_TIMEOUT) -> None:
        WebDriverWait(self.driver, timeout).until(lambda d: self.get_ingredient_counter(name) == expected)

    @allure.step("Добавить ингредиент в заказ (drag&drop): {name}")
    def add_ingredient_to_order(self, name: str) -> None:
        source = self.wait_visible(self.ingredient_card_locator(name), timeout=DEFAULT_TIMEOUT)
        target = self.wait_visible(MainLocators.ORDER_DROP_AREA, timeout=DEFAULT_TIMEOUT)
        self.scroll_into_view(source)

        drag_and_drop_html5(self.driver, source, target)

    @staticmethod
    def normalize_order_number_for_feed(order_number: str) -> str:
        """Оставляет только цифры для сопоставления в ленте"""
        return "".join(ch for ch in order_number if ch.isdigit())

    @allure.step("Дождаться реального номера заказа (не 9999)")
    def wait_real_order_number(self, timeout: int = 30) -> str:
        """
        Ждём, пока в модалке появится реальный номер.
        """
        def _get_number(_):
            el = self.driver.find_element(*MainLocators.ORDER_NUMBER)
            txt = "".join(ch for ch in el.text.strip() if ch.isdigit())
            if txt and txt != "9999":
                return txt
            return False

        return WebDriverWait(self.driver, timeout).until(_get_number)

    @allure.step("Создать заказ: булка={bun_name}, соус={sauce_name}")
    def create_order(self, bun_name: str, sauce_name: str) -> str:
        """
        Требует авторизации.
        Создаёт заказ и возвращает номер.
        """
        self.open_constructor()

        self.add_ingredient_to_order(bun_name)
        self.add_ingredient_to_order(sauce_name)

        self.click(MainLocators.ORDER_BUTTON, timeout=DEFAULT_TIMEOUT)

        order_number = self.wait_real_order_number(timeout=40)

        self.wait_visible(MainLocators.ORDER_ACCEPTED_TEXT, timeout=DEFAULT_TIMEOUT)

        self.close_modal()
        return order_number
