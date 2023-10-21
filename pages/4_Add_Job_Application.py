import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import uuid
import components.authenticate as authenticate

st.set_page_config(
    page_title="Add Job Application", 
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

def job_application_form(email):
    st.title('Add Job Application Info')
    with st.form("hey"):
        col1, col2 = st.columns(2)
        with col1:
            job_position = st.text_input("Job position", key="input1", placeholder="Enter the name of the job position",)
            company_name = st.text_input("Company Name", value=None, key="input2", placeholder="Enter the company name",)
            job_reference = st.text_input("Job Reference", value=None, key="input5", placeholder="Enter the job reference number",)
            closing_date = st.date_input("Closing Date", value=None, key="input6", format="DD/MM/YYYY",)

        with col2:
            city_job = st.text_input("City", value=None, key="input4", placeholder="Enter the city where the job will be",)
            country_job = st.text_input("Country", value=None, placeholder="Enter the country where the job will be",)
            salary = st.number_input("Salary in pounds", value=None, key="input3", placeholder="Enter the salary for this position",)
            

        link = st.text_input("link", value=None, key="input10", placeholder="Enter the linkof the job descrition",)
        about_company = st.text_area("Info about company", value=None, key="input7", placeholder="Enter information about company",)
        about_role = st.text_area("Info about role", value=None, key="input8", placeholder="Enter information about new role",)
        experience_success = st.text_area("Experience needed / keys to success", value=None, key="input9", placeholder="Enter Experience needed / keys to success",)
        
        if st.form_submit_button("Submit"):
            try:
                job_application_item = {
                    "job_application_id": str(uuid.uuid4()),
                    "job_position": job_position,
                    "company_name": company_name,
                    "city_job": city_job,
                    "country_job": country_job,
                    "salary": salary,
                    "job_reference": job_reference,
                    "closing_date": datetime.combine(closing_date, datetime.min.time()),  # Convert to datetime
                    "creation_date": datetime.now(),
                    "link": link,
                    "about_company": about_company,
                    "about_role": about_role,
                    "experience_success": experience_success,
                    "cover letter": None
                }
                
                # Find the entry with both username and email and append academic_item to education array
                collection.update_one(
                    {"email": email},
                    {"$push": {"job_applications": job_application_item}}
                )
                
                st.success("Job Application data saved")

            except Exception as e:
                st.error(f"An error occurred: {e}")
    perfil = collection.find_one({"email": email})
    if perfil:
        name_db = perfil.get("name")
        first_name = name_db.split()[0]
        with st.sidebar:
            st.write(f'Ahoj, {first_name}!')


if st.session_state["authenticated"]:
    email = st.session_state['email_user']
    job_application_form(email)
    authenticate.button_logout()
else:
    st.write("# Add Job Application")
    st.markdown(
        """
        Streamline your job application process with AI-powered cover letters tailored to your profile and desired role.
    """
    )
    st.markdown('Please Log In')
    authenticate.button_login()