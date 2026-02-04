from selenium.webdriver.common.by import By


class LoginLocators:
    ENTER_FROM_MAIN = (By.XPATH, "//button[contains(normalize-space(), 'Войти в аккаунт')]")

    EMAIL = (
        By.XPATH,
        "//form//label[normalize-space()='Email']/following::input[1]"
        " | //form//input[@placeholder='Email' or @placeholder='E-mail']"
        " | //form//input[@name='name' and (@type='text' or @type='email')]",
    )

    PASSWORD = (
        By.XPATH,
        "//form//label[normalize-space()='Пароль']/following::input[1]"
        " | //form//input[@type='password' or @placeholder='Пароль']",
    )

    SUBMIT = (By.XPATH, "//button[normalize-space()='Войти']")
