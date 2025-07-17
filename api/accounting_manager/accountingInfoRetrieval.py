from django.db import models
from abc import ABC, abstractmethod
from decimal import Decimal
from datetime import date
from typing import Optional, List
from .models import Customer, DebtInfo

#interface for accounting information management
class AccountingInfo(ABC):
    @abstractmethod
    def getCustomerDebtList(self) -> List[DebtInfo]:
        """Retrieve debt information for a specific customer"""
        pass


class LogoExcelAdapter(models.Model, AccountingInfo):
    excel_file_path = models.FileField(upload_to='excel_files/')
    last_sync = models.DateTimeField(auto_now=True)

    def getCustomerDebtList(self) -> List[DebtInfo]:
        """
        Parses Excel file and returns a list of DebtInfo objects
        
        Expected Excel columns:
        - CariHesapNo
        - DebtAmount
        - DueDate
        - LastPaymentDate
        """
        try:
            # Read Excel file
            df = pd.read_excel(self.excel_file_path.path)
            
            debt_info_list = []
            
            # Iterate through rows and create DebtInfo objects
            for _, row in df.iterrows():
                try:
                    customer = Customer.objects.get(cariHesapNo=row['CariHesapNo'])
                    
                    debt_info = DebtInfo(
                        customer=customer,
                        debt_amount=Decimal(str(row['DebtAmount'])),
                        due_date=pd.to_datetime(row['DueDate']).date(),
                        last_payment_date=pd.to_datetime(row['LastPaymentDate']).date()
                    )
                    debt_info_list.append(debt_info)
                    
                except Customer.DoesNotExist:
                    # Log error or handle missing customer
                    continue
                    
            return debt_info_list
            
        except Exception as e:
            # Log the error
            print(f"Error parsing Excel file: {str(e)}")
            return []

    class Meta:
        verbose_name = "Logo Excel Adapter"
        verbose_name_plural = "Logo Excel Adapters"
        
class LogoDBAdapter(models.Model, AccountingInfo):
    # ...existing model fields...

    def get_customer_debt(self, customer_id: int) -> Optional[DebtInfo]:
        if not self.customers.filter(id=customer_id).exists():
            return None
        return self.customers.get(id=customer_id).debt_info

    # Implement other required methods...
class LogoAPIAdapter(models.Model, AccountingInfo):
    # ...existing model fields...

    def get_customer_debt(self, customer_id: int) -> Optional[DebtInfo]:
        if not self.customers.filter(id=customer_id).exists():
            return None
        return self.customers.get(id=customer_id).debt_info

    # Implement other required methods...