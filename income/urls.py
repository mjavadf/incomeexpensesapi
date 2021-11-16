from django.urls import path
from . import views

urlpatterns = [
    path('', views.IncomesListAPIView.as_view(), name='incomes'),
    path('<int:id>/', views.IncomeDetailAPIView.as_view(), name='income'),
]