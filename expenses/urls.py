from django.urls import path
from . import views

urlpatterns = [
    path('', views.ExpensesListAPIView.as_view(), name='expenses'),
    path('<int:id>/', views.ExpenseDetailAPIView.as_view(), name='expense'),
]