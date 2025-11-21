import streamlit as st
import pandas as pd
from sqlalchemy import text
from shared import engine, load_data, run_query, fetch



def call_procedure(proc_name, params=None):
    with engine.begin() as conn:
        if params:
            placeholders = ", ".join([f":{p}" for p in params.keys()])
            q = text(f"CALL {proc_name}({placeholders})")
            result = conn.execute(q, params)
        else:
            q = text(f"CALL {proc_name}()")
            result = conn.execute(q)

        try:
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            return df
        except:
            return pd.DataFrame()


def call_function(func_name, params=None):
    with engine.begin() as conn:
        if params:
            placeholders = ", ".join([f":{p}" for p in params.keys()])
            q = text(f"SELECT {func_name}({placeholders}) AS result")
            r = conn.execute(q, params)
        else:
            q = text(f"SELECT {func_name}() AS result")
            r = conn.execute(q)

        row = r.fetchone()
        return row[0] if row else None


def page_database_tools_user():
    st.header("🧰 Database Tools (User Portal)")

    tool = st.selectbox(
        "Select Tool",
        [
            "List Tables",
            "View Table Data",
            "Run Procedure",
            "Run Function",
            "Show Triggers",
            "Show Procedures",
            "Show Functions",
            "Run Raw SQL"
        ],
        key="user_db_tool_selector"
    )

    # ----------------------------------------------------------------
    # LIST TABLES
    # ----------------------------------------------------------------
    if tool == "List Tables":
        df = pd.read_sql("SHOW TABLES;", engine)
        st.dataframe(df)

    # ----------------------------------------------------------------
    # VIEW TABLE
    # ----------------------------------------------------------------
    elif tool == "View Table Data":
        tlist = pd.read_sql("SHOW TABLES;", engine)
        tables = [t[0] for t in tlist.values.tolist()]

        tname = st.selectbox("Select table", tables)

        if st.button("Load"):
            df = pd.read_sql(f"SELECT * FROM {tname}", engine)
            st.dataframe(df)

    # ----------------------------------------------------------------
    # RUN PROCEDURES
    # ----------------------------------------------------------------
    elif tool == "Run Procedure":
        st.subheader("📦 Execute Stored Procedure")

        proc = st.selectbox(
            "Choose procedure",
            ["GetMealPlanSummary", "AddFeedback", "UpdateUserWeight"],
            key="user_proc_select"
        )

        if proc == "GetMealPlanSummary":
            uid = st.number_input("User ID", min_value=1)
            if st.button("Run"):
                df = call_procedure("GetMealPlanSummary", {"userId": uid})
                st.dataframe(df)

        elif proc == "AddFeedback":
            uid = st.number_input("User ID", min_value=1)
            rid = st.number_input("Recipe ID", min_value=1)
            rating = st.slider("Rating", 1, 5)
            comments = st.text_area("Comments")

            if st.button("Submit"):
                call_procedure("AddFeedback", {
                    "p_userId": uid,
                    "p_recipeId": rid,
                    "p_rating": rating,
                    "p_comments": comments
                })
                st.success("Feedback submitted!")

        elif proc == "UpdateUserWeight":
            uid = st.number_input("User ID", min_value=1)
            new_w = st.number_input("New Weight (kg)", min_value=1.0)

            if st.button("Update"):
                call_procedure("UpdateUserWeight", {
                    "p_userId": uid,
                    "p_newWeight": new_w
                })
                st.success("Weight updated (trigger recalculated BMI).")

    # ----------------------------------------------------------------
    # RUN FUNCTIONS
    # ----------------------------------------------------------------
    elif tool == "Run Function":
        st.subheader("🧮 Execute SQL Function")

        func = st.selectbox(
            "Choose function",
            ["CalculateBMI", "GetRecipeCalories"]
        )

        if func == "CalculateBMI":
            h = st.number_input("Height (cm)", min_value=50)
            w = st.number_input("Weight (kg)", min_value=1.0)

            if st.button("Compute BMI"):
                result = call_function("CalculateBMI", {
                    "height_cm": h,
                    "weight_kg": w
                })
                st.success(f"BMI = {result}")

        elif func == "GetRecipeCalories":
            rid = st.number_input("Recipe ID", min_value=1)

            if st.button("Compute Calories"):
                result = call_function("GetRecipeCalories", {
                    "recipeId": rid
                })
                st.success(f"Total Calories = {result} kcal")

    # ----------------------------------------------------------------
    # SHOW TRIGGERS
    # ----------------------------------------------------------------
    elif tool == "Show Triggers":
        df = pd.read_sql("SHOW TRIGGERS;", engine)
        st.dataframe(df)

    # ----------------------------------------------------------------
    # SHOW PROCEDURES
    # ----------------------------------------------------------------
    elif tool == "Show Procedures":
        df = pd.read_sql("SHOW PROCEDURE STATUS WHERE Db = DATABASE();", engine)
        st.dataframe(df)

    # ----------------------------------------------------------------
    # SHOW FUNCTIONS
    # ----------------------------------------------------------------
    elif tool == "Show Functions":
        df = pd.read_sql("SHOW FUNCTION STATUS WHERE Db = DATABASE();", engine)
        st.dataframe(df)

    # ----------------------------------------------------------------
    # RAW SQL
    # ----------------------------------------------------------------
    elif tool == "Run Raw SQL":
        q = st.text_area("Enter SQL")

        if st.button("Execute"):
            try:
                df = pd.read_sql(q, engine)
                st.dataframe(df)
            except Exception as e:
                st.error(str(e))



# ------------------------------------
# Streamlit Page Config
# ------------------------------------
st.set_page_config(page_title="User Portal", layout="wide")
st.title("🍽 Nutrition Management – User Portal")

# ------------------------------------
# Session State Setup
# ------------------------------------
if "user_logged_in" not in st.session_state:
    st.session_state.user_logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

# ------------------------------------
# LOGIN / REGISTER (if not logged in)
# ------------------------------------
if not st.session_state.user_logged_in:
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    # ---------------------- LOGIN TAB ----------------------
    with tab1:
        st.subheader("User Login")

        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", key="login_button"):
            df = load_data("User")
            user = df[
                (df["Email"] == login_email) &
                (df["Password"] == login_password)
            ]

            if not user.empty:
                st.session_state.user_logged_in = True
                st.session_state.user_id = int(user.iloc[0]["User_ID"])
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid email or password.")

    # ---------------------- REGISTER TAB ----------------------
    with tab2:
        st.subheader("Create Account")

        reg_name = st.text_input("Full Name", key="register_name")
        reg_email = st.text_input("Email (new)", key="register_email")
        reg_pass = st.text_input("Password", type="password", key="register_password")

        if st.button("Register", key="register_button"):
            if reg_name and reg_email and reg_pass:
                run_query("""
                    INSERT INTO User (Name, Email, Password)
                    VALUES (:n, :e, :p)
                """, {"n": reg_name, "e": reg_email, "p": reg_pass})

                st.success("Account created! Please log in.")
            else:
                st.error("All fields are required.")

    st.stop()

# ------------------------------------
# LOGOUT BUTTON
# ------------------------------------
if st.sidebar.button("🚪 Logout", key="logout_button"):
    st.session_state.user_logged_in = False
    st.session_state.user_id = None
    st.rerun()

# ------------------------------------
# USER MENU
# ------------------------------------
st.sidebar.header("User Menu")
section = st.sidebar.selectbox(
    "Choose Section",
    [
        "Profile",
        "My Meal Plan",
        "Browse Recipes",
        "Weight History",
        "Diet Log",          # ⭐ NEW
        "Give Feedback",
        "Database Tools"
    ],
    key="section_selector"
)


# ===============================================================
#                   1. PROFILE PAGE
# ===============================================================
def page_profile():
    st.header("👤 My Profile")

    df = load_data("User")
    user = df[df["User_ID"] == st.session_state.user_id]

    if user.empty:
        st.error("User not found.")
        return

    st.dataframe(user)

    st.write("---")
    st.subheader("✏️ Edit Profile")

    # SAFE VALUE HANDLING
    raw_height = user.iloc[0].get("Height_cm")
    raw_weight = user.iloc[0].get("Weight_kg")

    # Height
    try:
        current_height = int(raw_height) if pd.notna(raw_height) else 50
        current_height = max(50, min(250, current_height))
    except:
        current_height = 50

    # Weight
    try:
        current_weight = float(raw_weight) if pd.notna(raw_weight) else 20.0
        current_weight = max(20.0, min(300.0, current_weight))
    except:
        current_weight = 20.0

    with st.form("profile_edit_form"):
        new_name = st.text_input("Name", user.iloc[0]["Name"], key="edit_name")
        new_height = st.number_input("Height (cm)", 50, 250, current_height, key="edit_height")
        new_weight = st.number_input("Weight (kg)", 20.0, 300.0, current_weight, key="edit_weight")

        submitted = st.form_submit_button("Save Changes")
        if submitted:
            bmi = round(new_weight / ((new_height / 100) ** 2), 2)

            run_query("""
                UPDATE User
                SET Name = :n, Height_cm = :h, Weight_kg = :w, BMI = :b
                WHERE User_ID = :uid
            """, {
                "n": new_name,
                "h": new_height,
                "w": new_weight,
                "b": bmi,
                "uid": st.session_state.user_id
            })

            st.success("Profile updated!")
            st.rerun()

# ===============================================================
#                   2. MY MEAL PLAN PAGE
# ===============================================================
def page_my_mealplan():
    st.header("🥗 My Meal Plan")

    user_id = st.session_state.user_id

    # Load user's meal plan
    mealplans = fetch("""
        SELECT * FROM Meal_Plan
        WHERE User_ID = :u
    """, {"u": user_id})

    # --------------------------------------------------------------
    # IF USER HAS NO MEAL PLAN → SHOW CREATE BUTTON
    # --------------------------------------------------------------
    if mealplans.empty:
        st.info("You do not have a meal plan yet.")

        if st.button("➕ Create Meal Plan", key="create_mealplan_button"):
            run_query("""
                INSERT INTO Meal_Plan (User_ID, Plan_Name, Start_Date, End_Date, Notes)
                VALUES (:u, 'My Meal Plan', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 7 DAY), 'Auto-created')
            """, {"u": user_id})

            st.success("Meal plan created!")
            st.rerun()

        return  # stop here — add UI only after creating a plan

    # --------------------------------------------------------------
    # USER HAS A MEAL PLAN → SHOW IT
    # --------------------------------------------------------------
    st.subheader("📘 My Meal Plan")
    st.dataframe(mealplans)

    mp_id = int(mealplans.iloc[0]["MealPlan_ID"])

    # --------------------------------------------------------------
    # SHOW RECIPES IN THE PLAN
    # --------------------------------------------------------------
    items = fetch("""
        SELECT
            mpr.MPR_ID,
            mpr.Recipe_ID,
            mpr.Meal_Type,
            mpr.Day_Of_Week,
            r.Recipe_Name,
            r.Cuisine_Type,
            GetRecipeCalories(r.Recipe_ID) AS Calories
        FROM MealPlan_Recipes mpr
        JOIN Recipe r ON r.Recipe_ID = mpr.Recipe_ID
        WHERE mpr.MealPlan_ID = :mp
        ORDER BY 
            FIELD(mpr.Day_Of_Week, 'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'),
            mpr.MPR_ID
    """, {"mp": mp_id})

    st.subheader("🍽 Meals in Your Plan")
    st.dataframe(items)

    st.write("---")

    # --------------------------------------------------------------
    # ADD RECIPE TO MEAL PLAN
    # --------------------------------------------------------------
    st.subheader("➕ Add Recipe to Meal Plan")

    recipes = fetch("SELECT Recipe_ID, Recipe_Name FROM Recipe")

    if recipes.empty:
        st.warning("No recipes available to add.")
        return

    recipe_options = {
        f"{row['Recipe_Name']} (ID {row['Recipe_ID']})": row["Recipe_ID"]
        for _, row in recipes.iterrows()
    }

    selected = st.selectbox("Select Recipe", list(recipe_options.keys()), key="add_recipe_select")
    sel_recipe_id = recipe_options[selected]

    meal_type = st.selectbox(
        "Meal Type",
        ["Breakfast", "Lunch", "Dinner", "Snack"],
        key="add_recipe_meal_type"
    )

    day = st.selectbox(
        "Day of Week",
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        key="add_recipe_day"
    )

    if st.button("Add to Meal Plan", key="add_recipe_btn"):
        run_query("""
            INSERT INTO MealPlan_Recipes (MealPlan_ID, Recipe_ID, Meal_Type, Day_Of_Week)
            VALUES (:mp, :rid, :mt, :d)
        """, {
            "mp": mp_id,
            "rid": sel_recipe_id,
            "mt": meal_type,
            "d": day
        })

        st.success(f"Added recipe to your {day} {meal_type}!")
        st.rerun()




# ===============================================================
#                   3. BROWSE RECIPES
# ===============================================================
def page_browse_recipes():
    st.header("🍳 Browse Recipes")

    df = fetch("""
        SELECT r.*, GetRecipeCalories(r.Recipe_ID) AS Calories
        FROM Recipe r
    """)

    st.dataframe(df)

# ===============================================================
#                   4. WEIGHT HISTORY
# ===============================================================
def page_weight_history():
    st.header("⚖ Weight History")

    user_id = st.session_state.user_id

    # ---------------------------------------------------
    # LOAD WEIGHT HISTORY
    # ---------------------------------------------------
    history = fetch("""
        SELECT *
        FROM User_Weight_History
        WHERE User_ID = :u
        ORDER BY Updated_At ASC
    """, {"u": user_id})

    st.subheader("📘 History Records")
    st.dataframe(history)

    # ---------------------------------------------------
    # WEIGHT PROGRESS GRAPH
    # ---------------------------------------------------
    st.subheader("📈 Weight Progress Graph")

    if not history.empty:
        # Create dataframe for plotting
        graph_df = history[["Updated_At", "New_Weight"]].copy()
        graph_df.rename(columns={"New_Weight": "Weight (kg)"}, inplace=True)

        st.line_chart(graph_df.set_index("Updated_At"))
    else:
        st.info("No weight history yet. Update weight to see graph.")

    st.write("---")

    # ---------------------------------------------------
    # LOAD CURRENT WEIGHT SAFELY
    # ---------------------------------------------------
    user_df = fetch("SELECT Weight_kg FROM User WHERE User_ID = :u", {"u": user_id})
    raw_weight = user_df.iloc[0]["Weight_kg"] if not user_df.empty else None
    current_weight = float(raw_weight) if raw_weight not in (None, "", "NULL") else 50.0

    # ---------------------------------------------------
    # UPDATE WEIGHT FORM
    # ---------------------------------------------------
    st.subheader("➕ Update My Weight")

    new_weight = st.number_input(
        "Enter New Weight (kg)",
        min_value=20.0,
        max_value=300.0,
        value=current_weight,
        step=0.1,
        key="update_weight_input"
    )

    if st.button("Update Weight", key="update_weight_button"):
        run_query("""
            CALL UpdateUserWeight(:uid, :nw)
        """, {
            "uid": user_id,
            "nw": new_weight
        })

        st.success("Weight updated! History entry created.")
        st.rerun()


# ===============================================================
#                   5. DIET LOG PAGE
# ===============================================================
def page_diet_log():
    st.header("🍽 Diet Log")

    user_id = st.session_state.user_id

    # Load logs
    logs = fetch("""
        SELECT 
            l.Log_ID,
            l.Date,
            l.Time,
            r.Recipe_Name,
            l.Portion_Size,
            l.Notes,
            l.is_finished
        FROM User_Diet_Log l
        LEFT JOIN Recipe r ON r.Recipe_ID = l.Recipe_ID
        WHERE l.User_ID = :uid
        ORDER BY l.Date DESC, l.Time DESC
    """, {"uid": user_id})

    st.subheader("📘 Log Entries")
    st.dataframe(logs)

    st.write("---")
    st.subheader("➕ Add Entry")

    recipes = fetch("SELECT Recipe_ID, Recipe_Name FROM Recipe")
    recipe_options = {
        f"{row['Recipe_Name']} (ID {row['Recipe_ID']})": row["Recipe_ID"]
        for _, row in recipes.iterrows()
    }

    sel = st.selectbox("Recipe", list(recipe_options.keys()))
    recipe_id = recipe_options[sel]

    portion = st.number_input("Portion Size", 0.5, 10.0, 1.0, 0.5)
    date = st.date_input("Date")
    time = st.time_input("Time")
    notes = st.text_area("Notes")

    if st.button("Add Log"):
        run_query("""
            INSERT INTO User_Diet_Log (User_ID, Recipe_ID, Date, Time, Portion_Size, Notes)
            VALUES (:uid, :rid, :d, :t, :p, :n)
        """, {
            "uid": user_id,
            "rid": recipe_id,
            "d": date,
            "t": time,
            "p": portion,
            "n": notes
        })
        st.success("Log added!")
        st.rerun()

    st.write("---")
    st.subheader("✔ Mark as Finished")

    if not logs.empty:
        sel_id = st.selectbox("Select Log ID", logs["Log_ID"])
        if st.button("Mark Finished"):
            run_query("UPDATE User_Diet_Log SET is_finished = TRUE WHERE Log_ID = :id", {"id": sel_id})
            st.success("Marked!")
            st.rerun()

    st.write("---")
    st.subheader("🗑 Delete Entry")

    if not logs.empty:
        del_id = st.selectbox("Delete Log ID", logs["Log_ID"])
        if st.button("Delete Log"):
            run_query("DELETE FROM User_Diet_Log WHERE Log_ID = :id", {"id": del_id})
            st.success("Deleted!")
            st.rerun()




# ===============================================================
#                   5. FEEDBACK PAGE
# ===============================================================
def page_feedback():
    st.header("⭐ Give Feedback")

    recipes = load_data("Recipe")
    recipe_options = {
        f"{row['Recipe_Name']} (ID: {row['Recipe_ID']})": row["Recipe_ID"]
        for _, row in recipes.iterrows()
    }

    selected = st.selectbox("Choose Recipe", list(recipe_options.keys()), key="feedback_recipe_selector")
    recipe_id = recipe_options[selected]

    rating = st.slider("Rating", 1, 5, 3, key="feedback_rating")
    comment = st.text_area("Comment", key="feedback_comment")

    if st.button("Submit Feedback", key="feedback_submit"):
        run_query("""
            INSERT INTO Feedback (User_ID, Recipe_ID, Rating, Comments)
            VALUES (:u, :r, :rat, :c)
        """, {
            "u": st.session_state.user_id,
            "r": recipe_id,
            "rat": rating,
            "c": comment
        })

        st.success("Feedback submitted!")

def page_database_tools_user():
    st.header("🧰 Database Tools / Procedures / Functions")

    tool = st.selectbox(
        "Select Tool",
        [
            "List Tables",
            "View Table Data",
            "Show Triggers",
            "Show Functions",
            "Show Procedures",
            "Run Custom SQL"
        ],
        key="db_tool_selector_user"
    )

    # --------------------------------------------------------
    # LIST TABLES
    # --------------------------------------------------------
    if tool == "List Tables":
        tables = fetch("SHOW TABLES")
        st.dataframe(tables)

    # --------------------------------------------------------
    # VIEW TABLE CONTENT
    # --------------------------------------------------------
    elif tool == "View Table Data":
        tables = fetch("SHOW TABLES")
        table_list = [t[0] for t in tables.values.tolist()]

        tname = st.selectbox("Select Table", table_list, key="db_user_table_name")

        if st.button("Load Data", key="db_user_load"):
            data = fetch(f"SELECT * FROM {tname}")
            st.dataframe(data)

    # --------------------------------------------------------
    # SHOW TRIGGERS
    # --------------------------------------------------------
    elif tool == "Show Triggers":
        st.subheader("🔧 Triggers")
        trig = fetch("SHOW TRIGGERS")
        st.dataframe(trig)

    # --------------------------------------------------------
    # SHOW FUNCTIONS
    # --------------------------------------------------------
    elif tool == "Show Functions":
        st.subheader("🧮 SQL Functions")
        funcs = fetch("SHOW FUNCTION STATUS WHERE Db = DATABASE()")
        st.dataframe(funcs)

    # --------------------------------------------------------
    # SHOW PROCEDURES
    # --------------------------------------------------------
    elif tool == "Show Procedures":
        st.subheader("📦 Stored Procedures")
        procs = fetch("SHOW PROCEDURE STATUS WHERE Db = DATABASE()")
        st.dataframe(procs)

    # --------------------------------------------------------
    # RUN CUSTOM SQL
    # --------------------------------------------------------
    elif tool == "Run Custom SQL":
        st.subheader("📝 Run SQL Query")
        q = st.text_area("Write SQL", height=200, key="db_user_sql")

        if st.button("Execute", key="db_user_exec"):
            try:
                result = fetch(q)
                st.dataframe(result)
            except Exception as e:
                st.error(str(e))


# -------------------------------------------------------
# ROUTE TO SELECTED PAGE
# -------------------------------------------------------
if section == "Profile":
    page_profile()

elif section == "My Meal Plan":
    page_my_mealplan()

elif section == "Browse Recipes":
    page_browse_recipes()

elif section == "Weight History":
    page_weight_history()

elif section == "Diet Log":
    page_diet_log()


elif section == "Give Feedback":
    page_feedback()

elif section == "Database Tools":
    page_database_tools_user()
