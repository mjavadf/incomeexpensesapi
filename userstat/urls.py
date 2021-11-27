from django.urls import path
from .views import ExpenseSummaryStats, IncomeSummaryStats

urlpatterns = [
    path('expenses_category_data/',
         ExpenseSummaryStats.as_view(),
         name='expenses_category_data'),
    path('incomes_source_data/',
         IncomeSummaryStats.as_view(),
         name='incomes_source_data'),
]
