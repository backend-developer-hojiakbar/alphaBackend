# core/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'products', PublicDataViewSet, basename='products')
router.register(r'materials', PublicDataViewSet, basename='materials')
router.register(r'templates', PublicDataViewSet, basename='templates')
router.register(r'tariff-plans', PublicDataViewSet, basename='tariff-plans')
router.register(r'orders', OrderViewSet, basename='orders')

admin_router = DefaultRouter()
admin_router.register(r'users', UserManagementViewSet, basename='admin-users')
admin_router.register(r'subscriptions', SubscriptionManagementViewSet, basename='admin-subscriptions')
admin_router.register(r'products', ContentManagementViewSet, basename='admin-products')
admin_router.register(r'materials', ContentManagementViewSet, basename='admin-materials')
admin_router.register(r'templates', ContentManagementViewSet, basename='admin-templates')
admin_router.register(r'promocodes', ContentManagementViewSet, basename='admin-promocodes')
admin_router.register(r'tariffplans', ContentManagementViewSet, basename='admin-tariffplans')
admin_router.register(r'auditlog', AuditLogViewSet, basename='admin-auditlog')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),

    # <<< --- YANGI URL QO'SHILDI --- >>>
    path('my-subscriptions/', MySubscriptionView.as_view(), name='my-subscriptions'),

    path('price-list/', PriceListView.as_view(), name='price-list'),

    path('', include(router.urls)),
    path('admin/', include(admin_router.urls)),
]