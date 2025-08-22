from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from .serializers import *
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .models import *
from .serializers import *
from .permissions import IsOwner


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        phone = request.data.get('phone')
        password = request.data.get('password')
        user = User.objects.filter(phone=phone).first()

        if user is None or not user.check_password(password):
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        if user.status == 'blocked':
            return Response({'error': 'User is blocked'}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        is_staff = user.is_staff  # FOYDALANUVCHINING ADMIN STATUSI

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data,
            'is_staff': is_staff  # <<<--- YANGI QO'SHILGAN MAYDON ---<<<
        })


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


# <<< --- YANGI VIEW QO'SHILDI --- >>>
class MySubscriptionView(generics.ListAPIView):
    """Faqat tizimga kirgan foydalanuvchining o'z obunalarini qaytaradi."""
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Bu so'rov yuborayotgan userning obunalarini filterlab beradi
        return Subscription.objects.filter(user=self.request.user)


class PublicDataViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.basename == 'products': return ProductSerializer
        if self.basename == 'materials': return MaterialSerializer
        if self.basename == 'templates': return TemplateSerializer
        if self.basename == 'tariff-plans': return TariffPlanSerializer

    def get_queryset(self):
        if self.basename == 'products': return Product.objects.all()
        if self.basename == 'materials': return Material.objects.all()
        if self.basename == 'templates': return Template.objects.all()
        if self.basename == 'tariff-plans': return TariffPlan.objects.all()
        return None


class PriceListView(generics.RetrieveUpdateAPIView):
    """
    Har bir foydalanuvchi faqat o'zining narxlar jadvalini ko'ra oladi va o'zgartira oladi.
    """
    serializer_class = PriceListSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self):
        # So'rov yuborayotgan foydalanuvchiga tegishli PriceList'ni topamiz.
        # Agar mavjud bo'lmasa, yangisini yaratamiz.
        obj, created = PriceList.objects.get_or_create(user=self.request.user)
        # IsOwner permissioni uchun obyektni tekshirish imkonini beramiz
        self.check_object_permissions(self.request, obj)
        return obj


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-createdAt')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserManagementViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'phone'


class SubscriptionManagementViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAdminUser]


class ContentManagementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.basename == 'admin-products': return ProductSerializer
        if self.basename == 'admin-materials': return MaterialSerializer
        if self.basename == 'admin-templates': return TemplateSerializer
        if self.basename == 'admin-promocodes': return PromoCodeSerializer
        if self.basename == 'admin-tariffplans': return TariffPlanSerializer

    def get_queryset(self):
        if self.basename == 'admin-products': return Product.objects.all()
        if self.basename == 'admin-materials': return Material.objects.all()
        if self.basename == 'admin-templates': return Template.objects.all()
        if self.basename == 'admin-promocodes': return PromoCode.objects.all()
        if self.basename == 'admin-tariffplans': return TariffPlan.objects.all()
        return None


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLogEntry.objects.all().order_by('-timestamp')
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminUser]