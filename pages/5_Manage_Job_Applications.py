import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode
import openai
from docx import Document
from io import BytesIO
import components.authenticate as authenticate

st.set_page_config(
    page_title="Job Applications", 
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
# Openai connect
openai_key = st.secrets["OPENAI_API_KEY"]
openai.api_key = openai_key

def show_job_applications(email):
    st.title('Manage Job Applications')
    st.markdown('*(Filter and select the desired Job Application)')
    perfil = collection.find_one({"email": email})
    if perfil:
        name_cl = perfil['name']
        first_name = name_cl.split()[0]
        relocate_cl = perfil['relocate']
        summary_cl = perfil['summary']
        key_facts_cl = perfil['key_facts']
        actual_city_cl = perfil['city']
        actual_country_cl = perfil['country']
        profesional_experience_cl = perfil['experience']
        academic_cl = perfil['education']
        email_cl = perfil['email']
        languages_cl = perfil['languages']
        software_skills_cl = perfil['software_skills']
        with st.sidebar:
            st.write(f'Ahoj, {first_name}!')

        # st.markdown(perfil['languages'])
        job_applications_db = perfil.get("job_applications")
        job_applications_df = pd.DataFrame(job_applications_db)
        # st.markdown(job_applications_df.columns)
        # select the columns you want the users to see
        gb = GridOptionsBuilder.from_dataframe(job_applications_df[['job_position', 'company_name', 'city_job','creation_date']]) 
        # configure selection
        gb.configure_selection(selection_mode="single", use_checkbox=True)
        gb.configure_side_bar()
        gridOptions = gb.build()

        data = AgGrid(job_applications_df,
              gridOptions=gridOptions,
              enable_enterprise_modules=True,
              allow_unsafe_jscode=True,
              update_mode=GridUpdateMode.SELECTION_CHANGED,
              columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
        
        selected_rows = data["selected_rows"]

        if len(selected_rows) != 0:

            job_application_id_cl = selected_rows[0]['job_application_id']
            job_position_cl = selected_rows[0]['job_position']
            company_name_cl = selected_rows[0]['company_name']
            about_company_cl = selected_rows[0]['about_company']
            about_role_cl = selected_rows[0]['about_role']
            experience_success_cl = selected_rows[0]['experience_success']
            ciy_job_cl = selected_rows[0]['city_job']
            country_job_cl = selected_rows[0]['country_job']

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("##### Job Position")
                st.markdown(f":orange[{selected_rows[0]['job_position']}]")
                st.markdown("##### Location")
                st.markdown(f":orange[{selected_rows[0]['city_job']},] " + f":orange[{selected_rows[0]['country_job']}]")
                st.markdown("##### Creation Date")
                creation_date_obj = datetime.fromisoformat(selected_rows[0]['creation_date'])
                formatted_creation_date = creation_date_obj.strftime("%d / %b / %Y")
                st.markdown(f":orange[{formatted_creation_date}]")
                
            with col2:
                st.markdown("##### Company")
                st.markdown(f":orange[{selected_rows[0]['company_name']}]")
                st.markdown("##### Salary")
                if selected_rows[0]['salary'] is not None:
                    formatted_salary = "{:,}".format(selected_rows[0]['salary'])
                else:
                    formatted_salary = "Unknown"
                st.markdown(f":orange[{formatted_salary}]")
                st.markdown("##### Closing Date")
                closing_date_obj = datetime.fromisoformat(selected_rows[0]['closing_date'])
                formatted_closing_date = closing_date_obj.strftime("%d / %b / %Y")
                st.markdown(f":orange[{formatted_closing_date}]")
            
            col1, col2 = st.columns(2)

            with col1:
                st.markdown('##### Link')
                selected_link_db = selected_rows[0]['link']
                st.link_button("Go to job info", selected_link_db)
            with col2:
                if selected_rows[0]['cover_letter'] is None:                 
                    st.markdown('##### Cover Letter')
                    if st.button('Generate cover letter'):
                    
                        completion = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You are a human resources expert in creating cover letters."},
                                {"role": "user", 
                                "content": f"""Write a cover letter with the following info
                                Applicant Data:
                                name of job seeker: {name_cl}
                                email: {email_cl}
                                living now in: {actual_city_cl}, {actual_country_cl}
                                willing to relocate: {relocate_cl}
                                academic background: {academic_cl}
                                profesional experience: {profesional_experience_cl}
                                profesional summary: {summary_cl}
                                key_facts: {key_facts_cl}
                                language skills: {languages_cl}
                                software skills: {software_skills_cl}

                                Desired job position data:
                                job position: {job_position_cl}
                                location where the job will be developed: {ciy_job_cl}, {country_job_cl}
                                company name: {company_name_cl}
                                about the company: {about_company_cl}
                                about the role: {about_role_cl}
                                experience and keys to success: {experience_success_cl}

                                The cover letter should have empashis in how my profesional experience can help to the company and work team,
                                you dont need to list all my academic credentials, languages and previus profesional experience. It must have maximum 3 paragraphs.
                                Make sure to include my contact details, also take into account if i am willing to relocate
                                """}
                            ]
                        )
                        # Extracting the content and save it to mongodb
                        cover_letter_content = completion['choices'][0]['message']['content']
                        
                        collection.update_one(
                            {
                                "email": email,
                                "job_applications.job_application_id": job_application_id_cl
                            },
                            {
                                "$set": {"job_applications.$.cover_letter": cover_letter_content}
                            }
                        )
                        
                        # Update the data loaded
                        perfil_updated = collection.find_one({"email": email})
                        job_applications_db_updated = perfil_updated.get("job_applications")
                        # st.rerun()
                        # text_cl = completion.choices[0].message
                        for i in job_applications_db_updated:
                            if i.get('job_application_id') == job_application_id_cl:
                                cl_raw = i['cover_letter']
                        
                        # Generate DOCX bytes from content
                        docx_bytes = generate_docx_bytes_from_content(cl_raw)
                        st.download_button(
                            label="Download Cover Letter",
                            data=docx_bytes,
                            file_name=f'{job_position_cl}_{company_name_cl}_cover_letter.docx',
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )                        
                else:
                    st.markdown('##### Cover Letter')
                    # Retrieve the cover letter

                    for i in job_applications_db:
                        if i.get('job_application_id') == job_application_id_cl:
                            cl_raw = i['cover_letter']
                    
                    # Generate DOCX bytes from content
                    docx_bytes = generate_docx_bytes_from_content(cl_raw)
                    st.download_button(
                        label="Download Cover Letter",
                        data=docx_bytes,
                        file_name=f'{job_position_cl}_{company_name_cl}_cover_letter.docx',
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )                   
    else:
        st.info(f"No data saved for {email}.")

def generate_docx_bytes_from_content(content):
    doc = Document()
    doc.add_paragraph(content)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

if st.session_state["authenticated"]:
    email = st.session_state['email_user']
    show_job_applications(email)
    authenticate.button_logout()
else:
    st.write("# Manage Job Applications")
    st.markdown(
        """
        Streamline your job application process with AI-powered cover letters tailored to your profile and desired role.
    """
    )
    st.markdown('Please Log In')
    authenticate.button_login()