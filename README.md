# 💊 MedShop Tracker

A modern, responsive inventory management system designed for medical shops and pharmacies. Built with **Django 5** and **Tailwind CSS**.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.0.6-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Installation & Setup](#-installation--setup)
- [Demo Credentials](#-demo-credentials)
- [Project Architecture](#-project-architecture)
- [API Endpoints](#-api-endpoints)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🏥 Inventory Management
- **Medicine Tracking** – Complete CRUD functionality with batch details and IDs.
- **Real-Time Stock Updates** – Automatic inventory level adjustments upon transaction entry.
- **Expiry Monitoring** – Visual alert indicators for expired or near-expiry (≤30 days) inventory.

### 💰 Transactions & Audit Trail
- **Buy/Sell Records** – Log supplier purchases and customer sales.
- **Partner Management** – Track vendor and client relationships.
- **Full Audit History** – Easily search and review past transactions.

### 📊 Analytics & Reporting
- **Revenue Dashboard** – Real-time tracking across daily, weekly, monthly, and yearly windows.
- **Data Visualizations** – Interactive charts powered by Plotly & Pandas.
- **Data Portability** – One-click CSV exports for accounting and auditing.

### 🔐 Security & User Management
- **Custom Authentication** – Email-based sign-in system.
- **Document Management** – Secure storage for government IDs and drug licenses.

---

## 🛠 Tech Stack

| Component | Technology |
|---|---|
| **Language** | Python 3.10+ |
| **Framework** | Django 5.0.6 |
| **Database** | SQLite (Production ready for PostgreSQL) |
| **Styling** | Tailwind CSS |
| **Analytics** | Pandas, NumPy, Plotly |

---

## 🚀 Installation & Setup

### Prerequisites
- Python `3.10+`
- `pip` package manager
- `git`

### 1. Clone & Navigate
```bash
git clone [https://github.com/yourusername/medshop-tracker.git](https://github.com/yourusername/medshop-tracker.git)
cd medshop-

