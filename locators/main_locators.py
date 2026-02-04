from selenium.webdriver.common.by import By


class MainLocators:
    # Заголовок конструктора
    TITLE = (By.XPATH, "//*[contains(normalize-space(),'Соберите бургер')]")

    # Навигация
    NAV_CONSTRUCTOR = (By.XPATH, "//p[normalize-space()='Конструктор']/ancestor::a")
    NAV_FEED = (By.XPATH, "//p[normalize-space()='Лента Заказов' or normalize-space()='Лента заказов']/ancestor::a")

    # Кнопка оформления
    ORDER_BUTTON = (By.XPATH, "//button[normalize-space()='Оформить заказ']")

    # Модалка (универсальные локаторы)
    MODAL = (By.XPATH, "//section[contains(@class,'Modal') or contains(@class,'modal')]")
    MODAL_OVERLAY = (By.XPATH, "//div[contains(@class,'Modal_modal_overlay') or contains(@class,'modal_overlay')]")
    MODAL_CLOSE = (
        By.XPATH,
        "//section[contains(@class,'Modal') or contains(@class,'modal')]"
        "//button[contains(@class,'close') or contains(@class,'Close')]",
    )

    # Контент модалки ингредиента
    INGREDIENT_DETAILS_TITLE = (
        By.XPATH,
        "//section[contains(@class,'Modal') or contains(@class,'modal')]"
        "//*[contains(normalize-space(), 'Детали ингредиента')]",
    )

    # Сообщение о принятом заказе
    ORDER_ACCEPTED_TEXT = (
        By.XPATH,
        "//section[contains(@class,'Modal') or contains(@class,'modal')]"
        "//*[contains(normalize-space(),'Ваш заказ начали готовить')]",
    )

    # Номер заказа (цифры)
    ORDER_NUMBER = (
        By.XPATH,
        "//section[contains(@class,'Modal') or contains(@class,'modal')]"
        "//*[contains(@class,'digits') or contains(@class,'Digits') or self::h2]",
    )

    # Зона дропа (конструктор)
    ORDER_DROP_AREA = (By.XPATH, "//section[contains(@class,'BurgerConstructor')]")
