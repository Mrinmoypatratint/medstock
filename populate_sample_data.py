"""
Script to populate the database with sample data for demo purposes.
Run with: python manage.py shell < populate_sample_data.py
Or: python populate_sample_data.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medshop.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from accounts.models import Profile
from inventory.models import Medicine, Transaction, Manufacturer
from datetime import date, timedelta
from decimal import Decimal
import random

print("=" * 50)
print("POPULATING SAMPLE DATA FOR MEDSHOP TRACKER")
print("=" * 50)

# Get or create demo user
user, created = User.objects.get_or_create(
    username='room214boys@gmail.com',
    defaults={'email': 'room214boys@gmail.com'}
)
if created:
    user.set_password('Demo@1234')
    user.save()
    print('\n✓ Created demo user:')
    print('  Email: demo@medshop.com')
    print('  Password: Demo@1234')
else:
    print('\n✓ Demo user already exists')

# Update profile
profile = user.profile
profile.full_name = 'Dr. Rajesh Kumar'
profile.phone = '9876543210'
profile.address = '123 Medical Plaza, Sector 5\nNew Delhi, India 110001'
profile.medical_license = 'DL-MED-2024-12345'
profile.gov_id_type = 'Aadhaar Card'
profile.save()
print('✓ Updated profile for Dr. Rajesh Kumar')

# Create Manufacturers
print('\n--- Creating Manufacturers ---')
manufacturers_data = [
    {'name': 'Sun Pharmaceuticals', 'contact_person': 'Amit Sharma', 'phone': '9876543211', 'address': 'Mumbai, Maharashtra'},
    {'name': 'Cipla Ltd', 'contact_person': 'Priya Patel', 'phone': '9876543212', 'address': 'Bangalore, Karnataka'},
    {'name': 'Dr. Reddys Labs', 'contact_person': 'Vikram Singh', 'phone': '9876543213', 'address': 'Hyderabad, Telangana'},
    {'name': 'Lupin Limited', 'contact_person': 'Neha Gupta', 'phone': '9876543214', 'address': 'Pune, Maharashtra'},
    {'name': 'Mankind Pharma', 'contact_person': 'Rohit Verma', 'phone': '9876543215', 'address': 'Gurgaon, Haryana'},
    {'name': 'Zydus Cadila', 'contact_person': 'Sanjay Mehta', 'phone': '9876543216', 'address': 'Ahmedabad, Gujarat'},
    {'name': 'Torrent Pharma', 'contact_person': 'Kavita Joshi', 'phone': '9876543217', 'address': 'Ahmedabad, Gujarat'},
]

for m in manufacturers_data:
    obj, created = Manufacturer.objects.get_or_create(name=m['name'], defaults=m)
    if created:
        print(f'  ✓ Created: {m["name"]}')
    else:
        print(f'  - Exists: {m["name"]}')

# Create Medicines
print('\n--- Creating Medicines ---')
today = date.today()

# Get manufacturer objects
mfg_sun = Manufacturer.objects.get(name='Sun Pharmaceuticals')
mfg_cipla = Manufacturer.objects.get(name='Cipla Ltd')
mfg_reddy = Manufacturer.objects.get(name='Dr. Reddys Labs')
mfg_lupin = Manufacturer.objects.get(name='Lupin Limited')
mfg_mankind = Manufacturer.objects.get(name='Mankind Pharma')
mfg_zydus = Manufacturer.objects.get(name='Zydus Cadila')
mfg_torrent = Manufacturer.objects.get(name='Torrent Pharma')

medicines_data = [
    # Name, Medicine ID, Manufacturer obj, Cost Price, MRP, Mfg Date offset (days ago), Exp Date offset (days from now), Qty
    ('Paracetamol 500mg', 'MED001', mfg_sun, 25.00, 35.00, 180, 365, 500),
    ('Amoxicillin 250mg', 'MED002', mfg_cipla, 45.00, 65.00, 120, 270, 300),
    ('Omeprazole 20mg', 'MED003', mfg_reddy, 35.00, 50.00, 90, 540, 200),
    ('Metformin 500mg', 'MED004', mfg_lupin, 20.00, 30.00, 200, 400, 450),
    ('Atorvastatin 10mg', 'MED005', mfg_mankind, 55.00, 80.00, 150, 480, 250),
    ('Azithromycin 500mg', 'MED006', mfg_zydus, 85.00, 120.00, 100, 300, 180),
    ('Cetirizine 10mg', 'MED007', mfg_torrent, 15.00, 22.00, 220, 600, 600),
    ('Pantoprazole 40mg', 'MED008', mfg_sun, 40.00, 55.00, 130, 350, 320),
    ('Ibuprofen 400mg', 'MED009', mfg_cipla, 18.00, 28.00, 160, 420, 400),
    ('Vitamin D3 60K', 'MED010', mfg_mankind, 30.00, 45.00, 90, 730, 150),
    # Some expiring soon
    ('Cough Syrup 100ml', 'MED011', mfg_lupin, 50.00, 75.00, 300, 25, 80),
    ('Antacid Gel 170ml', 'MED012', mfg_zydus, 65.00, 95.00, 280, 20, 45),
    ('Cold Tablets', 'MED013', mfg_sun, 22.00, 32.00, 250, 15, 120),
    # Some expired
    ('Antiseptic Cream', 'MED014', mfg_cipla, 40.00, 60.00, 400, -10, 30),
    ('Eye Drops 10ml', 'MED015', mfg_reddy, 75.00, 110.00, 380, -5, 25),
    # More variety
    ('Calcium Tablets', 'MED016', mfg_torrent, 90.00, 130.00, 100, 500, 200),
    ('B-Complex Syrup', 'MED017', mfg_mankind, 55.00, 80.00, 120, 450, 150),
    ('Diclofenac Gel', 'MED018', mfg_zydus, 45.00, 65.00, 140, 380, 180),
    ('Ranitidine 150mg', 'MED019', mfg_lupin, 25.00, 38.00, 180, 320, 280),
    ('Multivitamin Caps', 'MED020', mfg_sun, 120.00, 175.00, 80, 600, 350),
]

for name, med_id, manufacturer, cost, mrp, mfg_offset, exp_offset, qty in medicines_data:
    med, created = Medicine.objects.get_or_create(
        medicine_id=med_id,
        owner=user,
        defaults={
            'name': name,
            'manufacturer': manufacturer,
            'cost_price': Decimal(str(cost)),
            'mrp': Decimal(str(mrp)),
            'mfg_date': today - timedelta(days=mfg_offset),
            'exp_date': today + timedelta(days=exp_offset),
            'quantity_on_hand': qty,
        }
    )
    if created:
        print(f'  ✓ Created: {name} (Qty: {qty})')
    else:
        print(f'  - Exists: {name}')

# Create Transactions
print('\n--- Creating Sample Transactions ---')

partners_bought = ['MedSupply India', 'PharmaDist Co', 'HealthCare Wholesale', 'National Pharma Dist', 'Metro Medical Supply']
partners_sold = ['City Hospital', 'Apollo Clinic', 'Max Healthcare', 'Fortis Pharmacy', 'Care Medical Store', 'Walk-in Customer']

medicines = list(Medicine.objects.filter(owner=user))

# Create some bought transactions (older)
for i in range(15):
    med = random.choice(medicines)
    qty = random.randint(50, 200)
    days_ago = random.randint(10, 60)
    txn, created = Transaction.objects.get_or_create(
        owner=user,
        medicine=med,
        ttype='BOUGHT',
        partner_name=random.choice(partners_bought),
        unit_price=med.cost_price,
        quantity=qty,
        defaults={
            'created_at': today - timedelta(days=days_ago),
        }
    )
    if created:
        # Don't update quantity since we already set it
        print(f'  ✓ Bought: {qty}x {med.name} from {txn.partner_name}')

# Create some sold transactions (recent)
for i in range(20):
    med = random.choice(medicines)
    if med.quantity_on_hand < 10:
        continue
    qty = random.randint(5, min(50, med.quantity_on_hand // 2))
    days_ago = random.randint(1, 30)
    txn, created = Transaction.objects.get_or_create(
        owner=user,
        medicine=med,
        ttype='SOLD',
        partner_name=random.choice(partners_sold),
        unit_price=med.mrp,
        quantity=qty,
        defaults={
            'created_at': today - timedelta(days=days_ago),
        }
    )
    if created:
        print(f'  ✓ Sold: {qty}x {med.name} to {txn.partner_name}')

# Summary
print('\n' + '=' * 50)
print('SAMPLE DATA CREATED SUCCESSFULLY!')
print('=' * 50)
print(f'\n📊 Summary:')
print(f'   • Manufacturers: {Manufacturer.objects.count()}')
print(f'   • Medicines: {Medicine.objects.filter(owner=user).count()}')
print(f'   • Transactions: {Transaction.objects.filter(owner=user).count()}')
print(f'\n🔐 Demo Login:')
print(f'   Email: demo@medshop.com')
print(f'   Password: Demo@1234')
print(f'\n🌐 Access the app at: http://127.0.0.1:8000/')
print('=' * 50)
