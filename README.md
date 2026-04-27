# 🏠 RentHu Uganda

A comprehensive real estate rental platform for the Ugandan market with property listings, bookings, maintenance management, agent connections, and payment processing.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup
```bash
cd find_your_perfect_home
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8001
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Access
- Frontend: http://localhost:5173
- Backend API: http://localhost:8001/api/
- Admin Panel: http://localhost:8001/admin/

## 🌟 Key Features

- **Property Management**: Listings, search, images, detailed info
- **User System**: Multi-role (Tenant, Owner, Agent, Admin)
- **Agent Network**: Verified agents with smart assignment
- **Maintenance System**: Complete ticket management with notifications
- **Booking System**: Seamless booking with availability tracking
- **Payment Processing**: Mobile money & credit card integration
- **Analytics Dashboard**: Comprehensive reporting for all users
- **AI Assistant**: Intelligent chatbot for customer support

## 🛠️ Tech Stack

- **Backend**: Django 4.2.7 + Django REST Framework
- **Frontend**: React 19.2.4 + Vite 8.0.0
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Authentication**: JWT tokens
- **Payments**: Mobile money + Stripe integration

## 📁 Project Structure

```
projectA/
├── find_your_perfect_home/  # Django backend
│   ├── accounts/           # User management
│   ├── properties/         # Property CRUD
│   ├── bookings/          # Booking system
│   ├── payments/          # Payment processing
│   ├── maintenance/       # Maintenance management
│   ├── agents/            # Agent system
│   ├── notifications/     # Notification system
│   ├── analytics/         # Analytics & reporting
│   ├── audit_logs/        # System auditing
│   ├── refunds/           # Refund management
│   ├── ai_agent/          # AI chatbot
│   ├── mobile_money/      # Mobile money payments
│   ├── credit_cards/      # Credit card payments
│   └── ussd/              # USSD services
└── frontend/              # React frontend
    ├── src/components/    # Reusable components
    ├── src/pages/        # Page components
    └── src/services/     # API services
```




## 🚀 Deployment

```bash
# Backend
python manage.py collectstatic
gunicorn find_your_perfect_home.wsgi:application

# Frontend
npm run build
```

## 📄 License

MIT License - see LICENSE file for details.

---

**Built with ❤️ for the Ugandan real estate market**
