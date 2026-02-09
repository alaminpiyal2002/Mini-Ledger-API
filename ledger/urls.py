from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, LedgerEntryViewSet, CustomerEntriesListView, CustomerSummaryView

router = DefaultRouter()
router.register(r"customers", CustomerViewSet, basename="customer")
router.register(r"entries", LedgerEntryViewSet, basename="entry")

urlpatterns = [
    path("", include(router.urls)),
    path("customers/<int:customer_id>/entries/", CustomerEntriesListView.as_view(), name="customer-entries"),
    path("customers/<int:customer_id>/summary/", CustomerSummaryView.as_view(), name="customer-summary"),
]

