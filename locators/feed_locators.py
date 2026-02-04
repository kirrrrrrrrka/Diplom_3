from selenium.webdriver.common.by import By


class FeedLocators:
    TITLE = (By.XPATH, "//*[normalize-space()='Лента заказов' or normalize-space()='Лента Заказов']")

    ALL_TIME = (By.XPATH, "//*[contains(normalize-space(),'Выполнено за все время')]/following::*[1]")
    TODAY = (By.XPATH, "//*[contains(normalize-space(),'Выполнено за сегодня')]/following::*[1]")

    IN_WORK_LIST = (By.XPATH, "//*[normalize-space()='В работе:']/following::ul[1]")
    DONE_LIST = (By.XPATH, "//*[normalize-space()='Готовы:']/following::ul[1]")

    ALL_DONE_MESSAGE = (By.XPATH, "//*[contains(normalize-space(),'Все текущие заказы готовы')]")

    NAV_CONSTRUCTOR = (By.XPATH, "//p[normalize-space()='Конструктор']/ancestor::a")
