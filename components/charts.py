import streamlit as st
from pymongo import MongoClient
import datetime
import plotly.express as px
import pandas as pd

# Use your MongoDB Atlas connection string here
mongo_uri = st.secrets["mongo_uri"]
# Create a MongoClient using the provided URI
client = MongoClient(mongo_uri)
# Specify the database and collection
db = client["job"]
collection = db["profile"]

def display_plots(email):
    st.title('Job Applications')
        # st.text(email)
    try:   
        perfil = collection.find_one({"email": email})
        name = perfil['name']
        with st.sidebar:
            st.write(f'Ahoj, {name}!')
        total_ja = len(perfil['job_applications'])
        # Get the current year and month
        now = datetime.datetime.now()
        current_year = now.year
        current_month = now.month
        # Count the number of dictionaries with a creation_date in the current month
        current_month_ja = sum(1 for application in perfil['job_applications'] if application['creation_date'].year == current_year and application['creation_date'].month == current_month)
        now = datetime.datetime.now()
        month_name = now.strftime('%B')
        year = now.strftime('%y')
        # count cover letter
        non_none_cover_letters = [application for application in perfil['job_applications'] if 'cover_letter' in application and application['cover_letter'] is not None]
        total_cl = len(non_none_cover_letters)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="##### Total Job Applications", value = total_ja)
        with col2:
            st.metric(label=f"##### {month_name} {year} Job Applications", value=current_month_ja, delta= total_ja - current_month_ja)
        with col3:
            st.metric(label="##### Cover Letters Generated", value = total_cl)
        st.divider()
        # Extract the cities from the job applications
        cities = [job['city_job'] for job in perfil['job_applications']]
        # Create a dataframe with the cities
        df = pd.DataFrame(cities, columns=['City'])
        # Count the occurrences of each city
        city_counts = df['City'].value_counts().reset_index()
        city_counts.columns = ['City', 'Count']
        # Plot the cities
        # fig = px.bar(city_counts, x='City', y='Count', title="Cities from Job Applications", 
        #             labels={'City': 'City', 'Count': 'Number of Applications'},
        #             color_discrete_sequence=px.colors.sequential.RdBu)
        fig = px.pie(city_counts, values='Count', names='City', 
                    #  title="Cities from Job Applications", 
                    color_discrete_sequence=px.colors.sequential.RdBu)
        col1, col2 = st.columns(2)
        with col1:
            st.write('##### Cities from Job Applications')
            st.plotly_chart(fig, theme="streamlit")
    except:
        st.markdown("""
             **No Data to Display** -
             Please take the following actions:
             - Edit Profile
             - Add Professional Experience
             - Add Academic Records
             - Add Job Applications
             """)
        
    


# email = st.session_state['email_user']
# display_plots(email)