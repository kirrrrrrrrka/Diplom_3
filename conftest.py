import pytest
import allure

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from config import BASE_URL, TEST_USER_EMAIL, TEST_USER_PASSWORD
from pages.login_page import LoginPage
from pages.main_page import MainPage, MainLocators


def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="all", help="chrome|firefox|all")
    parser.addoption("--headless", action="store_true", default=False)


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(params=["chrome", "firefox"])
def driver(request):
    """
    Драйвер создаётся через Selenium Manager (без webdriver_manager и без GitHub).
    """
    browser = request.param
    headless = request.config.getoption("--headless")
    chosen = request.config.getoption("--browser")

    if chosen != "all" and chosen != browser:
        pytest.skip(f"Skipped by --browser {chosen}")

    if browser == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        drv = webdriver.Chrome(options=options)

    else:  # firefox
        options = FirefoxOptions()
        if headless:
            options.add_argument("-headless")

        drv = webdriver.Firefox(options=options)
        drv.set_window_size(1920, 1080)

    yield drv
    drv.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    При падении теста прикладываем в Allure:
    - скриншот
    - html страницы
    """
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("driver", None)
        if driver:
            try:
                png = driver.get_screenshot_as_png()
                allure.attach(png, name="screenshot", attachment_type=allure.attachment_type.PNG)
            except Exception:
                pass
            try:
                html = driver.page_source
                allure.attach(html, name="page_source", attachment_type=allure.attachment_type.HTML)
            except Exception:
                pass


@pytest.fixture
def authorized_driver(driver, base_url):
    """
    Авторизация в UI.
    Возвращаем MainPage в авторизованном состоянии.
    """
    login = LoginPage(driver, base_url)
    login.open_login()
    login.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)

    main = MainPage(driver, base_url)
    main.open_constructor()

    # Проверка что реально залогинились: есть кнопка "Оформить заказ"
    main.wait_visible(MainLocators.ORDER_BUTTON, timeout=15)
    assert "/login" not in driver.current_url
    return main
    
