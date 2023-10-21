import streamlit as st
from pymongo import MongoClient
import components.authenticate as authenticate

st.set_page_config(
    page_title="Edit Profile", 
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

def edita_perfil(email):
    # Streamlit app
    st.subheader(f"Edit profile")
    with st.form(key='profile_info'):
        name = st.text_input("Full Name")
        col1, col2, = st.columns(2)
        with col1:
            city = st.text_input("City")
        with col2:
            country = st.text_input("Country")
        relocate = st.checkbox('Willing to relocate')
        summary = st.text_area("Profesional Summary")
        key_facts = st.text_area("Key Facts")

        submitted = st.form_submit_button("Save Profile")
        
        if submitted:
            try:
                perfil_data = {
                    "email": email,
                    "name": name,
                    "city": city,
                    "country": country,
                    "relocate": relocate,
                    "summary": summary,
                    "key_facts": key_facts,
                }
                # Filter for the document to update
                filter_doc = {"email": email}
                 # Use the $set operator to update the desired fields
                update_doc = {"$set": perfil_data}
                # Use upsert=True to insert a new document if no matching document is found
                collection.update_one(filter_doc, update_doc, upsert=True)
                # collection.insert_one(perfil)
                st.success("Profile saved!")
                st.rerun()
            except Exception as e:
                st.error(f"An error occurred: {e}")

# Function to retrieve and display education data
def show_perfil(email):
    st.title("Profile")
    perfil = collection.find_one({"email": email})
    if perfil:
        # st.text(perfil)
        name_db = perfil.get("name")
        first_name = name_db.split()[0]
        email_db = perfil.get("email")
        city_db = perfil.get("city")
        country = perfil.get("country")
        summary_db = perfil.get("summary")
        key_facts_db = perfil.get("key_facts")
        languages_db = perfil.get("languages")
        software_db = perfil.get("software_skills")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'Name: **{name_db}**')
            st.markdown(f'Email: **{email_db}**')
            st.markdown(f'Location: **{city_db}, {country}**')
            if languages_db:
                languages_string = ", ".join([lang["language"] for lang in languages_db if "language" in lang])
                st.markdown(f'Languages: **{languages_string}**')
            if software_db:
                software_string = ", ".join([soft["software"] for soft in software_db if "software" in soft])
                st.markdown(f'Software Skills: **{software_string}**')
        # with col2:
        #     st.image('https://images.unsplash.com/photo-1548407260-da850faa41e3?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1487&q=80',
        #              width=150)
        
        st.markdown(f'Profesional Summary: **{summary_db}**')
        st.markdown(f'Key Facts: **{key_facts_db}**')
        with st.sidebar:
            st.write(f'Ahoj, {first_name}!')
        
        

    else:
        st.info(f"No data saved for {email}.")

def language_form(email):
    # Streamlit app
    st.title("Add your Languages")
    with st.form('language'):
        col1, col2 = st.columns(2)

        with col1:
            language = st.text_input("Language name")
        with col2:
            language_level = st.selectbox("Language Level", 
                                  ('Beginner A1', 'Elementary A2',
                                   'Intermediate B1', 'Upper-Intermediate B2',
                                   'Advanced C1', 'Proeficency / Native C2'),
                                   index=None)

        if st.form_submit_button("Add Language"):
            try:
                language_item = {
                    "language": language,
                    "language_level": language_level,
                }
                
                # Find the entry with both username and email and append academic_item to education array
                collection.update_one(
                    {"email": email},
                    {"$push": {"languages": language_item}}
                )
                
                st.success("Language saved")
                st.rerun()

            except Exception as e:
                st.error(f"An error occurred: {e}")

def software_form(email):
    # Streamlit app
    st.title("Add your Software Skills")
    with st.form('software_skills'):
        col1, col2, col3= st.columns(3)

        with col1:
            software = st.text_input("Software name")
        with col2:
            knowledge_level = st.selectbox("Knowledge Level", 
                                  ('Beginner', 'Intermediate', 'Advanced '),
                                   index=None)
        with col3:
            software_years_experience = st.number_input('Years of experience')

        if st.form_submit_button("Add Software Skill"):
            try:
                software_skill_item = {
                    "software": software,
                    "knowledge_level": knowledge_level,
                    "software_years_experience": software_years_experience,
                }
                
                # Find the entry with both username and email and append academic_item to education array
                collection.update_one(
                    {"email": email},
                    {"$push": {"software_skills": software_skill_item}}
                )
                
                st.success("Software skill saved")
                st.rerun()

            except Exception as e:
                st.error(f"An error occurred: {e}")

# Page start here

if st.session_state["authenticated"]:
    email = st.session_state['email_user']
    # Display education data
    show_perfil(email)
    st.divider()
    edita_perfil(email)
    language_form(email)
    software_form(email)
    authenticate.button_logout()
else:
    st.write("# Edit Profile")
    st.markdown(
        """
        Streamline your job application process with AI-powered cover letters tailored to your profile and desired role.
    """
    )
    st.markdown('Please Log In')
    authenticate.button_login()
