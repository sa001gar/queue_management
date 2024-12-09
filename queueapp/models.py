from django.db import models
from django.contrib.auth.models import User

class Line(models.Model):
    name = models.CharField(max_length=255)
    pincode = models.CharField(max_length=6)
    registration_start_time = models.DateTimeField()
    capacity = models.IntegerField()
    current_count = models.IntegerField(default=0)
    details = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Registration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    line = models.ForeignKey(Line, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=10)
    aadhaar_no = models.CharField(max_length=12)
    dob = models.DateField()
    position = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.line.name}"

