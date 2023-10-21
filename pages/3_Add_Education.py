import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import components.authenticate as authenticate

st.set_page_config(
    page_title="Academic Records", 
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

def education_form(email):
    # Streamlit app
    st.title("Add your Academic History")
    with st.form('academic', clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            academic_title = st.text_input("Academic Title Achieved")
            school = st.text_input("Academic Institution")
            grade = st.number_input("Grade Average")
        with col2:
            start_date = st.date_input("Start Date", value=None, format="DD/MM/YYYY")
            end_date = st.date_input("End Date", value=None, format="DD/MM/YYYY")

        if st.form_submit_button("Add Academic Record"):
            try:
                academic_item = {
                    "academic_title": academic_title,
                    "start_date": datetime.combine(start_date, datetime.min.time()),  # Convert to datetime
                    "end_date": datetime.combine(end_date, datetime.min.time()),
                    "school": school,
                    "grade": grade,
                }
                
                # Find the entry with both username and email and append academic_item to education array
                collection.update_one(
                    {"email": email},
                    {"$push": {"education": academic_item}}
                )
                
                st.success("Academic Record saved")

            except Exception as e:
                st.error(f"An error occurred: {e}")

def show_education(email):
    st.header("Academic Record")
    perfil = collection.find_one({"email": email})
    if perfil:
        academic_db = perfil.get("education", [])
        name_db = perfil.get("name")
        first_name = name_db.split()[0]
        # Sort the academic records based on end_date in descending order (most recent first)
        sorted_academic_db = sorted(academic_db, key=lambda x: x.get('end_date', datetime.min), reverse=True)
        
        for i in sorted_academic_db:
            start_date_str = i['start_date'].strftime("%B %Y") if isinstance(i['start_date'], datetime) else ""
            end_date_str = i['end_date'].strftime("%B %Y") if isinstance(i['end_date'], datetime) else ""
            
            # Use columns to layout academic record and delete button
            col1, col2 = st.columns([0.9, 0.1])  # Adjust these values as needed
            
            with col1:
                # Display the academic record
                st.write(i['academic_title'] + ' / ' + i['school'] + ' / ' + start_date_str + ' - ' + end_date_str)
                st.divider()
            with col2:
                # Construct a unique key for the button based on the academic details
                button_key = f"delete_{i['academic_title']}_{i['school']}_{start_date_str}_{end_date_str}"
                # Display the delete button next to the academic record with the unique key
                if st.button("❌", key=button_key):
                    delete_academic_record(email, i)
                    # Refresh the page to see the updated list
                    st.rerun()
        with st.sidebar:
            st.write(f'Ahoj, {first_name}!')

    else:
        st.info(f"No data saved for {email}.")

def delete_academic_record(email, academic_item):
    """
    Remove the specified academic record from the database.
    """
    try:
        collection.update_one(
            {"email": email},
            {"$pull": {"education": academic_item}}
        )
        st.success("Deleted!")
    except Exception as e:
        st.error(f"An error occurred: {e}")

if st.session_state["authenticated"]:
    email = st.session_state['email_user']
    education_form(email)
    show_education(email)
    authenticate.button_logout()

else:
    st.write("# Add Academic Records")
    st.markdown(
        """
        Streamline your job application process with AI-powered cover letters tailored to your profile and desired role.
    """
    )
    st.markdown('Please Log In')
    authenticate.button_login()