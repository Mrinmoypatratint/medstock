from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
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

