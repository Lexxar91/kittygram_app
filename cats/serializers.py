import base64
from django.core.files.base import ContentFile
from rest_framework import serializers
import webcolors

import datetime as dt

from .core.constants import THIRTY, MORE_THAN_THIRTY, NOT_NAME_FOR_COLOR
from .models import Achievement, AchievementCat, Cat


class Hex2NameColor(serializers.Field):
    """
    Сериализатор для преобразования цвета из HEX в имя цвета.
    """
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        """
        Преобразует шестнадцатеричный цвет в имя цвета.
        Args:
            data (str): Шестнадцатеричный код цвета.
        Returns:
            str: Имя цвета.
        Raises:
            serializers.ValidationError: Если не удается найти имя для указанного цвета.
        """
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError(NOT_NAME_FOR_COLOR)
        return data


class AchievementSerializer(serializers.ModelSerializer):
    """
    Сериализатор достижений котов.
    """
    achievement_name = serializers.CharField(source='name')

    class Meta:
        model = Achievement
        fields = ('id', 'achievement_name',)


class Base64ImageField(serializers.ImageField):
    """
    Преобразует base64-кодированное изображение в объект ContentFile.
    Args:
        data (str): base64-кодированное изображение в формате "data:image/формат;base64,данные".
    Returns:
        ContentFile: Объект ContentFile, представляющий декодированное изображение.
    """
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class CatSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Cat.
    """
    achievements = AchievementSerializer(required=False, many=True)
    color = Hex2NameColor()
    age = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)
    birth_year = serializers.IntegerField()

    class Meta:
        model = Cat
        fields = (
            'id', 'name', 'color', 'birth_year', 'achievements', 'owner', 'age',
            'image'
        )
        read_only_fields = ('owner',)

    def validate_birth_year(self, value):
        """
        Проверка поля birth_year, что бы коту не могло быть
        больше 30 лет
        """
        current_year = dt.datetime.now().year
        if current_year - int(value) > THIRTY:
            raise serializers.ValidationError(MORE_THAN_THIRTY)
        return value

    def get_age(self, obj):
        return dt.datetime.now().year - int(obj.birth_year)

    def create(self, validated_data):
        """
        Создает нового кота.
        Args:
            validated_data (dict): Проверенные данные для создания кота.
        Returns:
            Cat: Новый созданный кот.
        """
        if 'achievements' not in self.initial_data:
            cat = Cat.objects.create(**validated_data)
            return cat
        else:
            achievements = validated_data.pop('achievements')
            cat = Cat.objects.create(**validated_data)
            for achievement in achievements:
                current_achievement, status = Achievement.objects.get_or_create(
                    **achievement
                )
                AchievementCat.objects.create(
                    achievement=current_achievement, cat=cat
                )
            return cat

    def update(self, instance, validated_data):
        """
        Обновляет существующего кота.
        Args:
            instance (Cat): Экземпляр кота, который нужно обновить.
            validated_data (dict): Проверенные данные для обновления кота.
        Returns:
            Cat: Обновленный экземпляр кота.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.color = validated_data.get('color', instance.color)
        instance.birth_year = validated_data.get(
            'birth_year', instance.birth_year
        )
        instance.image = validated_data.get('image', instance.image)
        if 'achievements' in validated_data:
            achievements_data = validated_data.pop('achievements')
            lst = []
            for achievement in achievements_data:
                current_achievement, status = Achievement.objects.get_or_create(
                    **achievement
                )
                lst.append(current_achievement)
            instance.achievements.set(lst)

        instance.save()
        return instance
