import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import components.authenticate as authenticate

st.set_page_config(
    page_title="Professional Experience", 
    page_icon="🆑", 
    # layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Report a bug': "mailto:gabriel.vapp@gmail.com",
        'About': "# Go and get that Job!"
    }
    )

# Use your MongoDB Atlas connection string here
mongo_uri = st.secrets["mongo_uri"]

# Create a MongoClient using the provided URI
client = MongoClient(mongo_uri)

# Specify the database and collection
db = client["job"]
collection = db["profile"]

def experience_form(email):
    # Streamlit app
    st.title("Add your Working Experience")
    with st.form('profesional_experience'):
        col1, col2 = st.columns(2)

        with col1:
            position_name = st.text_input("Position Name")
            employer = st.text_input("Employer")
        with col2:
            start_date = st.date_input("Start Date", value=None, min_value=None, max_value=None, format="DD/MM/YYYY")
            end_date = st.date_input("End Date", value=None, min_value=None, max_value=None, format="DD/MM/YYYY")
        duties = st.text_area("Duties and Achievements")

        if st.form_submit_button("Add Profesional Experience"):
            try:
                experience_item = {
                    "position_name": position_name,
                    "start_date": datetime.combine(start_date, datetime.min.time()),  # Convert to datetime
                    "end_date": datetime.combine(end_date, datetime.min.time()),
                    "employer": employer,
                    "duties": duties,
                }
                
                # Find the entry with both username and email and append experience_item to experience array
                collection.update_one(
                    {"email": email},
                    {"$push": {"experience": experience_item}}
                )
                
                st.success("Professional experience saved")

            except Exception as e:
                st.error(f"An error occurred: {e}")

def show_experience(email):
    st.header("Working Experience")
    perfil = collection.find_one({"email": email})
    if perfil:
        # st.text(perfil)
        experience_db = perfil.get("experience")
        name_db = perfil.get("name")
        first_name = name_db.split()[0]
        for i in experience_db:
            start_date_str = i['start_date'].strftime("%B %Y") if isinstance(i['start_date'], datetime) else ""
            end_date_str = i['end_date'].strftime("%B %Y") if isinstance(i['end_date'], datetime) else ""
            
            # Use columns to layout experience and delete button
            col1, col2 = st.columns([0.9, 0.1])  # Adjust these values as needed to align the button and text properly
            
            with col1:
                # Display the experience
                st.write(i['position_name'] + ' / ' + i['employer'] + ' / ' + start_date_str + ' - ' + end_date_str)
                st.divider()
            with col2:
                # Construct a unique key for the button based on the experience details
                button_key = f"delete_{i['position_name']}_{i['employer']}_{start_date_str}_{end_date_str}"
                # Display the delete button next to the experience with the unique key
                if st.button("❌", key=button_key):
                    delete_experience(email, i)
                    # Refresh the page to see the updated list
                    st.rerun()
        with st.sidebar:
            st.write(f'Ahoj, {first_name}!')

    else:
        st.info(f"No data saved for {email}.")

def delete_experience(email, experience_item):
    """
    Remove the specified experience from the database.
    """
    try:
        collection.update_one(
            {"email": email},
            {"$pull": {"experience": experience_item}}
        )
        st.success("deleted!")
    except Exception as e:
        st.error(f"An error occurred: {e}")

if st.session_state["authenticated"]:
    email = st.session_state['email_user']
    experience_form(email)
    show_experience(email)
    authenticate.button_logout()
else:
    st.write("# Add Professional Experience")
    st.markdown(
        """
        Streamline your job application process with AI-powered cover letters tailored to your profile and desired role.
    """
    )
    st.markdown('Please Log In')
    authenticate.button_login()