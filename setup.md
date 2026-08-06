# 🚀 Installation & Setup Guide

## Prerequisites
Before you begin, ensure you have the following installed on your system:
- **Python** `3.10+`
- **pip** package manager
- **git** (for cloning the repository)

## Step-by-Step Installation

### 1. Clone & Navigate
First, clone the repository to your local machine:
```bash
git clone https://github.com/Mrinmoypatratint/medstock.git
cd medstock
```

### 2. Create a Virtual Environment
It is recommended to use a virtual environment to manage dependencies:
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
Install the required packages using the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### 4. Database Setup
Apply the initial database migrations to set up the SQLite database:
```bash
python manage.py makemigrations
python manage.py migrate
```

*(Optional)* If you want to populate the database with sample data for testing, run:
```bash
python populate_sample_data.py
```

### 5. Create a Superuser (Optional)
To access the Django admin interface, create a superuser account:
```bash
python manage.py createsuperuser
```

### 6. Run the Development Server
Start the local development server:
```bash
python manage.py runserver
```
The application will now be running at `http://127.0.0.1:8000/`.
