# core/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *


# Foydalanuvchi modelini admin panelida sozlash
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('phone', 'name', 'status', 'is_staff', 'is_superuser')
    list_filter = ('status', 'is_staff', 'is_superuser')
    search_fields = ('phone', 'name')
    ordering = ('phone',)

    # UserAdmin'da standart bo'lmagan maydonlarni ko'rsatish uchun
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal info', {'fields': ('name', 'status')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'name', 'password'),
        }),
    )


# Superadmin tomonidan boshqariladigan kontent
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('id', 'name')
    ordering = ('name',)


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('id', 'name')
    ordering = ('name',)


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'productId')
    list_filter = ('productId',)
    search_fields = ('id', 'name')
    ordering = ('name',)


# Narxlar jadvali uchun (bu yerda faqat bitta yozuv bo'lishi kerak)
@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    list_display = ('user', 'lastUpdated')

    # Faqat bitta yozuv qo'shishga ruxsat berish uchun
    def has_add_permission(self, request):
        return not PriceList.objects.exists()


# Moliya va obuna tizimi
@admin.register(TariffPlan)
class TariffPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'period')
    search_fields = ('id', 'name')


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'value', 'uses', 'isActive')
    list_filter = ('isActive', 'type')
    search_fields = ('id',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'expiresAt')
    list_filter = ('status', 'plan')
    search_fields = ('user__name', 'user__phone')
    autocomplete_fields = ['user', 'plan']  # Qidirish uchun qulay interfeys qo'shadi


# Buyurtmalar
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'totalCost', 'createdAt')
    list_filter = ('status', 'createdAt')
    search_fields = ('id', 'user__name', 'user__phone', 'customer__name', 'customer__phone')
    date_hierarchy = 'createdAt'
    ordering = ('-createdAt',)

    # Faqat ko'rish uchun, o'zgartirish tavsiya etilmaydi
    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


# Tizim jurnali
@admin.register(AuditLogEntry)
class AuditLogEntryAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action')
    list_filter = ('user',)
    search_fields = ('user__name', 'action')
    ordering = ('-timestamp',)

    # Admin panelda o'zgartirishni taqiqlash
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False