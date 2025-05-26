from rest_framework.pagination import PageNumberPagination


class HabitPagination(PageNumberPagination):
    """
    Кастомная пагинация для привычек.
    - По умолчанию выводится 5 привычек на страницу.
    - Параметр `page_size` позволяет переопределить количество элементов.
    - Максимальное количество привычек на странице - 50.
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50
