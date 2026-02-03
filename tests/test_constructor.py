import pytest
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from config import DEFAULT_TIMEOUT
from pages.feed_page import FeedLocators, FeedPage
from pages.main_page import MainLocators, MainPage


BUN_NAME = "Флюоресцентная булка R2-D3"
SAUCE_NAME = "Соус Spicy-X"


@allure.feature("Конструктор")
@pytest.mark.constructor
class TestConstructor:
    @allure.title("Переход по клику на 'Конструктор'")
    def test_click_constructor_opens_constructor_page(self, driver, base_url):
        feed = FeedPage(driver, base_url)
        feed.open_feed()
        feed.click_constructor_nav()

        main = MainPage(driver, base_url)
        main.wait_visible(MainLocators.TITLE)

    @allure.title("Переход по клику на 'Лента заказов'")
    def test_click_feed_opens_feed_page(self, driver, base_url):
        main = MainPage(driver, base_url)
        main.open_constructor()
        main.click_feed_nav()

        feed = FeedPage(driver, base_url)
        feed.wait_visible(FeedLocators.TITLE)

    @allure.title("Клик по ингредиенту открывает модалку с деталями")
    def test_click_ingredient_opens_details_modal(self, driver, base_url):
        main = MainPage(driver, base_url)
        main.open_constructor()

        main.open_ingredient_details(BUN_NAME)

        main.wait_visible(
            (
                By.XPATH,
                f"//section[contains(@class,'Modal') or contains(@class,'modal')]//*[normalize-space()='{BUN_NAME}']",
            )
        )

    @allure.title("Модалка ингредиента закрывается по клику на крестик")
    def test_ingredient_modal_closes_by_cross(self, driver, base_url):
        main = MainPage(driver, base_url)
        main.open_constructor()

        main.open_ingredient_details(BUN_NAME)
        main.close_modal()

        assert main.wait_invisible(MainLocators.INGREDIENT_DETAILS_TITLE)

    @allure.title("При добавлении ингредиента в заказ увеличивается счетчик")
    def test_add_ingredient_increases_counter(self, driver, base_url):
        main = MainPage(driver, base_url)
        main.open_constructor()

        bun_before = main.get_ingredient_counter(BUN_NAME)
        sauce_before = main.get_ingredient_counter(SAUCE_NAME)

        main.add_ingredient_to_order(BUN_NAME)
        WebDriverWait(driver, DEFAULT_TIMEOUT).until(
            lambda d: main.get_ingredient_counter(BUN_NAME) == bun_before + 2
        )

        main.add_ingredient_to_order(SAUCE_NAME)
        WebDriverWait(driver, DEFAULT_TIMEOUT).until(
            lambda d: main.get_ingredient_counter(SAUCE_NAME) == sauce_before + 1
        )
