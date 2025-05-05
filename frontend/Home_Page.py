import streamlit as st
import requests
import os
from dotenv import load_dotenv
import asyncio
from httpx_oauth.clients.google import GoogleOAuth2
import firebase_admin
from firebase_admin import auth, exceptions, credentials, initialize_app

load_dotenv('.env')
os.makedirs("resume/", exist_ok=True)

CLIENT_ID = os.environ['GOOGLE_OAUTH_CLIENT_ID']
CLIENT_SECRET = os.environ['GOOGLE_OAUTH_CLIENT_SECRET']
REDIRECT_URI = os.environ['GOOGLE_OAUTH_REDIRECT_URI']

cred = credentials.Certificate("careerhub-925c0.json")

try:
    firebase_admin.get_app()
except ValueError:
    initialize_app(cred)

client = GoogleOAuth2(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

st.set_page_config(page_title="CareerHub", layout="wide")
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

async def get_access_token(client: GoogleOAuth2, redirect_url: str, code: str):
    return await client.get_access_token(code, redirect_url)

async def get_email(client: GoogleOAuth2, token: str):
    user_id, user_email = await client.get_id_email(token)
    return user_id, user_email

def get_logged_in_user_email():
        query_params = st.query_params
        code = query_params.get('code')
        
        if code:
            token = asyncio.run(get_access_token(client, REDIRECT_URI, code))
            st.query_params.clear()

            if token:
                user_id, user_email = asyncio.run(get_email(client, token['access_token']))
                if user_email:
                    try:
                        user = auth.get_user_by_email(user_email)
                    except exceptions.FirebaseError:
                        user = auth.create_user(email=user_email)
                    st.session_state.user_email = user.email
        return None


def show_login_button():
    authorization_url = asyncio.run(client.get_authorization_url(
        REDIRECT_URI,
        scope=["email", "profile"],
        extras_params={"access_type":"offline"}
    ))
    st.markdown(f'''
        <style>
            .login-button {{
                display: inline-block;
                padding: 10px 20px;
                font-size: 20px;
                font-weight: bold;
                color: black;
                background-color: white; /* Google Blue */
                border: none;
                border-radius: 5px;
                text-decoration: none;
                text-align: center;
                transition: background-color 0.3s;
            }}
            .login-button:hover {{
                background-color: #357ae8;
            }}
        </style>
        <a class="login-button" href="{authorization_url}" target="_self">Login with Google</a>''', unsafe_allow_html=True)
    get_logged_in_user_email()        


def main():
    # When not logged in
    if not st.session_state.user_email and not st.session_state.user_name:
        st.title("Welcome to CareerHub!")
        st.subheader("Your End to End Hands-Free Job Application Optimization Platform")
        st.divider()

    with st.sidebar:
        if not st.session_state.user_email:
            get_logged_in_user_email()
            if not st.session_state.user_email:
                show_login_button()
    
    if st.session_state.user_email:
        if not st.session_state.user_name:
            response = requests.get("http://backend:8000/login", params={"unique_id": st.session_state.user_email})
            response_json = response.json()

            if "Error" in response_json and response_json["Error"] == "User not found. Register first!":
                name = st.sidebar.text_input("Enter your Name", "")
                if name:
                    requests.post(
                            "http://backend:8000/register",
                            params={"unique_id": st.session_state.user_email, "name": name},
                    )                
            else:
                st.session_state.user_name = response_json.get("name", "User")
                response = requests.get("http://backend:8000/load-details",
                                    params={"unique_id": st.session_state.user_email})
                response_json = response.json()
                if response_json.get("personal_details") == None:
                    st.session_state.personal_details = {
                        "first_name": "",
                        "last_name": "",
                        "email": "",
                        "phone": "",
                        "linkedin": "",
                        "github": ""
                    }
                else:
                    st.session_state.personal_details = response_json.get("personal_details")
                st.session_state.education = response_json.get("education", [])
                st.session_state.work_experience = response_json.get("work_experience", [])
                st.session_state.projects = response_json.get("projects", [])
                if response_json.get("skills") == None:
                    st.session_state.skills = []
                else:
                    st.session_state.skills = response_json["skills"].get("skills", [])
            st.rerun()
        
        # When logged in
        else:

            st.title(f"Welcome to CareerHub, {st.session_state.user_name}!")

            # Sidebar for navigation
            tabs = ["Personal Details", "Education", "Work Experience", "Projects", "Skills"]
            selected_tab = st.sidebar.radio("Your Details", tabs)
            # Personal Details Tab
            if selected_tab == "Personal Details":
                st.subheader("Personal Details")
                col1, col2 = st.columns([1, 1])
                st.session_state.personal_details["first_name"] = col1.text_input(
                    "First Name", st.session_state.personal_details["first_name"])
                st.session_state.personal_details["last_name"] = col2.text_input(
                    "Last Name", st.session_state.personal_details["last_name"])
                st.session_state.personal_details["email"] = st.text_input(
                    "Email", st.session_state.personal_details["email"])
                st.session_state.personal_details["phone"] = st.text_input(
                    "Phone", st.session_state.personal_details["phone"])
                st.session_state.personal_details["linkedin"] = st.text_input(
                    "LinkedIn Profile URL (https://www.linkedin.com/in/<?>)", st.session_state.personal_details["linkedin"])
                st.session_state.personal_details["github"] = st.text_input(
                    "GitHub Profile URL (https://github.com/<?>)", st.session_state.personal_details["github"])

            # Education Tab
            elif selected_tab == "Education":
                st.subheader("Education Details")
                # Display existing education entries
                for i, edu in enumerate(st.session_state.education):
                    with st.expander(f"Education {i+1}", expanded=True):
                        edu["degree"] = st.text_input("Degree", edu.get("degree", ""), key=f"degree_{i}")
                        edu["university"] = st.text_input("University / College", edu.get("university", ""), key=f"university_{i}")
                        edu["start_year"] = st.number_input("Year of Start", 1900, 2100, edu.get("start_year", 2020), key=f"start_year_{i}")
                        edu["graduation_year"] = st.number_input("Year of Graduation", 1900, 2100, edu.get("graduation_year", 2024), key=f"grad_year_{i}")
                        edu["gpa"] = st.number_input("CGPA", 0.0, 10.0, edu.get("gpa", 0.0), step=0.1, key=f"gpa_{i}")
                        edu["description"] = st.text_area("Description (Write in multiple lines for bulleted points)", edu.get("description", ""), key=f"description_{i}")
                        if st.button("Remove", key=f"remove_edu_{i}"):
                            st.session_state.education.pop(i)
                            st.rerun()
                if st.button("➕ Add Education"):
                    st.session_state.education.append({"degree": "", "university": "", "graduation_year": 2024, "gpa": 0.0})
                    st.rerun()

            # Work Experience Tab
            elif selected_tab == "Work Experience":
                st.subheader("Work Experience")
                for i, work in enumerate(st.session_state.work_experience):
                    with st.expander(f"Work Experience {i+1}", expanded=True):
                        work["job_title"] = st.text_input("Job Title", work.get("job_title", ""), key=f"job_title_{i}")
                        work["company"] = st.text_input("Company Name", work.get("company", ""), key=f"company_{i}")
                        work["location"] = st.text_input("Location", work.get("location", ""), key=f"location_{i}")
                        work["start_year"] = st.number_input("Year of Start", 1900, 2100, work.get("start_year", 2020), key=f"start_year_{i}")
                        work["end_year"] = st.number_input("Year of End", 1900, 2100, work.get("end_year", 2024), key=f"end_year_{i}")
                        work["work_desc"] = st.text_area("Job Description (Write in multiple lines for bulleted points)", work.get("work_desc", ""), key=f"work_desc_{i}")
                        if st.button("Remove", key=f"remove_work_{i}"):
                            st.session_state.work_experience.pop(i)
                            st.rerun()
                if st.button("➕ Add Work Experience"):
                    st.session_state.work_experience.append({"job_title": "", "company": "", "location": "", "work_desc": ""})
                    st.rerun()

            # Projects Tab
            elif selected_tab == "Projects":
                st.subheader("Projects")
                for i, proj in enumerate(st.session_state.projects):
                    with st.expander(f"Project {i+1}", expanded=True):
                        proj["project_name"] = st.text_input("Project Name", proj.get("project_name", ""), key=f"project_name_{i}")
                        proj["project_tech"] = st.text_area("Technologies Used", proj.get("project_tech", ""), key=f"project_tech_{i}")
                        proj["project_link"] = st.text_input("Project URL", proj.get("project_link", ""), key=f"project_link_{i}")
                        proj["project_desc"] = st.text_area("Project Description (Write in multiple lines for bulleted points)", proj.get("project_desc", ""), key=f"project_desc_{i}")
                        if st.button("Remove", key=f"remove_proj_{i}"):
                            st.session_state.projects.pop(i)
                            st.rerun()
                if st.button("➕ Add Project"):
                    st.session_state.projects.append({"project_name": "", "project_desc": "", "project_link": ""})
                    st.rerun()

            # Skills Tab
            elif selected_tab == "Skills":
                st.subheader("Skills")
                for i, skill in enumerate(st.session_state.skills):
                    col1, col2 = st.columns([4, 1])
                    skill_text = col1.text_input(f"Skill {i+1}", skill, key=f"skill_{i}")
                    st.session_state.skills[i] = skill_text  # Update skill entry
                    if col2.button("❌", key=f"remove_skill_{i}"):
                        st.session_state.skills.pop(i)
                        st.rerun()
                if st.button("➕ Add Skill"):
                    st.session_state.skills.append("")
                    st.rerun()
            
            # Submit Button
            if st.button("Save Details", type="primary"):
                st.success("Your details have been saved successfully! 🎉")
                data = {}
                data['personal_details'] = st.session_state['personal_details']
                data['education'] = st.session_state['education']
                data['work_experience'] = st.session_state['work_experience']
                data['projects'] = st.session_state['projects']
                data['skills'] = st.session_state['skills']
                requests.post("http://backend:8000/update-details",
                    json={"unique_id": st.session_state.user_email, "content": data},
                )
                            
            # Generate Resume
 
            side_col1, side_col2 = st.sidebar.columns([0.55, 0.45])
            if side_col1.button("Generate Resume", type="secondary", key="generate"):
                response = requests.get("http://backend:8000/load-details",
                                    params={"unique_id": st.session_state.user_email})
                response_json = dict(response.json())
                data = {}
                for k,v in response_json.items():
                    data[k] = v
                response = requests.post("http://backend:8000/generate-resume",
                            json={"data": data}
                )                                
                if response.status_code == 200:
                    file_name = '_'.join(st.session_state.user_name.split())
                    with open(f"resume/resume_{file_name}.pdf", "wb") as f:
                        f.write(response.content)
                    side_col2.success("Resume generated successfully!")
                    with open(f"resume/resume_{file_name}.pdf", "rb") as file:
                        side_col1.download_button(
                            label="Download Resume",
                            data=file,
                            file_name=f"resume_{file_name}.pdf",
                            mime="application/pdf",
                        )
                    os.remove(f"resume/resume_{file_name}.pdf")
                else:
                    side_col2.error("Failed to generate resume.")
                
            st.sidebar.divider()


            # Logout button
            if st.sidebar.button("Logout", type="primary", key="logout"):
                st.session_state.user_email = ''
                st.session_state.user_name = ''
                st.rerun()
    

    


if __name__ == "__main__":
    main()