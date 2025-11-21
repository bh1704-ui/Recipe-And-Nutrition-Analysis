import streamlit as st
import pandas as pd
from sqlalchemy import text
from shared import engine, run_query, load_data, fetch


# ============================================================
# DATABASE UTIL FUNCTIONS
# ============================================================

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


# ============================================================
# SAFE USER DELETE (FULL CASCADE)
# ============================================================

def delete_user_completely(user_id):

    run_query("DELETE FROM User_Weight_History WHERE User_ID = :id", {"id": user_id})
    run_query("DELETE FROM User_Diet_Log WHERE User_ID = :id", {"id": user_id})
    run_query("DELETE FROM Feedback WHERE User_ID = :id", {"id": user_id})

    run_query("""
        DELETE FROM MealPlan_Recipes
        WHERE MealPlan_ID IN (SELECT MealPlan_ID FROM Meal_Plan WHERE User_ID = :id)
    """, {"id": user_id})

    run_query("DELETE FROM Meal_Plan WHERE User_ID = :id", {"id": user_id})

    run_query("DELETE FROM Recipe_Log WHERE Created_By = :id", {"id": user_id})
    run_query("DELETE FROM Recipe WHERE Creator_User_ID = :id", {"id": user_id})

    run_query("DELETE FROM User WHERE User_ID = :id", {"id": user_id})

def delete_recipe_completely(recipe_id):
    # Remove from meal plans
    run_query("DELETE FROM MealPlan_Recipes WHERE Recipe_ID = :id", {"id": recipe_id})

    # Remove from diet logs
    run_query("DELETE FROM User_Diet_Log WHERE Recipe_ID = :id", {"id": recipe_id})

    # Remove feedback
    run_query("DELETE FROM Feedback WHERE Recipe_ID = :id", {"id": recipe_id})

    # Remove ingredient links
    run_query("DELETE FROM Recipe_Ingredient WHERE Recipe_ID = :id", {"id": recipe_id})

    # Remove recipe logs
    run_query("DELETE FROM Recipe_Log WHERE Recipe_ID = :id", {"id": recipe_id})

    # Remove the recipe itself
    run_query("DELETE FROM Recipe WHERE Recipe_ID = :id", {"id": recipe_id})

def delete_ingredient_completely(ingredient_id):

    # Remove ingredient links inside recipes
    run_query("DELETE FROM Recipe_Ingredient WHERE Ingredient_ID = :id", {"id": ingredient_id})

    # Remove nutrition info tied to ingredient
    run_query("DELETE FROM Nutrition WHERE Ingredient_ID = :id", {"id": ingredient_id})

    # Finally delete ingredient
    run_query("DELETE FROM Ingredient WHERE Ingredient_ID = :id", {"id": ingredient_id})

# ============================================================
# STREAMLIT ADMIN PORTAL
# ============================================================

st.set_page_config(page_title="Admin Portal", layout="wide")
st.title("🛠 Nutrition Management – Admin Portal")


# ============================================================
# LOGIN SESSION
# ============================================================

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False


if not st.session_state.admin_logged_in:
    st.subheader("🔐 Admin Login")

    login_email = st.text_input("Admin Email", key="admin_login_email")
    login_password = st.text_input("Password", type="password", key="admin_login_password")

    if st.button("Login", key="admin_login_button"):
        df = load_data("User")
        admin = df[
            (df["Email"] == login_email) &
            (df["Password"] == login_password) &
            (df["role"] == "admin")
        ]

        if not admin.empty:
            st.session_state.admin_logged_in = True
            st.success("Admin Login Successful!")
            st.rerun()
        else:
            st.error("Invalid admin credentials.")

    st.stop()


# ============================================================
# SIDEBAR MENU
# ============================================================

if st.sidebar.button("🚪 Logout", key="admin_logout_button"):
    st.session_state.admin_logged_in = False
    st.rerun()

st.sidebar.header("Admin Menu")

sections = [
    "Users",
    "Recipes",
    "Ingredients",
    "Meal Plans",
    "Feedback",
    "Database Tools",
]

section = st.sidebar.selectbox("Select Section", sections, key="admin_section_selector")


# ============================================================
# USERS PAGE
# ============================================================

if section == "Users":
    st.header("👤 Manage Users")

    df = load_data("User")
    st.dataframe(df)

    st.subheader("🗑 Delete User (Full Cascade Delete)")

    if not df.empty:
        delete_uid = st.selectbox(
            "Select User ID to Delete",
            df["User_ID"].tolist(),
            key="delete_user_selector"
        )

        if st.button("Delete User", key="delete_user_button"):
            try:
                delete_user_completely(delete_uid)
                st.success(f"User {delete_uid} deleted successfully with all linked records!")
                st.rerun()
            except Exception as e:
                st.error("❌ Error deleting user.")
                st.code(str(e))

    with st.expander("➕ Add User"):
        new_name = st.text_input("Name", key="add_user_name")
        new_email = st.text_input("Email", key="add_user_email")
        new_pass = st.text_input("Password", key="add_user_password")
        new_role = st.selectbox("Role", ["user", "admin"], key="add_user_role")

        if st.button("Add User", key="add_user_button"):
            run_query(
                "INSERT INTO User (Name, Email, Password, role) VALUES (:n, :e, :p, :r)",
                {"n": new_name, "e": new_email, "p": new_pass, "r": new_role}
            )
            st.success("User added.")
            st.rerun()



# ============================================================
# RECIPES PAGE
# ============================================================

elif section == "Recipes":
    st.header("🍳 Manage Recipes")

    df = load_data("Recipe")
    st.dataframe(df)

    # --------------------------
    # SAFE DELETE FUNCTION
    # --------------------------
    def delete_recipe_completely(recipe_id):
        # Remove from meal plans
        run_query("DELETE FROM MealPlan_Recipes WHERE Recipe_ID = :id", {"id": recipe_id})

        # Remove from diet logs
        run_query("DELETE FROM User_Diet_Log WHERE Recipe_ID = :id", {"id": recipe_id})

        # Remove feedback
        run_query("DELETE FROM Feedback WHERE Recipe_ID = :id", {"id": recipe_id})

        # Remove ingredient links
        run_query("DELETE FROM Recipe_Ingredient WHERE Recipe_ID = :id", {"id": recipe_id})

        # Remove recipe logs
        run_query("DELETE FROM Recipe_Log WHERE Recipe_ID = :id", {"id": recipe_id})

        # Remove the recipe itself
        run_query("DELETE FROM Recipe WHERE Recipe_ID = :id", {"id": recipe_id})

    # --------------------------
    # DELETE RECIPE SECTION
    # --------------------------
    st.subheader("🗑 Delete Recipe")
    if not df.empty:
        rid = st.selectbox("Recipe ID", df["Recipe_ID"], key="delete_recipe_id")
        if st.button("Delete Recipe", key="delete_recipe_button"):
            delete_recipe_completely(rid)
            st.success("Recipe deleted successfully (full cascade)!")
            st.rerun()

    # --------------------------
    # ADD RECIPE SECTION
    # --------------------------
    with st.expander("➕ Add Recipe"):
        rname = st.text_input("Recipe Name", key="new_recipe_name")
        desc = st.text_area("Description", key="new_recipe_desc")
        cuisine = st.text_input("Cuisine Type", key="new_recipe_cuisine")
        prep = st.number_input("Prep Time", 0, 500, key="new_recipe_prep")
        cook = st.number_input("Cook Time", 0, 500, key="new_recipe_cook")
        creator = st.number_input("Creator User ID", 1, key="new_recipe_creator")

        if st.button("Add Recipe", key="add_recipe_button"):
            run_query(
                """
                INSERT INTO Recipe (Recipe_Name, Description, Cuisine_Type,
                Preparation_Time_minutes, Cooking_Time_minutes, Creator_User_ID)
                VALUES (:n, :d, :c, :p, :k, :u)
                """,
                {"n": rname, "d": desc, "c": cuisine, "p": prep, "k": cook, "u": creator}
            )
            st.success("Recipe added.")
            st.rerun()



# ============================================================
# INGREDIENTS PAGE
# ============================================================

elif section == "Ingredients":
    st.header("🧂 Manage Ingredients")

    df = load_data("Ingredient")
    st.dataframe(df)

    st.subheader("🗑 Delete Ingredient")
    if not df.empty:
        del_ing = st.selectbox("Select Ingredient ID", df["Ingredient_ID"].tolist(), key="delete_ingredient_selector")
        if st.button("Delete Ingredient", key="delete_ingredient_button"):
            delete_ingredient_completely(del_ing)
            st.success("Ingredient deleted successfully!")
            st.rerun()

    with st.expander("➕ Add Ingredient"):
        ing_name = st.text_input("Ingredient Name", key="add_ing_name")
        unit = st.text_input("Unit", key="add_ing_unit")
        cat = st.text_input("Category", key="add_ing_category")

        if st.button("Add Ingredient", key="add_ing_button"):
            run_query("""
                INSERT INTO Ingredient (Ingredient_Name, Unit_Of_Measure, Category)
                VALUES (:n, :u, :c)
            """, {"n": ing_name, "u": unit, "c": cat})
            st.success("Ingredient added.")
            st.rerun()


# ============================================================
# MEAL PLANS PAGE
# ============================================================

elif section == "Meal Plans":
    st.header("🥗 Manage Meal Plans")

    df = load_data("Meal_Plan")
    st.dataframe(df)

    with st.expander("➕ Add Meal Plan"):
        uid = st.number_input("User ID", 1, key="new_mp_uid")
        pname = st.text_input("Plan Name", key="new_mp_name")

        if st.button("Add Meal Plan", key="add_mp_button"):
            run_query(
                "INSERT INTO Meal_Plan (User_ID, Plan_Name) VALUES (:u, :p)",
                {"u": uid, "p": pname}
            )
            st.success("Meal plan created.")
            st.rerun()



# ============================================================
# FEEDBACK PAGE
# ============================================================

elif section == "Feedback":
    st.header("⭐ User Feedback")
    df = load_data("Feedback")
    st.dataframe(df)



# ============================================================
# DATABASE TOOLS PAGE
# ============================================================

elif section == "Database Tools":
    st.header("🧰 Database Tools / Procedures / Functions / Triggers")

    tool = st.selectbox(
        "Select Tool",
        [
            "List Tables",
            "View Table Data",
            "Run Procedure",
            "Run Function",
            "Run GetRecipeCalories",
            "Run Trigger Test",
            "Show Triggers",
            "Show Procedures",
            "Show Functions",
            "Run Raw SQL",
        ],
        key="admin_tool_selector"
    )

    # ========== LIST TABLES ==========
    if tool == "List Tables":
        data = fetch("SHOW TABLES")
        st.dataframe(data)

    # ========== VIEW TABLE ==========
    elif tool == "View Table Data":
        tables = fetch("SHOW TABLES")
        table_list = [t[0] for t in tables.values.tolist()]
        t = st.selectbox("Select Table", table_list)
        if st.button("Load Table"):
            st.dataframe(fetch(f"SELECT * FROM {t}"))

    # ========== PROCEDURES ==========
    elif tool == "Run Procedure":
        st.subheader("📦 Execute Stored Procedure")
        proc = st.selectbox("Procedure", ["GetMealPlanSummary", "AddFeedback", "UpdateUserWeight"])

        if proc == "GetMealPlanSummary":
            uid = st.number_input("User ID", min_value=1)
            if st.button("Run"):
                st.dataframe(call_procedure("GetMealPlanSummary", {"userId": uid}))

        elif proc == "AddFeedback":
            uid = st.number_input("User ID", min_value=1)
            rid = st.number_input("Recipe ID", min_value=1)
            rating = st.slider("Rating", 1, 5)
            comment = st.text_area("Comment")
            if st.button("Submit"):
                call_procedure("AddFeedback", {
                    "p_userId": uid,
                    "p_recipeId": rid,
                    "p_rating": rating,
                    "p_comments": comment
                })
                st.success("Feedback added (procedure).")

        elif proc == "UpdateUserWeight":
            uid = st.number_input("User ID", min_value=1)
            w = st.number_input("New Weight", min_value=1.0)
            if st.button("Update"):
                call_procedure("UpdateUserWeight", {"p_userId": uid, "p_newWeight": w})
                st.success("User weight updated!")

    # ========== FUNCTIONS ==========
    elif tool == "Run Function":
        st.subheader("🧮 Run SQL Function")

        func = st.selectbox("Function", ["CalculateBMI"])

        if func == "CalculateBMI":
            h = st.number_input("Height (cm)", min_value=50)
            w = st.number_input("Weight (kg)", min_value=1.0)
            if st.button("Compute BMI"):
                result = call_function("CalculateBMI", {"height_cm": h, "weight_kg": w})
                st.success(f"BMI = {result}")

    # ========== GetRecipeCalories ==========
    elif tool == "Run GetRecipeCalories":
        rid = st.number_input("Recipe ID", min_value=1)
        if st.button("Compute Calories"):
            result = call_function("GetRecipeCalories", {"recipeId": rid})
            st.success(f"Total Calories = {result} kcal")

    # ========== TRIGGER TEST ==========
    elif tool == "Run Trigger Test":
        st.subheader("⚡ Trigger Test")

        trg = st.selectbox("Choose Trigger", ["Test Insert Trigger", "Test BMI Trigger"])

        if trg == "Test Insert Trigger":
            if st.button("Run Insert Trigger"):
                run_query("INSERT INTO Recipe (Recipe_Name) VALUES ('TriggerTest')")
                logs = fetch("SELECT * FROM Recipe_Log ORDER BY Log_ID DESC LIMIT 5")
                st.success("Trigger executed.")
                st.dataframe(logs)

        elif trg == "Test BMI Trigger":
            uid = st.number_input("User ID", min_value=1)
            if st.button("Run BMI Trigger"):
                run_query("UPDATE User SET Weight_kg = Weight_kg + 1 WHERE User_ID = :u", {"u": uid})
                st.success("Trigger executed.")

    # ========== SHOW TRIGGERS ==========
    elif tool == "Show Triggers":
        st.dataframe(fetch("SHOW TRIGGERS"))

    # ========== SHOW PROCEDURES ==========
    elif tool == "Show Procedures":
        st.dataframe(fetch("SHOW PROCEDURE STATUS WHERE Db = DATABASE()"))

    # ========== SHOW FUNCTIONS ==========
    elif tool == "Show Functions":
        st.dataframe(fetch("SHOW FUNCTION STATUS WHERE Db = DATABASE()"))

    # ========== RAW SQL ==========
    elif tool == "Run Raw SQL":
        q = st.text_area("Query")
        if st.button("Run SQL"):
            try:
                st.dataframe(fetch(q))
            except Exception as e:
                st.error(str(e))
