# 💊 MedShop Tracker

A modern, responsive inventory management system for medical shops and pharmacies. Built with Django and Tailwind CSS.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.0.6-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📋 Table of Contents

- [Features](#-features)
- [Screenshots](#-screenshots)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Usage](#-usage)
- [Demo Account](#-demo-account)
- [Project Structure](#-project-structure)
- [API Endpoints](#-api-endpoints)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🏥 Inventory Management
- **Medicine Tracking** - Add, edit, and delete medicines with detailed information
- **Stock Management** - Real-time quantity tracking with automatic updates
- **Expiry Alerts** - Visual indicators for expired, expiring (≤30 days), and OK medicines
- **Search & Filter** - Quick search by medicine name or ID

### 💰 Transaction Recording
- **Buy/Sell Transactions** - Record purchases from suppliers and sales to customers
- **Automatic Stock Updates** - Quantity adjusts automatically on transactions
- **Transaction History** - Complete audit trail with search functionality
- **Partner Management** - Track suppliers and customers

### 📊 Reports & Analytics
- **Revenue Dashboard** - Daily, weekly, monthly, and yearly revenue tracking
- **Profit Analysis** - Calculate profit/loss with visual charts
- **Expiry Loss Tracking** - Monitor losses from expired stock
- **Interactive Charts** - Plotly-powered visualizations
- **CSV Export** - Export data for external analysis

### 👤 User Management
- **Email-based Authentication** - Login with email instead of username
- **Profile Management** - Personal details, contact info, and documents
- **Government ID Upload** - Store Aadhaar, PAN, Drug License documents
- **Password Change** - Secure password management

### 📱 Responsive Design
- **Mobile-First** - Fully responsive on all devices
- **Touch-Friendly** - Optimized touch targets for mobile
- **Progressive Enhancement** - Works on all modern browsers

---

## 📸 Screenshots

### Dashboard
The main dashboard shows medicines with expiry status indicators and quick search.

### Reports
Interactive charts displaying revenue trends, top medicines, and inventory analysis.

### Records
Add medicines and record buy/sell transactions with automatic calculations.

---

## 🛠 Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.10+** | Backend programming language |
| **Django 5.0.6** | Web framework |
| **SQLite** | Database (easily switchable to PostgreSQL) |
| **Tailwind CSS** | Utility-first CSS framework |
| **Plotly** | Interactive charting library |
| **Pandas** | Data analysis for reports |
| **NumPy** | Numerical computations |

---

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/medshop-tracker.git
cd medshop-tracker
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run Migrations
```bash
python manage.py migrate
```

### Step 5: Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### Step 6: Load Sample Data (Optional)
```bash
python populate_sample_data.py
```

### Step 7: Run the Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

---

## 📖 Usage

### Adding Medicines
1. Navigate to **Records** page
2. Fill in the medicine details (name, ID, manufacturer, prices, dates)
3. Click **Save Medicine**

### Recording Transactions
1. Go to **Records** page
2. Select medicine from dropdown
3. Choose transaction type (Bought/Sold)
4. Enter partner name, unit price, and quantity
5. Click **Save Transaction**

### Viewing Reports
1. Navigate to **Reports** page
2. View revenue metrics and interactive charts
3. Click **Export CSV** to download data

### Managing Profile
1. Click **Profile** in the navigation
2. Update personal information
3. Upload government ID documents

---

## 🔐 Demo Account

Use these credentials to explore the app with sample data:

| Field | Value |
|-------|-------|
| **Email** | `demo@medshop.com` |
| **Password** | `Demo@1234` |

---

## 📁 Project Structure

```
MannaTracker/
├── accounts/                 # User authentication & profiles
│   ├── templates/accounts/   # Login, register, profile templates
│   ├── forms.py              # Authentication forms
│   ├── models.py             # Profile model
│   ├── views.py              # Auth views
│   └── urls.py               # Auth URL routes
│
├── inventory/                # Core inventory management
│   ├── templates/inventory/  # Dashboard, records, medicines
│   ├── models.py             # Medicine, Transaction, Manufacturer
│   ├── views.py              # CRUD operations
│   ├── forms.py              # Medicine & transaction forms
│   └── urls.py               # Inventory URL routes
│
├── reports/                  # Analytics & reporting
│   ├── templates/reports/    # Reports dashboard
│   └── views.py              # Report generation logic
│
├── static/                   # Static assets
│   ├── css/aPp.css           # Custom styles
│   └── js/app.js             # JavaScript functionality
│
├── templates/                # Base templates
│   ├── base.html             # Main layout
│   └── navbar.html           # Navigation component
│
├── media/                    # User uploads
│   └── gov_docs/             # Government ID documents
│
├── medshop/                  # Django project settings
│   ├── settings.py           # Configuration
│   ├── urls.py               # Root URL config
│   └── wsgi.py               # WSGI entry point
│
├── manage.py                 # Django CLI
├── requirements.txt          # Python dependencies
├── populate_sample_data.py   # Sample data script
└── README.md                 # This file
```

---

## 🔗 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/accounts/login/` | User login |
| GET/POST | `/accounts/register/` | User registration |
| GET | `/accounts/logout/` | User logout |
| GET/POST | `/accounts/profile/` | View/edit profile |

### Inventory
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Dashboard with medicine list |
| GET/POST | `/records/` | Add medicines & transactions |
| GET | `/medicines/` | Full medicine list |
| GET | `/manufacturers/` | Manufacturer management |
| GET | `/medlist/` | AJAX medicine list partial |

### Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reports/` | Analytics dashboard |

---

## 🔧 Configuration

### Environment Variables (Optional)
Create a `.env` file for production:

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgres://user:pass@host:5432/dbname
```

### Database
The project uses SQLite by default. To switch to PostgreSQL:

1. Install psycopg2: `pip install psycopg2-binary`
2. Update `DATABASES` in `settings.py`

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Mrinmoy Patra**

- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

---

## 🙏 Acknowledgments

- [Django](https://www.djangoproject.com/) - The web framework
- [Tailwind CSS](https://tailwindcss.com/) - CSS framework
- [Plotly](https://plotly.com/) - Charting library
- [Heroicons](https://heroicons.com/) - SVG icons

---

<p align="center">Made with ❤️ for medical shop owners</p>
