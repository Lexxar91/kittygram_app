from django.utils.decorators import method_decorator
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from .core.constants import SAFE_METHODS
from .models import Achievement, Cat

from .serializers import AchievementSerializer, CatSerializer


class CatViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с объектами Cat.
    Представление ModelViewSet для операций CRUD (создание, чтение, обновление, удаление)
    над объектами Cat.
    Параметры:
        queryset -- QuerySet, используемый для извлечения котов с загруженными данными о владельце и достижениях.
        serializer_class -- класс сериализатора для преобразования объектов Cat в JSON и обратно.
        pagination_class -- класс пагинации для разбиения результатов на страницы.
    Методы:
        - perform_create(serializer): Сохраняет объект Cat, устанавливая владельца из запроса.
    """
    queryset = Cat.objects.select_related('owner').prefetch_related('achievements')
    serializer_class = CatSerializer
    pagination_class = PageNumberPagination 

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @method_decorator(cache_page(20))
    def dispatch(self, request, *args, **kwargs):
        return super(CatViewSet, self).dispatch(request, *args, **kwargs)


class AchievementViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с объектами Achievement.
    Этот вьюсет предоставляет стандартные операции CRUD (Create, Retrieve, Update, Delete)
    для объектов Achievement.
    Атрибуты:
        - queryset: QuerySet, используемый для извлечения всех объектов Achievement.
        - serializer_class: Класс сериализатора, используемый для преобразования объектов Achievement
         в формат JSON и обратно.
        - pagination_class: Класс пагинации (в данном случае, отключен).
    """
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    pagination_class = None

    @method_decorator(cache_page(20))
    def dispatch(self, request, *args, **kwargs):
        return super(AchievementViewSet, self).dispatch(request, *args, **kwargs)
