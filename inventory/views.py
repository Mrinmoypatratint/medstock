import uuid
from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction as db_transaction
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
import json
import os
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from .models import Medicine, Transaction, Manufacturer, Bill, BillItem
from .forms import MedicineForm, TransactionForm, ManufacturerForm, BillForm


@login_required
def dashboard(request):
    q = request.GET.get('q','').strip()
    meds = Medicine.objects.all()
    if q:
        meds = meds.filter(Q(name__icontains=q) | Q(medicine_id__icontains=q))

    today = timezone.localdate()
    expiring_limit = today + timedelta(days=30)
    expired_count = meds.filter(exp_date__lt=today).count()
    expiring_count = meds.filter(exp_date__gte=today, exp_date__lte=expiring_limit).count()
    ok_count = meds.filter(exp_date__gt=expiring_limit).count()

    return render(request, 'inventory/dashboard.html', {
        'meds': meds,
        'q': q,
        'expired_count': expired_count,
        'expiring_count': expiring_count,
        'ok_count': ok_count,
    })

@login_required
def medicines(request):
    q = request.GET.get('q','').strip()
    status = request.GET.get('status', '').strip().lower()
    
    meds = Medicine.objects.all()
    
    if q:
        meds = meds.filter(Q(name__icontains=q) | Q(medicine_id__icontains=q))
    
    # Filter by expiry status
    today = timezone.localdate()
    expiring_limit = today + timedelta(days=30)
    
    if status == 'expired':
        meds = meds.filter(exp_date__lt=today)
    elif status == 'expiring':
        meds = meds.filter(exp_date__gte=today, exp_date__lte=expiring_limit)
    elif status == 'ok':
        meds = meds.filter(exp_date__gt=expiring_limit)
    
    # Count for display
    all_meds = Medicine.objects.all()
    expired_count = all_meds.filter(exp_date__lt=today).count()
    expiring_count = all_meds.filter(exp_date__gte=today, exp_date__lte=expiring_limit).count()
    ok_count = all_meds.filter(exp_date__gt=expiring_limit).count()
    
    return render(request, 'inventory/medicines.html', {
        'meds': meds,
        'q': q,
        'status': status,
        'expired_count': expired_count,
        'expiring_count': expiring_count,
        'ok_count': ok_count,
    })

@login_required
def medicine_detail_partial(request, pk):
    med = get_object_or_404(Medicine, pk=pk)
    return render(request, 'inventory/_medicine_detail.html', {'med': med})


@login_required
def records(request):
    """Add medicines, record Bought/Sold, search transactions. Always returns a response."""
    # Unbound by default; rebind on POST as needed
    mform = MedicineForm()
    tform = TransactionForm()

    # Search query for transactions table
    q = (request.GET.get('q') or '').strip()

    if request.method == 'POST':
        if 'save_medicine' in request.POST:
            mform = MedicineForm(request.POST)
            if mform.is_valid():
                obj = mform.save(commit=False)
                obj.owner = request.user
                if getattr(obj, 'quantity_on_hand', None) is None:  # safety if no model default
                    obj.quantity_on_hand = 0
                obj.save()
                messages.success(request, 'Medicine saved successfully.')
                return redirect('inventory:records')
            else:
                messages.error(request, 'Please fix the medicine form errors.')

        elif 'save_txn' in request.POST:
            tform = TransactionForm(request.POST)
            if tform.is_valid():
                txn = tform.save(commit=False)
                txn.owner = request.user
                med = txn.medicine

                if txn.ttype == 'BOUGHT':
                    med.quantity_on_hand += txn.quantity

                elif txn.ttype == 'SOLD':
                    if txn.quantity > med.quantity_on_hand:
                        messages.error(
                            request,
                            f"Cannot sell {txn.quantity}. Only {med.quantity_on_hand} in stock."
                        )
                    else:
                        med.quantity_on_hand -= txn.quantity

                # Only save if no oversell error
                if not messages.get_messages(request):
                    med.save()
                    txn.save()
                    messages.success(request, 'Transaction saved successfully.')
                    return redirect('inventory:records')
            else:
                messages.error(request, 'Please fix the transaction form errors.')

    # Ensure medicine dropdown shows only this user's items
    tform.fields['medicine'].queryset = Medicine.objects.all()

    # Build transactions list (no limit) + search
    txns = Transaction.objects.all().select_related('medicine').order_by('-created_at')
    if q:
        txns = txns.filter(
            Q(partner_name__icontains=q) |
            Q(medicine__name__icontains=q) |
            Q(created_at__date__icontains=q)
        )

    return render(request, 'inventory/records.html', {
        'mform': mform,
        'tform': tform,
        'txns': txns,
        'q': q,
    })


@login_required
def manufacturers(request):
    if request.method == 'POST':
        form = ManufacturerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Manufacturer saved.')
            return redirect('inventory:manufacturers')
    else:
        form = ManufacturerForm()

    q = request.GET.get('q', '').strip()
    items = Manufacturer.objects.all().order_by('name')
    if q:
        from django.db.models import Q
        items = items.filter(
            Q(name__icontains=q) |
            Q(contact_person__icontains=q) |
            Q(phone__icontains=q) |
            Q(address__icontains=q)
        )

    return render(request, 'inventory/manufacturers.html', {
        'form': form,
        'items': items,
        'q': q,
    })



@login_required
def medicine_edit_partial(request, pk):
    """Return the edit form as a partial to load inside the right pane."""
    med = get_object_or_404(Medicine, pk=pk)
    form = MedicineForm(instance=med)
    html = render_to_string('inventory/_medicine_form.html', {'form': form, 'med': med}, request)
    return HttpResponse(html)

@login_required
@require_http_methods(["POST"])
def medicine_edit(request, pk):
    """Accept POST from the inline form; return updated detail partial or form with errors."""
    med = get_object_or_404(Medicine, pk=pk)
    form = MedicineForm(request.POST, instance=med)
    if form.is_valid():
        form.save()
        messages.success(request, 'Medicine updated.')
        html = render_to_string('inventory/_medicine_detail.html', {'med': med, 'saved': True}, request)
        return HttpResponse(html)
    # Return the form again (with errors)
    html = render_to_string('inventory/_medicine_form.html', {'form': form, 'med': med}, request)
    return HttpResponse(html, status=400)

from django.shortcuts import redirect

@login_required
@require_http_methods(["POST"])
def medicine_delete(request, pk):
    """Delete medicine and redirect or return empty pane."""
    med = get_object_or_404(Medicine, pk=pk)
    med.delete()
    messages.success(request, 'Medicine deleted.')

    # If it's an AJAX request, just refresh the right pane.
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('inventory/_empty_detail.html', {}, request)
        return HttpResponse(html)

    # Otherwise redirect user to the dashboard.
    return redirect('inventory:dashboard')


@login_required
def medlist_partial(request):
    """Return just the list markup for the left list (used after save/delete)."""
    q = request.GET.get('q', '').strip()
    meds = Medicine.objects.all()
    if q:
        meds = meds.filter(Q(name__icontains=q) | Q(medicine_id__icontains=q))
    html = render_to_string('inventory/_med_list.html', {'meds': meds}, request)
    return HttpResponse(html)


@login_required
def generate_bill(request):
    """
    High-performance, atomic bill generation view.
    Handles multi-item cart submission, stock verification, atomic DB writes,
    Transaction logging, and user feedback messages.
    """
    if request.method == 'POST':
        form = BillForm(request.POST)
        medicine_ids = request.POST.getlist('medicine_id[]')
        quantities = request.POST.getlist('quantity[]')
        unit_prices = request.POST.getlist('unit_price[]')

        if not form.is_valid():
            messages.error(request, "Please correct the errors in the billing details form.")
            medicines = Medicine.objects.all().select_related('manufacturer').order_by('name')
            return render(request, 'inventory/generate_bill.html', {'form': form, 'medicines': medicines})

        if not medicine_ids or len(medicine_ids) == 0:
            messages.error(request, "Please add at least one medicine item to generate a bill.")
            medicines = Medicine.objects.all().select_related('manufacturer').order_by('name')
            return render(request, 'inventory/generate_bill.html', {'form': form, 'medicines': medicines})

        parsed_items = []
        errors = []

        for idx in range(len(medicine_ids)):
            med_id_str = medicine_ids[idx].strip() if idx < len(medicine_ids) else ""
            qty_str = quantities[idx].strip() if idx < len(quantities) else ""
            price_str = unit_prices[idx].strip() if idx < len(unit_prices) else ""

            if not med_id_str:
                continue

            try:
                med_id = int(med_id_str)
                qty = int(qty_str)
                price = Decimal(price_str)

                if qty <= 0:
                    errors.append(f"Row #{idx+1}: Quantity must be greater than 0.")
                if price < 0:
                    errors.append(f"Row #{idx+1}: Price cannot be negative.")

                parsed_items.append({
                    'medicine_id': med_id,
                    'quantity': qty,
                    'unit_price': price,
                    'row': idx + 1
                })
            except (ValueError, InvalidOperation):
                errors.append(f"Row #{idx+1}: Invalid quantity or price format.")

        if errors:
            for err in errors:
                messages.error(request, err)
            medicines = Medicine.objects.all().select_related('manufacturer').order_by('name')
            return render(request, 'inventory/generate_bill.html', {'form': form, 'medicines': medicines})

        if not parsed_items:
            messages.error(request, "No valid medicine items selected.")
            medicines = Medicine.objects.all().select_related('manufacturer').order_by('name')
            return render(request, 'inventory/generate_bill.html', {'form': form, 'medicines': medicines})

        try:
            with db_transaction.atomic():
                med_ids_set = {item['medicine_id'] for item in parsed_items}
                medicines_dict = {
                    med.id: med for med in Medicine.objects.select_for_update().filter(id__in=med_ids_set)
                }

                for item in parsed_items:
                    med = medicines_dict.get(item['medicine_id'])
                    if not med:
                        raise ValueError(f"Medicine in row #{item['row']} was not found in your inventory.")
                    if med.quantity_on_hand < item['quantity']:
                        raise ValueError(f"Insufficient stock for '{med.name}'. Requested: {item['quantity']}, Available: {med.quantity_on_hand}.")

                date_str = timezone.now().strftime('%Y%m%d')
                random_suffix = uuid.uuid4().hex[:6].upper()
                bill_number = f"INV-{date_str}-{random_suffix}"

                bill = form.save(commit=False)
                bill.owner = request.user
                bill.billed_by = request.user
                bill.bill_number = bill_number

                subtotal = Decimal('0.00')
                bill_items_to_create = []
                txns_to_create = []

                for item in parsed_items:
                    med = medicines_dict[item['medicine_id']]
                    item_total = item['unit_price'] * item['quantity']
                    subtotal += item_total

                    bill_items_to_create.append(BillItem(
                        bill=bill,
                        medicine=med,
                        quantity=item['quantity'],
                        unit_price=item['unit_price'],
                        total_price=item_total
                    ))

                    med.quantity_on_hand -= item['quantity']

                    txns_to_create.append(Transaction(
                        owner=request.user,
                        medicine=med,
                        ttype='SOLD',
                        partner_name=bill.customer_name or 'Walk-in Customer',
                        unit_price=item['unit_price'],
                        quantity=item['quantity']
                    ))

                tax_pct = bill.tax_percentage or Decimal('0.00')
                disc = bill.discount_amount or Decimal('0.00')

                tax_amt = (subtotal * tax_pct / Decimal('100.00')).quantize(Decimal('0.01'))
                total_amt = max(Decimal('0.00'), subtotal + tax_amt - disc).quantize(Decimal('0.01'))

                bill.subtotal = subtotal
                bill.tax_amount = tax_amt
                bill.total_amount = total_amt
                bill.save()

                BillItem.objects.bulk_create(bill_items_to_create)
                Transaction.objects.bulk_create(txns_to_create)
                Medicine.objects.bulk_update(medicines_dict.values(), ['quantity_on_hand'])

            messages.success(request, f"Bill #{bill.bill_number} generated successfully!")
            return redirect('inventory:bill_detail', pk=bill.pk)

        except ValueError as ve:
            messages.error(request, str(ve))
        except Exception as e:
            messages.error(request, f"An unexpected error occurred while generating the bill: {str(e)}")

        medicines = Medicine.objects.all().select_related('manufacturer').order_by('name')
        return render(request, 'inventory/generate_bill.html', {'form': form, 'medicines': medicines})

    else:
        form = BillForm()
        medicines = Medicine.objects.all().select_related('manufacturer').order_by('name')
        return render(request, 'inventory/generate_bill.html', {
            'form': form,
            'medicines': medicines,
        })


@login_required
def bill_list(request):
    """
    Displays list of all bills with prefetch optimization.
    """
    q = request.GET.get('q', '').strip()
    bills = Bill.objects.all().prefetch_related('items__medicine').order_by('-created_at')

    if q:
        bills = bills.filter(
            Q(bill_number__icontains=q) |
            Q(customer_name__icontains=q) |
            Q(customer_phone__icontains=q)
        )

    return render(request, 'inventory/bill_list.html', {
        'bills': bills,
        'q': q,
    })


@login_required
def bill_detail(request, pk):
    """
    Displays a printable invoice detail view.
    """
    bill = get_object_or_404(
        Bill.objects.prefetch_related('items__medicine__manufacturer'),
        pk=pk,
        
    )
    return render(request, 'inventory/bill_detail.html', {'bill': bill})


@login_required
@require_http_methods(["POST"])
def ai_chat_api(request):
    """
    Receives user messages and returns AI responses based on inventory data.
    Uses google-generativeai if API key is present, otherwise falls back to mocked logic.
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Build context from DB
        today = timezone.localdate()
        meds = Medicine.objects.all()
        total_meds = meds.count()
        total_value = sum(m.quantity_on_hand * m.cost_price for m in meds)
        expiring_count = meds.filter(exp_date__gte=today, exp_date__lte=today + timedelta(days=30)).count()
        expired_count = meds.filter(exp_date__lt=today).count()
        low_stock = meds.filter(quantity_on_hand__lte=10).values_list('name', 'quantity_on_hand')
        all_meds_list = list(meds.values_list('name', 'quantity_on_hand'))
        meds_text = ", ".join([f"{name}: {qty}" for name, qty in all_meds_list])
        
        context_str = f"User's Inventory Context:\n- Total Medicine Types: {total_meds}\n- Total Value: ₹{total_value}\n- Expiring in 30 days: {expiring_count}\n- Already Expired: {expired_count}\n- Low Stock Items (<10): {list(low_stock)}\n- All Medicines & Quantities: {meds_text}\n\nUser Question: {user_message}"
        
        # Try to use Gemini
        api_key = os.environ.get('GEMINI_API_KEY')
        if api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                system_instruction = "You are a helpful, professional Smart Assistant for MedShop Tracker. You help medical shop owners manage their inventory. Keep responses concise, friendly, and formatted nicely in plain text (no markdown formatting needed as it's a simple chat window)."
                response = model.generate_content(f"{system_instruction}\n\n{context_str}")
                return JsonResponse({'response': response.text})
            except Exception as e:
                print(f"Gemini API Error: {e}")
                # Fallback to mock if API call fails
                pass
        
        # Fallback Mock Logic
        lower_msg = user_message.lower()
        matched_meds = [m for m in meds if m.name.lower() in lower_msg]
        
        if matched_meds:
            reply_parts = [f"We currently have {m.quantity_on_hand} units of {m.name} in stock." for m in matched_meds]
            reply = " ".join(reply_parts)
        elif "expir" in lower_msg:
            reply = f"You have {expiring_count} items expiring soon, and {expired_count} already expired. Please check the Dashboard for details."
        elif "stock" in lower_msg or "inventory" in lower_msg:
            reply = f"You have {total_meds} types of medicine in stock. {len(low_stock)} items are running critically low (under 10 units)."
        elif "value" in lower_msg or "worth" in lower_msg:
            reply = f"The total cost value of your current inventory is approximately ₹{total_value:.2f}."
        else:
            reply = f"I am currently in Demo Mode (API key not set). Based on your data, you have {total_meds} items in inventory. Ask me about stock levels or specific medicines!"
            
        return JsonResponse({'response': reply})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
