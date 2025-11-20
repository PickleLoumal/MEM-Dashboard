from django.urls import path

from .views import policy_updates

app_name = "policy_updates"

urlpatterns = [
    path("updates/", policy_updates, name="updates"),
]
