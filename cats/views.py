from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.utils.decorators import method_decorator

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.views.decorators.cache import cache_page
from rest_framework.response import Response

from .models import Achievement, Cat

from .serializers import AchievementSerializer, CatSerializer


class CatViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для управления данными о котах.
    Основной вьюсет для выполнения операций CRUD (создание, чтение, обновление, удаление)
    над объектами Cat.
    Attributes:
       queryset: QuerySet для извлечения котов с загруженными данными о владельце и достижениях.
       serializer_class: Класс сериализатора для преобразования объектов Cat в JSON и обратно.
       pagination_class: Класс пагинации для разбиения результатов на страницы.
    Methods:
       - perform_create(serializer): Сохраняет объект Cat, устанавливая владельца из запроса.
       - top_colors_cats(request): Возвращает самый популярный цвет среди всех котов.
       - dispatch(request, *args, **kwargs): Применяет кеширование и передает запрос в базовый метод dispatch.
    """
    queryset = Cat.objects.select_related('owner').prefetch_related('achievements')
    serializer_class = CatSerializer
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, url_path='top-colors-cats')
    def top_colors_cats(self, request):
        try:
            top_color = Cat.objects.values('color') \
                .annotate(top=Count('color')) \
                .order_by('-top') \
                .first()['color']
            return Response({"Самый популярный цвет": top_color})
        except ObjectDoesNotExist:
            return Response({"Самый популярный цвет": "Нет данных о цветах котов"})

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
