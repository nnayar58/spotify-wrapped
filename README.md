# 🎶 Spotify Wrapped Clone

This project is a Django-based web application that mimics the popular "Spotify Wrapped" experience, allowing users to view their Spotify listening statistics. The app includes a login system, Spotify integration, and detailed music analysis.

## 🚀 Getting Started

Follow this simple step-by-step guide to set up the project on your own development environment.

### Prerequisites

Make sure you have the following installed:

- **Python 3.13 or higher**
- **PostgreSQL**
- **Git**

### 1. **Clone the Repository**

First, clone the project to your local machine:

```bash
git clone <repository-url>
cd spotify-wrapped
```

### 2. **Create a Python Virtual Environment**

Set up a virtual environment to manage dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # For macOS/Linux
venv\Scripts\activate     # For Windows
```

### 3. **Install Project Requirements**

Install the Python dependencies using `pip`:

```bash
pip install -r requirements.txt
```

### 4. **Set Up Environment Variables**

Create a `.env` file in the root directory of the project:

```bash
touch .env
```

Add the following environment variables to the `.env` file:

```
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/callback/
```

### 5. **Set Up the PostgreSQL Database**

Log in to your PostgreSQL server and create the database and user (use the exact commands without changing the name or password):

```sql
CREATE DATABASE rohitgogi;
CREATE USER rohitgogi WITH PASSWORD 'this_is_password123';
ALTER ROLE rohitgogi SET client_encoding TO 'utf8';
ALTER ROLE rohitgogi SET default_transaction_isolation TO 'read committed';
ALTER ROLE rohitgogi SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE rohitgogi TO rohitgogi;
```

### 6. **Apply Migrations**

Run the following commands to set up the database:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. **Create a Superuser**

To access the Django admin panel, create a superuser:

```bash
python manage.py createsuperuser
```

Follow the prompts to set up your admin credentials.

### 8. **Collect Static Files**

Before running the server, collect the static files:

```bash
python manage.py collectstatic
```

### 9. **Run the Development Server**

Start the server with:

```bash
python manage.py runserver
```

Open your web browser and go to:

```
http://127.0.0.1:8000/
```

### 10. **Spotify Integration**

Click "Connect to Spotify" on the home page to authenticate your Spotify account and view your listening statistics.

## 🛠 Troubleshooting

- **Issue:** `django.core.exceptions.ImproperlyConfigured: You're using the staticfiles app without having set the STATIC_ROOT setting to a filesystem path.`
  - **Solution:** Make sure you have added `STATIC_ROOT` in your `settings.py`:
    ```python
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    ```

- **Issue:** `psycopg2.errors.OperationalError: FATAL: role "rohitgogi" does not exist`
  - **Solution:** Ensure the PostgreSQL user and database are created as detailed in Step 5.

## 📄 Additional Notes

- All static files are ignored in version control as specified in the `.gitignore` file.
- The database username and password are standardized for consistency across development environments.
