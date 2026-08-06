# 📚 MedShop Tracker Documentation

## Project Architecture

The MedShop Tracker is built using the Django web framework and follows the MVT (Model-View-Template) architectural pattern.

### Overall Project Structure (Project Flow)
Below is the core structural organization of the MedShop Tracker:
```text
medstock/ (Root Directory)
├── medshop/               # Main Django Configuration (Settings, Core Routing)
├── accounts/              # User Management (Login, Roles, Profiles)
├── inventory/             # Core Logic (Medicines, Suppliers, Transactions)
├── reports/               # Data Processing & Visualization (Pandas, Plotly)
├── templates/             # HTML UI templates (Tailwind CSS applied here)
├── static/                # Static assets (CSS, JS, Images)
├── db.sqlite3             # Default Database
└── manage.py              # Django Project Manager
```

**Project Flow**:
1. **User Request**: A user interacts with the frontend (e.g., clicks "Add Medicine"). The browser sends an HTTP request.
2. **URL Routing**: `medshop/urls.py` captures the request and routes it to the specific app (like `inventory`).
3. **View Logic**: The app's `views.py` processes the request, optionally checking user permissions from `accounts`.
4. **Database Interaction (Models)**: The view queries or updates `models.py` (e.g., adjusting stock in the database).
5. **Context & Templates**: Data is passed as context to a Django template in the `templates/` directory.
6. **Response**: The server sends back the rendered HTML page with Tailwind styling to the user.

### Key Applications
- **`accounts`**: Manages user authentication, custom user models, and profiles.
- **`inventory`**: Handles medicine inventory, stock levels, and batch tracking.
- **`reports`**: Manages analytics, revenue dashboard, and data visualization.
- **`medshop`**: The core Django project directory containing settings and routing.

### Data Flow
1. **Views**: Process incoming HTTP requests and interact with models to retrieve or update data.
2. **Models**: Define the database schema and handle data storage (using SQLite by default).
3. **Templates**: Render the UI using HTML and Tailwind CSS, populated with data from the views.

## Core Features Breakdown

### Inventory Management
The system tracks medicines with details such as:
- **Name and ID**
- **Batch Number**
- **Expiry Date**
- **Stock Quantity**
- **Pricing** (Cost Price and Selling Price)

The inventory automatically updates when transactions (buy/sell) occur.

### Transactions
Every transaction is logged to maintain a full audit trail.
- **Buy Transactions**: Increase stock levels and record supplier details.
- **Sell Transactions**: Decrease stock levels and record customer details.

### Analytics and Visualization
The application leverages Pandas and Plotly to generate real-time charts and reports on:
- Daily, Weekly, and Monthly Revenue
- Fast-moving vs. Slow-moving items
- Profitability Analysis

## Demo Credentials
If you are testing the application, you can use the following default roles:
- **Admin**: Has full access to manage users, inventory, and system settings.
- **Staff/Pharmacist**: Can manage inventory, process transactions, but cannot alter system settings.
*(Note: Ensure you create these users or run the sample data script if testing locally).*
