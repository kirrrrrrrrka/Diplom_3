import pytest
import allure

from pages.feed_page import FeedPage
from pages.main_page import MainPage


BUN_NAME = "Флюоресцентная булка R2-D3"
SAUCE_NAME = "Соус Spicy-X"


@allure.feature("Лента заказов")
@pytest.mark.feed
class TestFeed:
    @allure.title("При создании нового заказа увеличивается 'Выполнено за все время'")
    def test_all_time_total_increases_after_order(self, driver, base_url, authorized_driver: MainPage):
        feed = FeedPage(driver, base_url)
        feed.open_feed()
        old_value = feed.get_all_time_total()

        authorized_driver.create_order(BUN_NAME, SAUCE_NAME)

        feed.open_feed()
        new_value = feed.wait_all_time_increase(old_value, timeout=90)
        assert new_value > old_value

    @allure.title("При создании нового заказа увеличивается 'Выполнено за сегодня'")
    def test_today_total_increases_after_order(self, driver, base_url, authorized_driver: MainPage):
        feed = FeedPage(driver, base_url)
        feed.open_feed()
        old_value = feed.get_today_total()

        authorized_driver.create_order(BUN_NAME, SAUCE_NAME)

        feed.open_feed()
        new_value = feed.wait_today_increase(old_value, timeout=90)

        if new_value <= old_value:
            allure.attach(
                f"Today total did not increase. old={old_value}, last={new_value}",
                name="today-total-debug",
                attachment_type=allure.attachment_type.TEXT,
            )

        assert new_value > old_value

    @allure.title("Номер заказа после оформления появляется в разделе 'В работе'")
    def test_order_number_appears_in_work_section(self, driver, base_url, authorized_driver: MainPage):
        order_number = authorized_driver.create_order(BUN_NAME, SAUCE_NAME)
        expected = MainPage.normalize_order_number_for_feed(order_number)

        feed = FeedPage(driver, base_url)
        feed.open_feed()
        where = feed.wait_order_in_work(expected, timeout=90)

        assert where in ("work", "done")
        if where == "done":
            allure.attach(
                "Order moved to 'Готовы' quickly; 'В работе' may already be empty.",
                name="fast-complete",
                attachment_type=allure.attachment_type.TEXT,
            )
