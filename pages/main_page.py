import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from config import DEFAULT_TIMEOUT
from pages.base_page import BasePage
from utils import drag_and_drop_html5


class MainLocators:
    TITLE = (By.XPATH, "//*[contains(normalize-space(),'Соберите бургер')]")

    NAV_CONSTRUCTOR = (By.XPATH, "//p[normalize-space()='Конструктор']/ancestor::a")
    NAV_FEED = (By.XPATH, "//p[normalize-space()='Лента Заказов' or normalize-space()='Лента заказов']/ancestor::a")

    ORDER_BUTTON = (By.XPATH, "//button[normalize-space()='Оформить заказ']")

    # Модалка ингредиента
    MODAL = (By.XPATH, "//section[contains(@class,'Modal') or contains(@class,'modal')]")
    MODAL_OVERLAY = (By.XPATH, "//div[contains(@class,'Modal_modal_overlay') or contains(@class,'modal_overlay')]")
    MODAL_CLOSE = (
        By.XPATH,
        "//section[contains(@class,'Modal') or contains(@class,'modal')]//button"
        "[contains(@class,'close') or contains(@class,'Close')]",
    )

    INGREDIENT_DETAILS_TITLE = (
        By.XPATH,
        "//section[contains(@class,'Modal') or contains(@class,'modal')]//*[contains(normalize-space(), 'Детали ингредиента')]",
    )

    # Секция заказа справа
    ORDER_DROP_AREA = (By.XPATH, "//section[contains(@class,'BurgerConstructor')]")


class MainPage(BasePage):
    def open_constructor(self) -> None:
        self.open(self.base_url + "/")
        self.wait_visible(MainLocators.TITLE, timeout=10)

    def click_constructor_nav(self) -> None:
        self.click(MainLocators.NAV_CONSTRUCTOR)

    def click_feed_nav(self) -> None:
        self.click(MainLocators.NAV_FEED)
        
    @staticmethod
    def ingredient_card_locator(name: str):
        return (
            By.XPATH,
            f"//a[contains(@class,'BurgerIngredient')][.//*[normalize-space()='{name}']]",
        )

    @staticmethod
    def ingredient_counter_locator(name: str):
        return (
            By.XPATH,
            f"//a[contains(@class,'BurgerIngredient')][.//*[normalize-space()='{name}']]"
            "//p[contains(@class,'counter') or contains(@class,'Counter')]/.."
            "//*[contains(@class,'counter') or contains(@class,'Counter')]",
        )

    def open_ingredient_details(self, name: str) -> None:
        locator = self.ingredient_card_locator(name)
        el = self.wait_visible(locator, timeout=10)
        self.scroll_into_view(el)

        self.click(locator, timeout=10)

        self.wait_visible(MainLocators.INGREDIENT_DETAILS_TITLE, timeout=10)

    def close_modal(self) -> None:
        if self.exists(MainLocators.MODAL_CLOSE):
            self.click(MainLocators.MODAL_CLOSE)
        else:
            self.click(MainLocators.MODAL_OVERLAY)

        self.wait_invisible(MainLocators.MODAL, timeout=10)

    def get_ingredient_counter(self, name: str) -> int:
        locator = self.ingredient_counter_locator(name)
        if not self.exists(locator):
            return 0
        text = self.driver.find_element(*locator).text.strip()
        return int(text) if text.isdigit() else 0

    def add_ingredient_to_order(self, name: str) -> None:
        source = self.wait_visible(self.ingredient_card_locator(name), timeout=10)
        target = self.wait_visible(MainLocators.ORDER_DROP_AREA, timeout=10)
        self.scroll_into_view(source)

        drag_and_drop_html5(self.driver, source, target)

    @staticmethod
    def normalize_order_number_for_feed(order_number: str) -> str:
        
        return "".join(ch for ch in order_number if ch.isdigit())

    def wait_real_order_number(self, timeout: int = 30) -> str:
        """
        Ждём, пока в модалке появится “реальный” номер (не 9999).
        """
        number_locator = (
            By.XPATH,
            "//section[contains(@class,'Modal') or contains(@class,'modal')]"
            "//*[contains(@class,'digits') or contains(@class,'Digits') or self::h2]",
        )

        def _get_number(_):
            el = self.driver.find_element(*number_locator)
            txt = "".join(ch for ch in el.text.strip() if ch.isdigit())
            if txt and txt != "9999":
                return txt
            return False

        return WebDriverWait(self.driver, timeout).until(_get_number)

    @allure.step("Create order with bun={bun_name} and sauce={sauce_name}")
    def create_order(self, bun_name: str, sauce_name: str) -> str:
        """
        Требует авторизации! (по твоему описанию)
        """
        self.open_constructor()

        self.add_ingredient_to_order(bun_name)
        self.add_ingredient_to_order(sauce_name)

        self.click(MainLocators.ORDER_BUTTON, timeout=15)

        order_number = self.wait_real_order_number(timeout=40)

        self.wait_visible(
            (
                By.XPATH,
                "//section[contains(@class,'Modal') or contains(@class,'modal')]//*[contains(normalize-space(),'Ваш заказ начали готовить')]",
            ),
            timeout=20,
        )

        self.close_modal()
        return order_number
