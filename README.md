# 🍲 FlavorShare

**FlavorShare** is a social recipe-sharing web application built using Django.  
It allows users to create, share, explore, and interact with recipes — combining the best of a cooking blog and a social media platform.

---

## 🌟 Features

- 👤 User registration & login
- 📝 Add and edit personal recipes with images, tags, and descriptions
- 🧑‍🍳 Separate registration for restaurant users
- 🧑‍🤝‍🧑 Follow/unfollow users
- ❤️ Like and share recipes
- 💬 Direct messaging between users (with recipe sharing)
- 🔍 Search users and recipes by name or tags (modal-based)
- 📰 Personalized recipe feed
- 📣 Sidebar promotions for restaurant users
- 👨‍💼 Admin dashboard to manage users and approve restaurant registrations
- ⚙️ Session management and cache control for smoother experience

---

## 💡 Technologies Used

- **Backend**: Python, Django
- **Frontend**: HTML, CSS, Bootstrap, JavaScript (AJAX)
- **Database**: SQLite (development)
- **Authentication**: Django's built-in auth
- **Deployment-ready**: Easily portable to PostgreSQL or production servers

---

## 🚀 How to Run Locally

1. **Clone the repository**
   ```bash
   git clone https://github.com/DilshaParvin/flavorshare.git
   cd flavorshare

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate       # For Windows
# source venv/bin/activate  # For macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply database migrations
python manage.py migrate

# 5. (Optional) Create a superuser for admin access
python manage.py createsuperuser

# 6. Run the development server
python manage.py runserver

Then open your browser and go to:
http://127.0.0.1:8000/

