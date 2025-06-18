from django.db import models

class Customer(models.Model):
    cariHesapNo = models.CharField(max_length=20, unique=True)
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    phoneNumber = models.CharField(max_length=15, blank=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)
    debtInfo = models.OneToOneField('DebtInfo', on_delete=models.CASCADE, related_name='customer', null=True)

    def __str__(self):
        return f"{self.cari_hesap_no} {self.first_name} {self.last_name}"

    class Meta:
        ordering = ['-created_at']

class DebtInfo(models.Model):
    debt_amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    last_payment_date = models.DateField(blank=False)
    
    def __str__(self):
        return f"{self.customer.cari_hesap_no} - {self.debt_amount} -Last payment: {self.last_payment_date } -Due date: {self.due_date}"
    
    class Meta:
        ordering = ['-due_date']

class Message(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    response = models.CharField(max_length=3, choices=Response.choices, default=Response.NO_RESPONSE)    
    DebtInfo = models.ForeignKey(DebtInfo, on_delete=models.CASCADE, related_name='messages', null=True, blank=False)
    def __str__(self):
        return f"Message to {self.customer.cari_hesap_no} at {self.sent_at}"
    
    class Meta:
        ordering = ['-sent_at']

    class Response(models.TextChoices):
        CONFIRM = 'CON', 'Confirmed'
        REJECT = 'REJ', 'Rejected'
        NO_RESPONSE  = 'NR', 'Neutral'


