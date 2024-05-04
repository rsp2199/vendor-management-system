from django.db import models
from django.db.models import Avg, Count
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Vendor, PurchaseOrder
from .serializers import VendorSerializer, PurchaseOrderSerializer, VendorPerformanceSerializer

class VendorListCreateAPIView(generics.ListCreateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

class VendorRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

class VendorPerformanceAPIView(generics.RetrieveAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorPerformanceSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class PurchaseOrderListCreateAPIView(generics.ListCreateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

class PurchaseOrderRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

class PurchaseOrderAcknowledgeAPIView(generics.UpdateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.acknowledgment_date = timezone.now()
        instance.save()
        # Update vendor's average_response_time
        instance.vendor.update_average_response_time()
        return Response(self.get_serializer(instance).data)
    
class Vendor(models.Model):
    # Vendor fields...

    def update_performance_metrics(self):
        completed_orders = self.purchase_orders.filter(status='completed')
        total_orders = self.purchase_orders.all()

        # Calculate on-time delivery rate
        on_time_deliveries = completed_orders.filter(delivery_date__lte=timezone.now()).count()
        self.on_time_delivery_rate = (on_time_deliveries / completed_orders.count()) * 100 if completed_orders.count() > 0 else 0.0

        # Calculate quality rating average
        self.quality_rating_avg = completed_orders.aggregate(Avg('quality_rating'))['quality_rating__avg'] or 0.0

        # Calculate fulfillment rate
        successful_orders = completed_orders.filter(quality_rating__isnull=False)
        self.fulfillment_rate = (successful_orders.count() / total_orders.count()) * 100 if total_orders.count() > 0 else 0.0

        self.save()

    def update_average_response_time(self):
        completed_orders = self.purchase_orders.filter(status='completed', acknowledgment_date__isnull=False)
        if completed_orders.exists():
            self.average_response_time = completed_orders.aggregate(Avg('acknowledgment_date' - 'issue_date'))['acknowledgment_date__avg'].total_seconds() / 3600
            self.save()
