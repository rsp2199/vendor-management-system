# serializers.py in your app

from rest_framework import serializers
from .models import Vendor,PurchaseOrder,VendorPerformance

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'  # Serialize all fields of Vendor model

class PurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'  # Serialize all fields of Vendor model

class VendorPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorPerformance
        fields = '__all__'  # Serialize all fields of Vendor model
