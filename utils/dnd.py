from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


def drag_and_drop_html5(driver: WebDriver, source: WebElement, target: WebElement) -> None:
    """
    HTML5 drag&drop через JS.
    ActionChains.drag_and_drop нестабилен в Firefox),
    """
    driver.execute_script(
        """
        const source = arguments[0];
        const target = arguments[1];

        const dataTransfer = new DataTransfer();

        source.dispatchEvent(new DragEvent('dragstart', { bubbles: true, dataTransfer }));
        target.dispatchEvent(new DragEvent('dragenter', { bubbles: true, dataTransfer }));
        target.dispatchEvent(new DragEvent('dragover',  { bubbles: true, dataTransfer }));
        target.dispatchEvent(new DragEvent('drop',      { bubbles: true, dataTransfer }));
        source.dispatchEvent(new DragEvent('dragend',   { bubbles: true, dataTransfer }));
        """,
        source,
        target,
    )
