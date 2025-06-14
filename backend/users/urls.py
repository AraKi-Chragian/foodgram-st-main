from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, subscribe, SubscriptionView

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")

custom_user_urls = [
    path("subscriptions/", SubscriptionView.as_view(), name="subscriptions"),
    path("<int:id>/subscribe/", subscribe, name="subscribe"),
]

urlpatterns = [
    path("", include(router.urls)),
    path("users/", include(custom_user_urls)),
]

