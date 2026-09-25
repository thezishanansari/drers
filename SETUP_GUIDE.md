# DRERS — Complete Setup Guide (Beginner Friendly)

Disaster Reporting & Emergency Response System
Django 5 + MySQL. Follow the steps in order — do not skip any.

---

## 1. What you need installed first

| Software | Check it works | Where to get it |
|---|---|---|
| Python 3.10+ | `python --version` | python.org/downloads (tick **Add Python to PATH**) |
| MySQL Server 8 | `mysql --version` | dev.mysql.com/downloads/installer |
| VS Code | — | code.visualstudio.com |

> **Windows users:** in every command below, use `python`.
> **macOS / Linux users:** use `python3`.

---

## 2. Final folder structure

Put the whole `drers_django_project` folder wherever you like, e.g. `D:\DRERS\`.
This is exactly what you should end up with:

```
DRERS/                                  <- outer folder (any name)
└── drers_django_project/               <- PROJECT ROOT (manage.py lives here)
    ├── env/                            <- virtual environment (you create in step 3)
    ├── manage.py
    ├── requirements.txt
    ├── .env                            <- you create in step 5 (copy of .env.example)
    ├── .env.example
    ├── .gitignore
    │
    ├── drers/                          <- project settings package
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   ├── wsgi.py
    │   └── asgi.py
    │
    ├── core/                           <- the main app (all logic)
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── context_processors.py       <- live header ticker
    │   ├── forms.py
    │   ├── models.py
    │   ├── urls.py
    │   ├── views.py
    │   ├── migrations/
    │   │   ├── __init__.py
    │   │   └── 0001_initial.py
    │   └── management/commands/
    │       ├── __init__.py
    │       └── seed_data.py            <- creates demo users + alerts
    │
    ├── templates/                      <- ALL HTML lives here
    │   ├── base.html                   <- header + warning stripe + ticker
    │   ├── _auth_left.html             <- shared left hero column
    │   ├── _stats.html
    │   ├── _report_table.html
    │   ├── login.html                  <- SCREENSHOT 1
    │   ├── register.html               <- SCREENSHOT 2
    │   ├── public_alerts.html          <- SCREENSHOT 3
    │   ├── dashboard_citizen.html
    │   ├── dashboard_responder.html
    │   ├── dashboard_admin.html
    │   ├── report_form.html
    │   └── report_detail.html
    │
    ├── static/                         <- ALL CSS/JS lives here
    │   ├── css/style.css               <- the entire dark design
    │   └── js/main.js                  <- ticker + flash messages
    │
    └── media/                          <- uploaded incident photos
```

**Rule of thumb:** `.html` → `templates/`, `.css` → `static/css/`, `.js` → `static/js/`,
Python logic → `core/`, configuration → `drers/`.

---

## 3. Create the virtual environment

Open a terminal **inside `drers_django_project`** (the folder with `manage.py`):

```bash
cd path/to/drers_django_project

# create it
python -m venv env
```

Activate it — you must do this **every time** you work on the project:

```bash
# Windows (PowerShell)
env\Scripts\activate

# Windows (CMD)
env\Scripts\activate.bat

# macOS / Linux
source env/bin/activate
```

Your prompt now starts with `(env)`. That means it worked.

> PowerShell error about scripts being disabled? Run once:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

---

## 4. Install the libraries

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:

| Library | Why |
|---|---|
| `Django==5.0.6` | the web framework |
| `mysqlclient` | lets Django talk to MySQL |
| `python-dotenv` | reads your `.env` secrets file |
| `Pillow` | required for incident photo uploads |

> **If `mysqlclient` fails to install:**
> * Windows → `pip install mysqlclient --only-binary :all:`
>   still failing? use `pip install pymysql` and add these 2 lines at the top of `drers/__init__.py`:
>   ```python
>   import pymysql
>   pymysql.install_as_MySQLdb()
>   ```
> * Ubuntu → `sudo apt install python3-dev default-libmysqlclient-dev build-essential`
> * macOS → `brew install mysql pkg-config`

---

## 5. Create the MySQL database

Log into MySQL:

```bash
mysql -u root -p
```

Then run these 4 lines (change the password to your own):

```sql
CREATE DATABASE drers_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'drers_user'@'localhost' IDENTIFIED BY 'YourStrongPassword123';
GRANT ALL PRIVILEGES ON drers_db.* TO 'drers_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Now create your secrets file. Copy `.env.example` to `.env`:

```bash
# Windows
copy .env.example .env
# macOS / Linux
cp .env.example .env
```

Open `.env` and set the **same** password you just used:

```
SECRET_KEY=any-long-random-text-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=drers_db
DB_USER=drers_user
DB_PASSWORD=YourStrongPassword123
DB_HOST=127.0.0.1
DB_PORT=3306
```

> `.env` is in `.gitignore` — your password never goes to GitHub. 

---

## 6. Create the tables

```bash
python manage.py makemigrations
python manage.py migrate
```

You should see a list of `... OK` lines. Your MySQL database now has these tables:

| Table | Holds |
|---|---|
| `auth_user` | usernames + hashed passwords (built into Django) |
| `drers_profile` | role (citizen/responder/admin) + phone |
| `drers_report` | every disaster report |
| `drers_response_update` | the audit trail / timeline |

---

## 7. Add the demo data

```bash
python manage.py seed_data
```

This creates the three accounts and the three alerts from the design:

| Role | Username | Password |
|---|---|---|
| Administrator | `admin` | `admin123` |
| Responder | `responder1` | `resp123` |
| Citizen | `sita` | `sita123` |

Want your own superuser instead? `python manage.py createsuperuser`

---

## 8. Run it

```bash
python manage.py runserver
```

Open your browser:

| Page | URL |
|---|---|
| Login (screenshot 1) | http://127.0.0.1:8000/login/ |
| Register (screenshot 2) | http://127.0.0.1:8000/register/ |
| Public Alerts (screenshot 3) | http://127.0.0.1:8000/alerts/ |
| Dashboard (after login) | http://127.0.0.1:8000/dashboard/ |
| Django admin panel | http://127.0.0.1:8000/admin/ |

Stop the server with `Ctrl + C`.

---

## 9. What works (all tested)

**Authentication**
- Login with real Django `authenticate()` + sessions; wrong password shows
  *"Invalid username or password."*
- Registration validates full name, username format, 10-digit phone starting
  with 9, 6-char password, and duplicate usernames.
- **Registration always creates a Citizen.** Role is never an input field, so a
  visitor can never make themselves Admin or Responder.
- Logout clears the session.

**Role-based dashboards** (one URL, `/dashboard/`, renders the right one)
- *Citizen* → own reports + "Report an Incident" button.
- *Responder* → reports assigned to them + the pending queue.
- *Admin* → every report + link to the Django admin.

**Reports**
- Citizens submit incidents (with optional photo upload).
- Admin assigns a responder; responders update status.
- Every change is logged to the response timeline.
- Auto-generated reference codes: `DR-000001`, `DR-000002`, …

**Security (verified by test)**
- A citizen cannot open another citizen's report.
- A citizen cannot change status or assign responders.
- A responder cannot assign responders (admin only).
- CSRF protection on every form; passwords stored hashed, never plain text.

---

## 10. Everyday workflow

```bash
cd drers_django_project
env\Scripts\activate        # or: source env/bin/activate
python manage.py runserver
```

After you change `models.py`:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 11. Common errors and fixes

| Error | Fix |
|---|---|
| `No module named 'django'` | The venv isn't active. Run the activate command from step 3. |
| `Access denied for user 'drers_user'` | Password in `.env` ≠ password in MySQL. Redo step 5. |
| `Unknown database 'drers_db'` | You skipped `CREATE DATABASE`. Redo step 5. |
| `Can't connect to MySQL server` | MySQL service is not running. Start it in Services (Windows) or `brew services start mysql`. |
| Page loads but has **no styling** | `DEBUG` must be `True` in `.env`, and CSS must be at `static/css/style.css`. Hard-refresh with `Ctrl+F5`. |
| `TemplateDoesNotExist` | The `templates/` folder must sit next to `manage.py`. |
| `CSRF verification failed` | Every `<form method="post">` needs `{% csrf_token %}`. |
| Port 8000 busy | `python manage.py runserver 8001` |

---

## 12. Before going live (later)

1. `DEBUG=False` in `.env`
2. Put your real domain in `ALLOWED_HOSTS`
3. Generate a fresh long `SECRET_KEY`
4. `python manage.py collectstatic`
5. Serve with Gunicorn/uWSGI behind Nginx, and enable HTTPS

---

## 13. Design reference (already applied in `style.css`)

| Purpose | Colour |
|---|---|
| Background | `#0d0c0b` |
| Header | `#151412` |
| Panels | `#201b17` |
| Dark panels | `#171513` |
| Emergency red | `#d71920` |
| Amber | `#f2a62b` |
| White | `#f5f2ed` |
| Body text | `#d0c6bb` |
| Muted text | `#9f968c` |
| Border | `#3a322c` |
| Green | `#36a65b` |
| Purple | `#9c75df` |

Fonts: **Oswald** (headings), **Inter** (body), **JetBrains Mono** (technical labels).
The warning stripe and diagonal background are pure CSS `repeating-linear-gradient()` —
no images, so they load instantly.
