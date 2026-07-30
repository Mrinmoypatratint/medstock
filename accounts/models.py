from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    ROLE_CHOICES = (
        ('OWNER', 'Shop Owner'),
        ('EMPLOYEE', 'Employee'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='OWNER')
    employer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='employees')
    
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    # Legacy text field (kept for backward compatibility)
    medical_license = models.CharField(max_length=100, blank=True)

    # New: document type + file
    gov_id_type = models.CharField(max_length=100, blank=True)  # e.g. Aadhaar, PAN, Drug License
    gov_id_file = models.FileField(upload_to='gov_docs/', blank=True, null=True)

    def __str__(self):
        return self.full_name or self.user.username

    def get_shop_owner(self):
        if self.role == 'EMPLOYEE' and self.employer:
            return self.employer
        return self.user

