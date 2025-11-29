# 🔍 Django Project Verification Checklist

Use this checklist to verify that your Django project is properly set up and working.

## ✅ Pre-Flight Checks

### 1. File Structure Verification
- [ ] `manage.py` exists at project root (not in subdirectory)
- [ ] `candlestickpattern/wsgi.py` is not empty
- [ ] `candlestickpattern/asgi.py` exists
- [ ] `myapp/` directory has files (not empty)
- [ ] `csv_upload/` is at root level (not in candlestickpattern/)
- [ ] `static/` directory exists with css/, js/, images/
- [ ] Templates are in `csv_upload/templates/csv_upload/`

### 2. Configuration Files
- [ ] `candlestickpattern/settings.py` includes both apps in INSTALLED_APPS
- [ ] `candlestickpattern/urls.py` includes admin URLs
- [ ] `csv_upload/urls.py` exists with app_name = 'csv_upload'
- [ ] `myapp/urls.py` exists with app_name = 'myapp'

### 3. Database Connection
- [ ] PostgreSQL server is running
- [ ] Database 'candlestick_pattern' exists
- [ ] User 'candlestick_user' has proper permissions

---

## 🚀 Setup Steps

### Step 1: Activate Virtual Environment
```powershell
cd d:\Projects\CandlestickPatterns
.\venv\Scripts\Activate.ps1
```
**Expected**: Prompt shows (venv) prefix

- [ ] Virtual environment activated

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```
**Expected**: All packages install without errors

- [ ] Django installed
- [ ] psycopg2-binary installed
- [ ] All dependencies installed successfully

### Step 3: Check Django Installation
```powershell
python manage.py --version
```
**Expected**: Shows Django version (e.g., 3.2.x)

- [ ] Django version displays correctly

### Step 4: Verify Apps Are Recognized
```powershell
python manage.py check
```
**Expected**: "System check identified no issues (0 silenced)."

- [ ] No errors in system check
- [ ] If you see warnings, note them: _______________

### Step 5: Create Migrations
```powershell
python manage.py makemigrations myapp
python manage.py makemigrations csv_upload
```
**Expected**: Creates migration files for both apps

- [ ] myapp migrations created
- [ ] csv_upload migrations created
- [ ] No errors during migration creation

### Step 6: Apply Migrations
```powershell
python manage.py migrate
```
**Expected**: All migrations apply successfully

- [ ] Database tables created
- [ ] No migration errors
- [ ] Auth tables created
- [ ] MyUser table created
- [ ] CsvFile table created

### Step 7: Create Superuser
```powershell
python manage.py createsuperuser
```
**Expected**: Prompts for username, email, password

- [ ] Superuser created successfully
- [ ] Username: _______________
- [ ] Email: _______________

### Step 8: Collect Static Files (Optional)
```powershell
python manage.py collectstatic --noinput
```
**Expected**: Static files copied to staticfiles/

- [ ] Static files collected (if needed)

### Step 9: Start Development Server
```powershell
python manage.py runserver
```
**Expected**: Server starts on http://127.0.0.1:8000/

- [ ] Server starts without errors
- [ ] No warnings (or acceptable warnings noted)

---

## 🌐 Testing Access Points

### Test 1: Homepage
**URL**: http://127.0.0.1:8000/
**Expected**: Displays homepage or 404 (depends on root URL configuration)

- [ ] Page loads
- [ ] No 500 errors

### Test 2: Admin Panel
**URL**: http://127.0.0.1:8000/admin/
**Expected**: Django admin login page

- [ ] Admin login page displays
- [ ] Can login with superuser credentials
- [ ] Can see "Users" (MyUser model)
- [ ] Can see "Csv Files" (CsvFile model)

### Test 3: CSV Upload
**URL**: http://127.0.0.1:8000/csv/upload/
**Expected**: CSV upload form

- [ ] Upload form displays
- [ ] Form has file and date fields
- [ ] No template errors

### Test 4: CSV List
**URL**: http://127.0.0.1:8000/csv/list/
**Expected**: List of uploaded CSV files (or empty list)

- [ ] List page displays
- [ ] No database errors
- [ ] No template errors

### Test 5: User Profile
**URL**: http://127.0.0.1:8000/profile/
**Expected**: Profile page (requires login) or redirect to login

- [ ] Page loads or redirects to login
- [ ] No 500 errors

### Test 6: Static Files
**Check**: View page source and verify CSS/JS loads
**Expected**: Static files serve correctly in DEBUG mode

- [ ] CSS loads (check browser dev tools)
- [ ] JS loads (check browser dev tools)
- [ ] No 404 for static files

---

## 🐛 Common Issues and Solutions

### Issue: "No module named 'csv_upload'"
**Solution**: Make sure you're in the project root directory where manage.py is located
```powershell
cd d:\Projects\CandlestickPatterns
python manage.py runserver
```

### Issue: "Table does not exist"
**Solution**: Run migrations
```powershell
python manage.py migrate
```

### Issue: "FATAL: password authentication failed"
**Solution**: Check PostgreSQL connection in settings.py
- Verify database name, user, password
- Ensure PostgreSQL is running
- Test connection: `psql -U candlestick_user -d candlestick_pattern`

### Issue: "Template does not exist"
**Solution**: Check template paths
- Verify templates are in `app/templates/app/` structure
- Check TEMPLATES configuration in settings.py

### Issue: Static files not loading
**Solution**: 
1. Ensure DEBUG=True in settings.py
2. Check STATIC_URL and STATICFILES_DIRS
3. Verify static files exist in static/ directory

### Issue: "ImproperlyConfigured: AUTH_USER_MODEL refers to model 'myapp.MyUser' that has not been installed"
**Solution**: 
1. Check INSTALLED_APPS includes 'myapp.apps.MyappConfig'
2. Run makemigrations: `python manage.py makemigrations myapp`
3. Run migrate: `python manage.py migrate`

---

## ✨ Success Indicators

Your Django project is working correctly if:

1. ✅ Server starts without errors
2. ✅ Admin panel is accessible
3. ✅ Can create and login with superuser
4. ✅ All app URLs load (even if with 404 for missing templates)
5. ✅ No 500 Internal Server Errors
6. ✅ Database migrations complete successfully
7. ✅ Static files load in browser
8. ✅ Can upload CSV file through admin or upload form

---

## 📋 Final Verification

Check all these statements are true:

- [ ] Project structure follows Django conventions
- [ ] manage.py is at project root
- [ ] All apps are properly installed
- [ ] Database migrations are complete
- [ ] Superuser account created
- [ ] Development server runs without errors
- [ ] Admin panel accessible
- [ ] At least one app URL works correctly
- [ ] Static files configuration is correct
- [ ] No critical errors in console

---

## 🎯 Next Steps After Verification

Once all checks pass:

1. **Develop Features**: Start building your candlestick pattern detection features
2. **Create Templates**: Design proper HTML templates for your views
3. **Add Data**: Import historical stock data via CSV uploads
4. **Test Patterns**: Implement and test pattern detection algorithms
5. **Integrate Plotly**: Add interactive charts to visualize patterns
6. **Write Tests**: Create unit tests for your models and views
7. **Documentation**: Document your API and features

---

## 📞 Getting Help

If you encounter issues not covered here:

1. Check Django documentation: https://docs.djangoproject.com/
2. Review error logs in terminal
3. Check browser console for JavaScript errors
4. Verify PostgreSQL logs for database issues
5. Use `python manage.py check --deploy` for deployment readiness

---

**Last Updated**: November 22, 2025
**Django Version**: 3.2.x
**Python Version**: 3.x
