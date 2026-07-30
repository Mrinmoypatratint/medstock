# inventory/urls.py
from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("medicines/", views.medicines, name="medicines"),
    path("medicine/<int:pk>/partial/", views.medicine_detail_partial, name="medicine_detail_partial"),

    # Inline edit/delete + list refresh
    path("medicine/<int:pk>/edit/partial/", views.medicine_edit_partial, name="medicine_edit_partial"),
    path("medicine/<int:pk>/edit/", views.medicine_edit, name="medicine_edit"),
    path("medicine/<int:pk>/delete/", views.medicine_delete, name="medicine_delete"),
    path("medlist/", views.medlist_partial, name="medlist_partial"),

    # Pages
    path("records/", views.records, name="records"),
    path("manufacturers/", views.manufacturers, name="manufacturers"),

    # Billing
    path("billing/", views.generate_bill, name="generate_bill"),
    path("bills/", views.bill_list, name="bill_list"),
    path("bill/<int:pk>/", views.bill_detail, name="bill_detail"),

    # AI Chat API
    path("api/ai-chat/", views.ai_chat_api, name="ai_chat_api"),
]


