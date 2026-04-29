#  Matrimony Web Application

This is a Django-based matrimonial web application built to help people find suitable life partners in a simple and structured way.

The idea behind this project was to create a platform where users can create profiles, explore matches, and connect — all in one place with a clean UI and smooth experience.

🌐 Live site: https://srivarammanamalai.com/

---

##  What this project does

* Users can register and create their profiles
* Browse and search for other profiles
* Filter matches based on preferences
* Basic matchmaking flow
* Payment option for premium features
* Fully responsive design (works on mobile too)

---

##  Built with

I kept the stack simple and practical:

* **Backend:** Python + Django
* **Frontend:** HTML, CSS, Bootstrap, JavaScript
* **Database:** SQLite (can be switched to MySQL)
* **Other:** Django REST API (for handling data)

---

##  Project structure (simplified)

```
APPSOURCE/
│── mck_website/        # Main website logic
│── mck_auth/           # Login / registration
│── mck_admin_console/  # Admin side
│── mck_master/         # Core data handling
│
│── static/             # CSS, JS
│── media/              # Uploaded files
│── img/                # Screenshots
│
│── manage.py
│── requirements.txt
```

## 📸 Screenshots

### 🏠 Home Page

![Home Page](img/home%20page.png)

### 👤 Profile Page

![Profile Page](img/profile%20page.png)

### 💳 Payment Page

![Payment Page](img/payment.png)---

##  Screens

* Home page
* Profile page
* Payment page

(Screenshots are available in the `img/` folder)

---

##  Running locally

Clone the project:

```bash
git clone https://github.com/your-username/matrimony-site.git
cd matrimony-site
```

Create virtual environment:

```bash
python -m venv env
env\Scripts\activate   # Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations and start server:

```bash
python manage.py migrate
python manage.py runserver
```

Open:

```
http://127.0.0.1:8000/
```

---

## Note on security

I’ve removed some sensitive files like:

* Actual `settings.py` values
* Secret keys
* Database data
* Media uploads

If you want to run this project, you’ll need to:

* Create your own `.env` file
* Add your own database config
* Generate a new Django secret key

---

##  Why I built this

This project was mainly built to practice:

* Django full-stack development
* Authentication systems
* Real-world project structure
* Payment integration flow

---

##  License

MIT License

---

If you have suggestions or want to improve something, feel free to open a PR.
