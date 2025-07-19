from .views import CustomLoginView
from django.urls import path


urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
]
