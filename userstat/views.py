import datetime

from django.shortcuts import render
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from expenses.models import Expense
from income.models import Income


class ExpenseSummaryStats(APIView):
    def get_amount_for_category(self, expenses, category):
        e = expenses.filter(category=category)
        amount = e.aggregate(Sum('amount'))

        return {'amount': str(amount['amount__sum'])}

    def get_category(self, expense):
        return expense.category

    def get(self, request):
        today = datetime.date.today()
        a_year_ago = today - datetime.timedelta(days=365)
        expenses = Expense.objects.filter(
            owner=request.user,
            date__gte=a_year_ago,
            date__lte=today
        )

        categories = list(set(map(self.get_category, expenses)))
        final = {}

        for category in categories:
            final[category] = self.get_amount_for_category(
                expenses, category
            )

        return Response({'category_data': final}, status=status.HTTP_200_OK)


class IncomeSummaryStats(APIView):
    def get_amount_for_source(self, incomes, source):
        i = incomes.filter(source=source)
        amount = i.aggregate(Sum('amount'))

        return {'amount': str(amount['amount__sum'])}

    def get_source(self, income):
        return income.source

    def get(self, request):
        today = datetime.date.today()
        a_year_ago = today - datetime.timedelta(days=365)
        incomes = Income.objects.filter(
            owner=request.user,
            date__gte=a_year_ago,
            date__lte=today
        )

        sources = list(set(map(self.get_source, incomes)))
        final = {}

        for source in sources:
            final[source] = self.get_amount_for_source(
                incomes, source
            )

        return Response({'source_data': final}, status=status.HTTP_200_OK)
