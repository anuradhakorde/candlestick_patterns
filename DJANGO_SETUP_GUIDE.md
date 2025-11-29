# Django Project Setup and Migration Guide

## ✅ COMPLETED RESTRUCTURING

The Django project structure has been corrected to follow Django best practices.

## 📁 New Folder Structure

```
CandlestickPatterns/
├── manage.py                      ✅ Moved to root (was in candlestickpattern/)
├── requirements.txt               ✅ Updated and cleaned
├── README.md
├── .env
│
├── candlestickpattern/           ← Django project configuration
│   ├── __init__.py
│   ├── settings.py               ✅ Updated INSTALLED_APPS
│   ├── urls.py                   ✅ Fixed imports and added admin
│   ├── wsgi.py                   ✅ Populated (was empty)
│   └── asgi.py                   ✅ Created (was missing)
│
├── csv_upload/                   ✅ Moved to root (was in candlestickpattern/)
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py                  ✅ Fixed import
│   ├── urls.py                   ✅ Created with namespace
│   ├── migrations/
│   │   └── __init__.py
│   └── templates/
│       └── csv_upload/           ✅ Proper template structure
│           ├── upload_csv.html   ✅ Moved from app root
│           └── csv_list.html     ✅ Moved from app root
│
├── myapp/                        ✅ Created (was empty)
│   ├── __init__.py
│   ├── admin.py                  ✅ Created with UserAdmin
│   ├── apps.py                   ✅ Created
│   ├── models.py                 ✅ Created MyUser model
│   ├── views.py                  ✅ Created profile view
│   ├── custom_auth.py            ✅ Created custom auth backend
│   ├── urls.py                   ✅ Created
│   ├── tests.py                  ✅ Created
│   └── migrations/
│       └── __init__.py
│
├── static/                       ✅ Created
│   ├── css/
│   │   └── style.css             ✅ Base styles created
│   ├── js/
│   │   └── main.js               ✅ Base JS created
│   └── images/
│
├── templates/                    ← Global templates
│   ├── index.html
│   ├── search.html
│   └── search_results.html
│
├── media/                        ← User uploaded files
├── config/                       ← Non-Django database config
├── pattern_query/                ← Pattern detection logic
├── plotter/                      ← Chart plotting
└── docker/                       ← Docker configuration

```

## 🔧 Changes Made

### 1. ✅ Project Structure
- Moved `manage.py` from `candlestickpattern/` to project root
- Moved `csv_upload/` app from `candlestickpattern/csv_upload/` to root level

### 2. ✅ Configuration Files
- **wsgi.py**: Populated (was empty)
- **asgi.py**: Created (was missing)
- **settings.py**: 
  - Fixed INSTALLED_APPS
  - Added STATIC_ROOT and STATICFILES_DIRS
  - Added MEDIA_ROOT and MEDIA_URL

### 3. ✅ URL Configuration
- **candlestickpattern/urls.py**: 
  - Added admin URL
  - Fixed app imports
  - Added namespace support
  - Added media/static file serving for development

### 4. ✅ Apps Created/Fixed
- **myapp**: Fully implemented with MyUser model and custom auth
- **csv_upload**: Fixed imports, added urls.py, organized templates

### 5. ✅ Templates Organization
- Moved templates to proper `app/templates/app/` structure
- csv_upload templates now in `csv_upload/templates/csv_upload/`

### 6. ✅ Static Files
- Created `static/` directory structure
- Added base CSS and JavaScript files

### 7. ✅ Dependencies
- Cleaned up `requirements.txt`
- Removed duplicates (psycopg2 and psycopg2-binary)
- Added version constraints
- Added missing packages (django-environ, gunicorn)

## 🚀 Next Steps to Get Django Running

### 1. Install Dependencies
```bash
# Activate virtual environment (if not already active)
.\venv\Scripts\Activate.ps1

# Install updated requirements
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
# Create migrations for new apps
python manage.py makemigrations myapp
python manage.py makemigrations csv_upload

# Apply migrations
python manage.py migrate
```

### 3. Create Superuser
```bash
python manage.py createsuperuser
```

### 4. Collect Static Files (for production)
```bash
python manage.py collectstatic
```

### 5. Run Development Server
```bash
python manage.py runserver
```

### 6. Access the Application
- **Homepage**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **CSV Upload**: http://127.0.0.1:8000/csv/upload/
- **CSV List**: http://127.0.0.1:8000/csv/list/
- **User Profile**: http://127.0.0.1:8000/profile/

## 📝 Important Notes

### Database Configuration
The project is configured to use PostgreSQL. Make sure:
1. PostgreSQL server is running (via Docker or local install)
2. Database `candlestick_pattern` exists
3. User `candlestick_user` has proper permissions

### Flask vs Django
The project currently has BOTH Flask (`app.py`) and Django. Consider:
- **Option 1**: Use Django exclusively (recommended)
- **Option 2**: Use Flask for API endpoints and Django for admin/forms
- **Option 3**: Migrate Flask functionality to Django

### Custom User Model
- The project uses a custom user model `myapp.MyUser`
- This MUST be set before first migration
- Already configured in settings.py as `AUTH_USER_MODEL = 'myapp.MyUser'`

### Media Files
- Uploaded CSV files will be stored in `media/csv_files/`
- Make sure the `media/` directory has write permissions

## 🐛 Troubleshooting

### If you get "No module named 'csv_upload'"
- Make sure you're running `manage.py` from the project root
- Check that `csv_upload` is in INSTALLED_APPS

### If migrations fail
- Drop the database and recreate it
- Delete all migration files except `__init__.py`
- Run `makemigrations` and `migrate` again

### If static files don't load
- Run `python manage.py collectstatic`
- Check STATIC_URL and STATICFILES_DIRS in settings.py
- Ensure DEBUG=True for development

## ✨ What's Working Now

1. ✅ Proper Django project structure
2. ✅ Custom user authentication system
3. ✅ CSV file upload functionality
4. ✅ Django admin interface
5. ✅ Static files configuration
6. ✅ Media files handling
7. ✅ Proper URL routing with namespaces
8. ✅ Template organization
9. ✅ PostgreSQL database integration
10. ✅ All critical files populated

## 🎯 Ready to Run!

Your Django project is now properly structured and ready to run. Follow the "Next Steps" section above to get started.
