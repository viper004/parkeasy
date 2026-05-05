# ParkEasy - Intelligent Parking Management System

[![Django](https://img.shields.io/badge/Django-6.0.3-darkgreen)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

**ParkEasy** is a comprehensive Django-based parking management system designed for apartment complexes and residential communities. It streamlines vehicle registration, parking slot allocation, and real-time vehicle gate access tracking with role-based user management.

## Key Features

- 🚗 **Vehicle Management** - Register, approve, and track vehicles (2-wheelers & 4-wheelers)
- 🛡️ **Role-Based Access Control** - Three distinct user roles (Admin, Residents, Security Staff)
- 🔐 **QR Code Generation** - Automatic QR code generation for approved vehicles
- 📋 **Vehicle Documentation** - Upload and manage RC books and vehicle images
- ✅ **Admin Approval System** - Vehicle approval/rejection workflow with assigned parking slots
- 📊 **Real-time Gate Access Logging** - Track vehicle entry/exit with staff and timestamps
- 🔍 **Advanced Search & Filtering** - Search members and vehicles by name, flat number, or phone
- 📸 **Security Staff Management** - Add and manage security personnel with photos

---

## System Architecture

### Architecture Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     ParkEasy System Architecture                │
└─────────────────────────────────────────────────────────────────┘

                          LOGIN PORTAL
                        (home page)
                              │
                    ┌─────────┼─────────┐
                    │         │         │
                    ▼         ▼         ▼
              ┌──────────┐ ┌──────────┐ ┌──────────────┐
              │  ADMIN   │ │ RESIDENT │ │ SECURITY     │
              │          │ │  (USER)  │ │ STAFF        │
              └────┬─────┘ └────┬─────┘ └──────┬───────┘
                   │            │              │
        ┌──────────┴────┐       │              │
        ▼               ▼       ▼              ▼
   ┌─────────┐  ┌───────────┐┌──────────┐┌──────────────┐
   │Dashboard│  │Dashboard  ││Dashboard ││Gate Control  │
   │         │  │           ││          ││              │
   │-Members │  │-My        ││-Recent   ││-Scan Vehicle │
   │ -Vehicles│  │ Vehicles  ││ Logs     ││-Log Entry/   │
   │ -Security│  │-Register  ││-Security ││ Exit         │
   │  Staff   │  │ New Vehicle││Staff Info│              │
   └────┬────┘  └─────┬─────┘└────┬─────┘└──────┬───────┘
        │              │           │             │
        ▼              ▼           ▼             ▼
    ┌────────────────────────────────────────────────┐
    │           DATABASE LAYER (SQLite)              │
    │   ┌─────────┐ ┌────────┐ ┌──────────────┐    │
    │   │  Users  │ │Vehicles│ │SecurityStaff │    │
    │   │  Admin  │ │Logs    │ │              │    │
    │   └─────────┘ └────────┘ └──────────────┘    │
    └────────────────────────────────────────────────┘
```

### Data Flow

```
Vehicle Registration Flow:
━━━━━━━━━━━━━━━━━━━━━━━━━━

User (Resident) → Add Vehicle → [RC Book + Image] → Database
                       ↓
                 Admin Reviews
                       ├─→ APPROVE → Assign Parking Slot → Generate QR Code
                       └─→ REJECT → Add Reject Reason → Notify User

Gate Access Flow:
━━━━━━━━━━━━━━━━

Vehicle at Gate → Security Scans QR/Enters Number
      ↓
  [Validate Vehicle & Approval Status]
      ├─→ NOT FOUND or NOT APPROVED → Deny Access
      ├─→ APPROVED → Toggle is_in Status (True/False)
      └─→ Log Entry/Exit Event → VehicleLog Record
```

---

## Database Schema

### Core Models

#### User (Residents)
```python
- nick_name: String (display name)
- phone: String (authentication key)
- dob: String (authentication key)
- flat_no: String (apartment unit number)
- vehicles: [Vehicle] (reverse relationship)
```

#### Admin
```python
- phone: String (authentication key)
- dob: String (authentication key)
```

#### Vehicle
```python
- user: ForeignKey → User
- number: String (registration number)
- type: Choice ('2W', '4W')
- rc_book: File (uploaded document)
- image: Image (vehicle photo)
- is_approved: Boolean (approval status)
- is_rejected: Boolean (rejection status)
- parking_slot: String (assigned slot)
- is_in: Boolean (current location: True=inside, False=outside)
- qr_code: Image (generated upon approval)
- reject_reason: Text (if rejected)
```

#### SecurityStaff
```python
- name: String
- photo: Image
- phone: String (authentication key)
- gender: String
- date_of_birth: String (authentication key)
```

#### VehicleLog
```python
- vehicle: ForeignKey → Vehicle
- staff: ForeignKey → SecurityStaff
- action: String ('IN' or 'OUT')
- timestamp: DateTime (auto-generated)
```

---

## User Roles & Permissions

| Feature | Admin | Resident | Security |
|---------|-------|----------|----------|
| View Dashboard | ✅ | ✅ | ✅ |
| Approve Vehicles | ✅ | ❌ | ❌ |
| Reject Vehicles | ✅ | ❌ | ❌ |
| Register Vehicle | ❌ | ✅ | ❌ |
| Gate Control | ❌ | ❌ | ✅ |
| View Logs | ✅ | ❌ | ✅ |
| Manage Members | ✅ | ❌ | ❌ |
| Manage Security Staff | ✅ | ❌ | ❌ |

---

## Tech Stack

- **Backend Framework**: Django 6.0.3
- **Programming Language**: Python 3.8+
- **Database**: SQLite3
- **Frontend**: HTML5, CSS, JavaScript
- **Libraries**:
  - `qrcode` - QR code generation
  - `Pillow` - Image processing
  - Django ORM - Database abstraction

---

## Project Structure

```
parkeasy/
├── db.sqlite3              # SQLite database
├── manage.py               # Django management script
├── README.md               # This file
├── media/                  # User-uploaded files
│   ├── qr_codes/          # Generated QR codes
│   ├── rc_books/          # Vehicle RC documents
│   ├── security_photos/   # Staff photos
│   └── vehicles/          # Vehicle images
├── parkease/              # Main Django app
│   ├── __init__.py
│   ├── apps.py
│   ├── asgi.py
│   ├── decorators.py      # Authentication decorators
│   ├── models.py          # Database models
│   ├── settings.py        # Django configuration
│   ├── urls.py            # URL routing
│   ├── views.py           # Request handlers
│   ├── wsgi.py
│   └── migrations/        # Database migrations
└── templates/             # HTML templates
    ├── index.html         # Home page
    ├── admin/             # Admin templates
    │   └── admin_dashboard.html
    ├── user/              # User templates
    │   └── user_dashboard.html
    └── security/          # Security templates
        └── security_dashboard.html
```

---

## API Endpoints

### Authentication
- `GET /` - Home page
- `POST /login/` - User login (phone + DOB)
- `GET /logout/` - User logout

### Admin Routes
- `GET /admin/dashboard/` - Admin dashboard
- `POST /admin/members/add/` - Add new resident
- `PUT /admin/members/<id>/update/` - Update resident
- `DELETE /admin/members/<id>/delete/` - Delete resident
- `POST /admin/vehicles/<id>/approve/` - Approve vehicle
- `POST /admin/vehicles/<id>/reject/` - Reject vehicle
- `POST /add-security/` - Add security staff
- `DELETE /delete-security/<id>/` - Remove security staff

### User Routes
- `GET /user/dashboard/` - User dashboard
- `POST /user/vehicles/add/` - Register new vehicle
- `POST /reapply-vehicle/` - Resubmit rejected vehicle

### Security Routes
- `GET /security/dashboard/` - Security dashboard
- `POST /security/gate-control/` - Record vehicle entry/exit

---

## Setup & Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/parkeasy.git
cd parkeasy
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Apply migrations**
```bash
python manage.py migrate
```

5. **Create superuser (optional)**
```bash
python manage.py createsuperuser
```

6. **Run development server**
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

---

## Authentication Details

The system uses **phone number + date of birth** as the authentication mechanism:

- **Admin** Login: Admin phone & DOB (must exist in Admin table)
- **Resident** Login: User phone & DOB (must exist in User table)
- **Security** Login: Security phone & DOB (must exist in SecurityStaff table)

No password hashing is currently implemented. For production, implement proper password-based authentication.

---

## Key Features in Detail

### 1. Vehicle Registration & Approval Workflow
- Residents upload vehicle documents (RC book, photo)
- Admin reviews pending vehicles
- Admin approves and assigns parking slot → QR code auto-generated
- Admin can reject with reason; residents can reapply

### 2. Gate Access Control
- Security scans vehicle number/QR code
- System validates vehicle approval and parking assignment
- Entry/Exit status toggled automatically
- Full audit trail maintained in VehicleLog

### 3. Real-time Logging
- Every gate access recorded with staff member and exact timestamp
- Queryable vehicle history

---

## Future Enhancements

- [ ] Mobile app (React Native/Flutter)
- [ ] Email notifications for approvals/rejections
- [ ] SMS integration for vehicle alerts
- [ ] Advanced analytics and reporting dashboard
- [ ] QR code scanning via mobile
- [ ] Payment integration for parking fees
- [ ] Vehicle maintenance tracking
- [ ] Visitor vehicle management
- [ ] OAuth2 authentication
- [ ] API with JWT tokens

---

## Security Notes

⚠️ **Current Implementation is for Development Only**

- Debug mode is enabled - disable in production
- Secret key is exposed - use environment variables
- No CSRF protection on sensitive endpoints
- Phone/DOB authentication is not secure - implement password-based auth
- Media files should be served via CDN in production

### Production Checklist
- [ ] Disable `DEBUG = True`
- [ ] Move `SECRET_KEY` to environment variable
- [ ] Set proper `ALLOWED_HOSTS`
- [ ] Implement password-based authentication
- [ ] Enable HTTPS
- [ ] Add rate limiting
- [ ] Implement proper logging
- [ ] Use environment-specific settings

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Support

For issues, questions, or suggestions, please open an issue on GitHub or contact the development team.

---

## Acknowledgments

- Built with Django 6.0.3
- QR code generation using `python-qrcode` library
- Image processing with Pillow