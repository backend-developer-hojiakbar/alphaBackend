from rest_framework import serializers
from .models import *


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone', 'name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            phone=validated_data['phone'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone', 'name', 'status')


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = '__all__'


class PriceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceList
        fields = ('user', 'variants', 'lastUpdated')
        read_only_fields = ('user',)


class TariffPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TariffPlan
        fields = '__all__'


class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    plan = TariffPlanSerializer(read_only=True)
    userId = serializers.CharField(source='user.phone', write_only=True)
    planId = serializers.PrimaryKeyRelatedField(
        queryset=TariffPlan.objects.all(), source='plan', write_only=True
    )

    class Meta:
        model = Subscription
        fields = ('id', 'user', 'plan', 'status', 'expiresAt', 'userId', 'planId')

    def create(self, validated_data):
        user_phone = validated_data.pop('user', {}).get('phone')
        try:
            user_instance = User.objects.get(phone=user_phone)
        except User.DoesNotExist:
            raise serializers.ValidationError({"userId": f"Foydalanuvchi '{user_phone}' topilmadi."})

        validated_data['user'] = user_instance
        return super().create(validated_data)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('user', 'createdAt', 'id')


class AuditLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = AuditLogEntry
        fields = ('id', 'user', 'action', 'timestamp')