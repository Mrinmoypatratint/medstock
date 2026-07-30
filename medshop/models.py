from django.db import models

class Bill(models.Model):
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Bill #{self.id} - {self.customer_name}"

class BillItem(models.Model):
    bill = models.ForeignKey(Bill, related_name='items', on_delete=models.CASCADE)
    # Assuming your medicine model is named 'Medicine' or 'Record'
    medicine_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    price_per_unit = models.DecimalField(max_digits=8, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.price_per_unit
        super().save(*args, **kwargs)