import streamlit as st

st.set_page_config(page_title="Nutrition Management", layout="wide")

st.title("🍽 Nutrition Management System")
st.subheader("Welcome! Please choose your portal:")

# Buttons for navigation
col1, col2 = st.columns(2)

with col1:
    if st.button("👤 User Portal"):
        st.switch_page("pages/user.py")

with col2:
    if st.button("🛠 Admin Portal"):
        st.switch_page("pages/admin.py")

st.markdown("---")
st.caption("Built for Nutrition Management & Meal Tracking")
