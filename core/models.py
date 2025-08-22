# core/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('The Phone number must be set')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    phone = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=[('active', 'Active'), ('blocked', 'Blocked')], default='active')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f"{self.name} ({self.phone})"


class Product(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    icon = models.CharField(max_length=50)
    fields = models.JSONField(default=list)
    pricingDimension = models.CharField(max_length=50, null=True, blank=True)
    pricingAttributes = models.JSONField(default=list)
    defaultState = models.JSONField(default=dict)

    def __str__(self):
        return self.name


class Material(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Template(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    previewColor = models.CharField(max_length=50)
    productId = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='templates')
    defaultState = models.JSONField(default=dict)

    def __str__(self):
        return self.name


class PriceList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='price_list', primary_key=True)
    variants = models.JSONField(default=dict)
    lastUpdated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.name}'s Price List"


class TariffPlan(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    period = models.CharField(max_length=10, choices=[('monthly', 'Monthly'), ('yearly', 'Yearly')])
    features = models.JSONField(default=list)

    def __str__(self):
        return self.name


class PromoCode(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    type = models.CharField(max_length=10, choices=[('percentage', 'Percentage'), ('fixed', 'Fixed')])
    value = models.DecimalField(max_digits=10, decimal_places=2)
    uses = models.PositiveIntegerField(default=0)
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return self.id


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(TariffPlan, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=10,
                              choices=[('active', 'Active'), ('cancelled', 'Cancelled'), ('expired', 'Expired')])
    expiresAt = models.DateTimeField()

    def __str__(self):
        return f"{self.user.name}'s subscription to {self.plan.name if self.plan else 'N/A'}"


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('Qabul qilindi', 'Qabul qilindi'),
        ('Jarayonda', 'Jarayonda'),
        ('Tayyor', 'Tayyor'),
        ('Yetkazildi', 'Yetkazildi'),
        ('Bekor qilindi', 'Bekor qilindi'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    items = models.JSONField()
    createdAt = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='Qabul qilindi')

    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    promoCode = models.CharField(max_length=50, null=True, blank=True)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    additionalServices = models.JSONField(default=list)
    totalCost = models.DecimalField(max_digits=12, decimal_places=2)

    customer = models.JSONField()
    delivery = models.JSONField()
    paymentMethod = models.CharField(max_length=50)

    def __str__(self):
        return f"Order #{self.id} by {self.user.name}"


class AuditLogEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name if self.user else 'System'} - {self.action[:50]}"