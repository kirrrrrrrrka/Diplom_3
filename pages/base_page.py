import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    
    MODAL_OVERLAY = (By.XPATH, "//div[contains(@class,'Modal_modal_overlay')]")
    def __init__(self, driver, base_url: str):
        self.driver = driver
        self.base_url = base_url.rstrip("/")

    def open(self, url: str) -> None:
        self.driver.get(url)
        self.wait_no_visible_overlays(timeout=10)

    def current_url(self) -> str:
        return self.driver.current_url

    def wait_url_contains(self, part: str, timeout: int = 10) -> bool:
        return WebDriverWait(self.driver, timeout).until(EC.url_contains(part))

    def wait_visible(self, locator, timeout: int = 10):
        return WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))

    def wait_present(self, locator, timeout: int = 10):
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))

    def wait_clickable(self, locator, timeout: int = 10):
        return WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator))

    def wait_invisible(self, locator, timeout: int = 10) -> bool:
        return WebDriverWait(self.driver, timeout).until(EC.invisibility_of_element_located(locator))

    def wait_no_visible_overlays(self, timeout: int = 10) -> bool:
        """Ждём, что нет ни одного ВИДИМОГО overlay (важно при наличии нескольких div)."""

        def _no_visible(_driver) -> bool:
            overlays = _driver.find_elements(*self.MODAL_OVERLAY)
            return all(not o.is_displayed() for o in overlays)

        return WebDriverWait(self.driver, timeout).until(_no_visible)

    def exists(self, locator) -> bool:
        return len(self.driver.find_elements(*locator)) > 0

    def scroll_into_view(self, element) -> None:
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

    def click_js(self, element) -> None:
        self.driver.execute_script("arguments[0].click();", element)

    def wait_not_obscured(self, element, timeout: int = 10) -> bool:
        """Ждём, что элемент не перекрыт другим слоем в точке центра элемента.

        Это помогает избегать ElementClickInterceptedException в Firefox, когда
        анимации/оверлеи ещё не успели уйти, но элемент уже видим.
        """

        script = """
        const el = arguments[0];
        const rect = el.getBoundingClientRect();
        const x = rect.left + rect.width / 2;
        const y = rect.top + rect.height / 2;
        const top = document.elementFromPoint(x, y);
        return top === el || (top && el.contains(top));
        """

        return WebDriverWait(self.driver, timeout).until(
            lambda d: bool(d.execute_script(script, element))
        )

    @allure.step("Click element")
    def click(self, locator, timeout: int = 10, wait_overlay: bool = True) -> None:
        # Для кликов по элементам страницы (не по элементам модалки) ждём,
        # что overlay не перекрывает интерфейс.
        if wait_overlay:
            self.wait_no_visible_overlays(timeout=timeout)
        el = self.wait_clickable(locator, timeout)
        self.scroll_into_view(el)
        el.click()

    @allure.step("Type text")
    def type(self, locator, text: str, timeout: int = 10) -> None:
        el = self.wait_visible(locator, timeout)
        self.scroll_into_view(el)
        el.clear()
        el.send_keys(text)
