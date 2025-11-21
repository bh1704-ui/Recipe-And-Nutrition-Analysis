🍽️ Recipe & Nutrition Analysis System

A Complete Nutrition Management Platform using Streamlit + MySQL

📌 Overview

The Recipe & Nutrition Analysis System is a full-stack application designed to help users track their diet, explore recipes, manage meal plans, analyze nutrition, and maintain personal health metrics.
It includes a User Portal, an Admin Dashboard, and a fully normalized MySQL database with triggers, functions, and stored procedures.

The project demonstrates solid DBMS concepts:
✔ ER modeling
✔ Relational schema design
✔ SQL functions & triggers
✔ Stored procedures
✔ CRUD operations
✔ Data integrity & constraints

🚀 Features
👤 User Features

Register / Login

View & update profile

Auto-BMI calculation

Weight history tracking with graphs

Browse all recipes

View total recipe calories (via SQL function)

Maintain weekly meal plan

Diet log (with finished marker & deletion)

Submit feedback for recipes

Database viewer for tables, triggers, functions

🧑‍💼 Admin Features

Manage Users

Add / Edit / Delete Recipes

Manage Ingredients & Nutrition data

Manage Recipe–Ingredient mapping

Manage Meal Plans

Delete recipes safely (removes logs, feedback, diet logs, mapping tables)

Full database inspection:

Triggers

Stored Procedures

SQL Functions

Custom SQL execution

🗄️ Database Highlights

The project uses MySQL with the following key features:

✔ Normalized Tables

User

Recipe

Ingredient

Nutrition

Recipe_Ingredient

Meal_Plan

MealPlan_Recipes

User_Diet_Log

Feedback

User_Weight_History

Recipe_Log

✔ SQL Functions

CalculateBMI()

GetRecipeCalories()

✔ Stored Procedures

GetMealPlanSummary()

AddFeedback()

UpdateUserWeight()

✔ Triggers

Auto-update BMI on profile update

Auto-log recipe creation events

📁 Project Structure
Recipe-And-Nutrition-Analysis/
│
├── pages/
│   ├── admin.py                   # Admin dashboard
│   ├── user.py                    # User dashboard
│
├── home.py                        # Main Streamlit entry page
├── init_admin.py                  # Initialize admin account
├── shared.py                      # Database connection + helper functions
├── fix_passwords.py               # Utility script to sanitize passwords
│
├── mysql/
│   └── dbms_miniproject_Final.sql # Full MySQL schema + sample data
│
├── requirements.txt               # Python dependencies
├── .gitignore
└── README.md


⚙️ Installation & Setup
1️⃣ Clone the repository
git clone https://github.com/bh1704-ui/Recipe-And-Nutrition-Analysis.git
cd Recipe-And-Nutrition-Analysis

2️⃣ Create and activate virtual environment
python -m venv .venv
.venv/Scripts/activate      # on Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Import MySQL database
mysql -u root -p < mysql/dbms_miniproject_Final.sql

5️⃣ Update database credentials

Modify shared.py:

engine = create_engine(
    "mysql+pymysql://username:password@localhost/NutritionDB"
)

6️⃣ Run the application
streamlit run home.py
