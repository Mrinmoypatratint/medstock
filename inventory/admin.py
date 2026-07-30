from django.contrib import admin
from .models import Medicine, Manufacturer, Transaction, Bill, BillItem

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone')

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name','medicine_id','manufacturer','mrp','exp_date','quantity_on_hand','owner')
    search_fields = ('name','medicine_id')
    list_filter = ('manufacturer','exp_date')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('ttype','medicine','quantity','unit_price','partner_name','owner','created_at')
    list_filter = ('ttype','created_at')


class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 0
    readonly_fields = ('medicine', 'quantity', 'unit_price', 'total_price')

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('bill_number', 'customer_name', 'customer_phone', 'payment_mode', 'subtotal', 'tax_amount', 'discount_amount', 'total_amount', 'owner', 'created_at')
    search_fields = ('bill_number', 'customer_name', 'customer_phone')
    list_filter = ('payment_mode', 'created_at')
    readonly_fields = ('bill_number', 'subtotal', 'tax_amount', 'total_amount', 'created_at')
    inlines = [BillItemInline]

