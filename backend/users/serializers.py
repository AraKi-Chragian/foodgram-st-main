import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import Recipe
from users.models import Subscription

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            header, img_str = data.split(";base64,")
            ext = header.split("/")[-1]
            decoded_file = base64.b64decode(img_str)
            file_name = f"avatar.{ext}"
            data = ContentFile(decoded_file, name=file_name)
        return super().to_internal_value(data)


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name", "password")

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "avatar",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request", None)
        if not request or request.user.is_anonymous:
            return False
        return obj.subscribers.filter(subscriber=request.user).exists()


class UserDetailSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "avatar",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        req = self.context.get("request")
        if not req or req.user.is_anonymous:
            return False
        return obj.subscribers.filter(subscriber=req.user).exists()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ("avatar",)

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get("avatar", instance.avatar)
        instance.save()
        return instance


class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
    )

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Неверный текущий пароль")
        return value

    def validate_new_password(self, value):
        validate_password(value)
        return value


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscriptionAuthorSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
            "avatar",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request", None)
        if not request or request.user.is_anonymous:
            return False
        return obj.subscribers.filter(subscriber=request.user).exists()

    def get_avatar(self, obj):
        if obj.avatar:
            req = self.context.get("request")
            url = obj.avatar.url
            if req:
                return req.build_absolute_uri(url)
            return url
        return None

    def get_recipes(self, obj):
        req = self.context.get("request")
        limit = None
        if req:
            try:
                limit = self.context.get("recipes_limit")
            except (TypeError, ValueError):
                pass
        qs = Recipe.objects.filter(author=obj).order_by("-id")
        if limit is not None:
            qs = qs[:limit]

        serializer = SubscriptionRecipeSerializer(qs, many=True, context=self.context)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class SubscriptionSerializer(serializers.ModelSerializer):
    subscriber = UserSerializer(read_only=True)
    author = SubscriptionAuthorSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ("id", "subscriber", "author")


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("subscriber", "author")

    def validate(self, data):
        subscriber = data.get("subscriber")
        author = data.get("author")
        if subscriber == author:
            raise serializers.ValidationError("Нельзя подписаться на самого себя.")
        exists = Subscription.objects.filter(subscriber=subscriber, author=author).exists()
        if exists:
            raise serializers.ValidationError("Вы уже подписаны на этого пользователя.")
        return data


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email")
