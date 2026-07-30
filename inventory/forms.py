from django import forms
from .models import Medicine, Transaction, Manufacturer, Bill

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name','medicine_id','manufacturer','cost_price','mrp','mfg_date','exp_date']  # removed quantity_on_hand
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'medicine_id': forms.TextInput(attrs={'class': 'form-control'}),
            'manufacturer': forms.Select(attrs={'class': 'form-select'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control','step':'0.01'}),
            'mrp': forms.NumberInput(attrs={'class': 'form-control','step':'0.01'}),
            'mfg_date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
            'exp_date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
        }


class TransactionForm(forms.ModelForm):
    TTYPE_CHOICES = (
        ('', '— Select Type —'),   # <- default blank; user must choose
        ('BOUGHT', 'Bought'),
        ('SOLD', 'Sold'),
    )
    ttype = forms.ChoiceField(
        choices=TTYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Transaction
        fields = ['medicine','ttype','partner_name','unit_price','quantity']
        widgets = {
            'medicine': forms.Select(attrs={'class':'form-select'}),
            'partner_name': forms.TextInput(attrs={'class':'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class':'form-control','step':'0.01'}),
            'quantity': forms.NumberInput(attrs={'class':'form-control'}),
        }

    def clean_ttype(self):
        val = self.cleaned_data.get('ttype') or ''
        if val == '':
            raise forms.ValidationError('Please choose Bought or Sold.')
        return val



class ManufacturerForm(forms.ModelForm):
    class Meta:
        model = Manufacturer
        fields = ['name', 'contact_person', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['customer_name', 'customer_phone', 'payment_mode', 'tax_percentage', 'discount_amount', 'notes']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer Name'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number (Optional)'}),
            'payment_mode': forms.Select(attrs={'class': 'form-select'}),
            'tax_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'value': '0.00'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'value': '0.00'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Additional notes...'}),
        }

