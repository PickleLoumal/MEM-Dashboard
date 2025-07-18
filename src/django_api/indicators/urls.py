from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='indicators_index'),
    path('fred/', views.fred_data, name='fred_data'),
    path('bea/', views.bea_data, name='bea_data'),
    path('monetary-base/', views.monetary_base, name='monetary_base'),
    path('health/', views.health_check, name='health_check'),
]
