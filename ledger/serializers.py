from rest_framework import serializers
from .models import Customer,LedgerEntry

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Customer
        fields=["id","name","email","phone","created_at"]
        read_only_fields=["id","created_at"]

class LedgerEntrySerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(write_only=True)
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = LedgerEntry
        fields = ["id", "customer", "customer_id", "entry_type", "amount", "note", "date", "created_at"]
        read_only_fields = ["id", "created_at", "customer"]

    def validate_customer_id(self, value: int) -> int:
        request = self.context["request"]
        exists = Customer.objects.filter(id=value, user=request.user).exists()
        if not exists:
            raise serializers.ValidationError("Customer not found.")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        customer_id = validated_data.pop("customer_id")
        customer = Customer.objects.get(id=customer_id, user=request.user)

        return LedgerEntry.objects.create(
            user=request.user,
            customer=customer,
            **validated_data,
        )

    def update(self, instance, validated_data):
        validated_data.pop("customer_id", None)
        return super().update(instance, validated_data)
