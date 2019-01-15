from django.urls import path, re_path
from .views import AssetsViewRouter, AssetViewRouter


urlpatterns = [
    path('', AssetsViewRouter.as_view(), name="assets"),
    re_path(r'^(?P<name>[\w\-]{4,64})$', AssetViewRouter.as_view(), name="asset")
]