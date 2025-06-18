from django.db import models
from abc import ABC, abstractmethod
from decimal import Decimal
from datetime import date
from typing import Optional, List
from .models import Customer, DebtInfo



class AccountingManager(models.Model):
    AccountingInfo = LogoExcelAdapter()
    def updateCustomerInfo():
        customerDebtList = self.getCustomerDebtList()
    class Meta:
        ordering = ['employee_id']