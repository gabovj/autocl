import streamlit as st
import components.authenticate as authenticate
import components.charts as charts

st.set_page_config(
    page_title="Home", 
    page_icon="🆑", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Report a bug': "mailto:gabriel.vapp@gmail.com",
        'About': "# Go and get that Job!"
    }
    )

authenticate.set_st_state_vars()


# st.text(st.session_state)

# Add login/logout buttons
if st.session_state["authenticated"]:
    email = st.session_state['email_user']
    charts.display_plots(email)
    authenticate.button_logout()
else:
    col1, col2, col3 = st.columns(3)
    with col2:
        st.image('test_logo.png', width=150)
    st.write("# AutoCover: Tailored Cover Letters Made Easy")
    st.markdown(
        """
        Streamline your job application process with AI-powered cover letters tailored to your profile and desired role.
    """
    )
    authenticate.button_login()