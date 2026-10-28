# Student Attendance Management System

A web-based college mini-project built with **Python Django**, **Bootstrap 5**, and **SQLite**.

## Features

- 🔒 Secure faculty login (Django's built-in auth)
- 🎓 Student management (Add / Edit / View / Delete)
- ✅ Daily attendance marking with Present/Absent radio buttons
- 📊 Attendance reports with percentage calculations
- ⚠️ Low attendance warning (below 75%)
- 📅 Attendance history per student
- 📥 CSV export for reports
- 📱 Responsive Bootstrap 5 UI

---

## Windows Setup Instructions

### Step 1 — Prerequisites
- Python 3.10 or higher ([python.org](https://www.python.org/downloads/))
- Make sure Python is added to PATH during installation.

### Step 2 — Open PowerShell in the Project Folder
Right-click the project folder → **Open in Terminal** (PowerShell)

Or navigate to it:
```powershell
cd "C:\Users\MADHU KRISHNA\OneDrive\Documents\project\small"
```

### Step 3 — (Optional) Create Virtual Environment
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

> **Tip:** If you get an execution policy error, run:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Step 4 — Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 5 — Run Migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Step 6 — Create Faculty Account (Superuser)
```powershell
python manage.py createsuperuser
```
Enter your preferred **username**, **email** (optional), and **password**.

### Step 7 — (Optional) Load Demo Students
```powershell
python manage.py load_demo_students
```

### Step 8 — Start the Development Server
```powershell
python manage.py runserver
```

### Step 9 — Open the Website
Open your browser and visit:
```
http://127.0.0.1:8000/
```
Login with the credentials you created in Step 6.

### Step 10 — Run Tests
```powershell
python manage.py test attendance
```

---

## Login & Navigation

| URL | Description |
|-----|-------------|
| `http://127.0.0.1:8000/login/` | Faculty Login |
| `http://127.0.0.1:8000/` | Dashboard |
| `http://127.0.0.1:8000/students/` | Student List |
| `http://127.0.0.1:8000/attendance/mark/` | Mark Attendance |
| `http://127.0.0.1:8000/reports/` | Attendance Reports |
| `http://127.0.0.1:8000/admin/` | Django Admin |

---

## Troubleshooting

**Python not found:**
- Reinstall Python and ensure "Add to PATH" is checked.
- Or use the full path: `C:\Python312\python.exe manage.py runserver`

**Virtual environment activation blocked:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Django not installed:**
```powershell
pip install django==5.1.4
```

**Migration errors:**
```powershell
python manage.py makemigrations attendance
python manage.py migrate
```

**Port 8000 already in use:**
```powershell
python manage.py runserver 8080
# Then visit http://127.0.0.1:8080/
```

**Database issues — reset cleanly:**
```powershell
del db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

---

## Project Structure

```
small/
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3            ← Created after migrate
├── attendance_system/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── attendance/
    ├── models.py         ← Student & Attendance models
    ├── views.py          ← All application logic
    ├── forms.py          ← Django forms
    ├── urls.py           ← URL routing
    ├── admin.py          ← Admin configuration
    ├── tests.py          ← Automated tests
    ├── management/
    │   └── commands/
    │       └── load_demo_students.py
    ├── templates/
    │   └── attendance/   ← All HTML templates
    └── static/
        └── attendance/
            ├── css/style.css
            └── js/main.js
```

---

## Technology Stack

- Python 3.12
- Django 5.1.4
- SQLite (built-in)
- Bootstrap 5.3
- Bootstrap Icons 1.11
- Vanilla JavaScript

---

*Mini-Project — Student Attendance Management System*
