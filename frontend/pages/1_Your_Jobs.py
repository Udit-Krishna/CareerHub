import streamlit as st
import asyncio
import os
import requests
import glob
from openai import OpenAI
import json

main_page = __import__("Home_Page")
API_BASE = "http://backend:8000"

os.makedirs("resume/", exist_ok=True)
os.makedirs("cover-letter/", exist_ok=True)
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

# --- Functions for API calls ---

def fetch_tabs_from_api():
    response = requests.get(f"{API_BASE}/load-jobs", params={"unique_id": st.session_state.user_email})
    response_json = response.json()
    print(response_json)
    return response_json['jobs']

def add_tab_to_api(tab_name):
    requests.post(f"{API_BASE}/add-job", json={"unique_id": st.session_state.user_email, "job_name": tab_name})

def delete_tab_from_api(tab_name):
    requests.post(f"{API_BASE}/remove-job", json={"unique_id": st.session_state.user_email, "job_name": tab_name})

def get_job_info_by_name(tab_name):
    response = requests.get(f"{API_BASE}/get-job-details", json={"unique_id": st.session_state.user_email, "job_name": tab_name})
    data = response.json()
    return data.get("job_url", ""), data.get("description", ""), data.get("requirements", "")

def fetch_description_by_url(tab_name, job_url):
    response = requests.post(f"{API_BASE}/fetch-description", json={"unique_id": st.session_state.user_email, "job_name": tab_name, "job_url": job_url})
    data = response.json()
    return data.get("description", ""), data.get("requirements", "")



if st.session_state.user_email and st.session_state.user_name:
    st.title("Your Space for Each Job Application")

    # Initialize tab list in session state
    if "tabs" not in st.session_state:
        st.session_state.tabs = fetch_tabs_from_api()
        
    with st.sidebar:
        st.header("Manage all your Jobs here")

        # Add Tab
        new_tab = st.text_input("➕ New Job", key="new_tab_input")
        if st.button("Add Job"):
            if new_tab and new_tab not in st.session_state.tabs:
                add_tab_to_api(new_tab)
                st.session_state.tabs = fetch_tabs_from_api()
                st.success(f"Added Job: {new_tab}")
            elif new_tab in st.session_state.tabs:
                st.warning("Job already exists.")
        
        # Delete Tab
        if st.session_state.tabs:
            tab_to_delete = st.selectbox("❌ Select Job to Delete", st.session_state.tabs)
            if st.button("Delete Job"):
                delete_tab_from_api(tab_to_delete)

                pattern = os.path.join("resume/", f"resume-{tab_to_delete}*")
                files_to_delete = glob.glob(pattern)
                for file in files_to_delete:
                    try:
                        os.remove(file)
                        print(f"Deleted: {file}")
                    except Exception as e:
                        print(f"Error deleting {file}: {e}")
                pattern = os.path.join("cover-letter/", f"cover-letter-{tab_to_delete}*")
                files_to_delete = glob.glob(pattern)
                for file in files_to_delete:
                    try:
                        os.remove(file)
                        print(f"Deleted: {file}")
                    except Exception as e:
                        print(f"Error deleting {file}: {e}")

                st.session_state.tabs = fetch_tabs_from_api()
                st.warning(f"Deleted Job: {tab_to_delete}")

        st.divider()
        
        # Logout button
        if st.button("Logout", type="primary", key="logout"):
            st.session_state.user_email = ''
            st.session_state.user_name = ''
            st.rerun()
        
    # --- Render tabs dynamically ---
    if st.session_state.tabs:
        tabs = st.tabs(st.session_state.tabs)
        for i, tab in enumerate(tabs):
            job_name = st.session_state.tabs[i]
            job_url_key = f"url_{job_name}"
            job_desc_key = f"desc_{job_name}"
            job_req_key = f"req_{job_name}"

            # Only fetch data once (on first render)
            if job_url_key not in st.session_state or job_desc_key not in st.session_state:
                job_url, job_desc, job_req = get_job_info_by_name(job_name)
                if job_url:
                    st.session_state[job_url_key] = job_url
                if job_desc:
                    st.session_state[job_desc_key] = job_desc
                if job_req:
                    st.session_state[job_req_key] = job_req

            with tab:
                st.subheader(f"💼 {job_name}")
                job_url = st.text_input("Job URL", key=job_url_key)
                
                # Show "Get Description" button if no description is present
                if not st.session_state.get(job_desc_key, ""):
                    if st.button("🔍 Get Description", key=f"btn_fetch_{job_name}"):
                        if job_url:
                            desc, req = fetch_description_by_url(job_name, job_url)
                            if desc:
                                st.session_state[job_desc_key] = desc
                                st.session_state[job_req_key] = req
                            st.rerun()
                        else:
                            st.warning("Please enter a job URL.")
                
                col1, col2 = st.columns(2)
                col1.text_area("Job Description", key=job_desc_key, height=300, disabled=True)
                col1.text_area("Qualifications and Requirements", key=job_req_key, height=300, disabled=True )

                if st.session_state[job_desc_key] and st.session_state[job_req_key]:
                    response = requests.get("http://backend:8000/get-job-uuid", json={"unique_id": st.session_state.user_email, "job_name": job_name})
                    job_uuid = response.json().get("job_uuid")
                    resume_path = f"./resume/resume-{job_name}-{job_uuid}.pdf"
                    letter_path = f"./cover-letter/cover-letter-{job_name}-{job_uuid}.pdf"
                    
                    if os.path.exists(resume_path):
                        with open(resume_path, "rb") as file:
                            col1.download_button(
                                label="📥 Download Tailored Resume PDF",
                                data=file,
                                file_name=os.path.basename(resume_path),
                                mime="application/pdf"
                            )
                    else:
                        if col1.button("Generate Tailored Resume for this Job", key=f"btn_resume_{job_name}"):
                            response = requests.get("http://backend:8000/load-details",
                                            params={"unique_id": st.session_state.user_email})
                            response_json = dict(response.json())
                            data = {}
                            for k,v in response_json.items():
                                data[k] = v
                            response = requests.post("http://backend:8000/generate-tailored-resume",
                                        json={"data": data, "job_desc" : st.session_state[job_desc_key]}
                            )
                            if response.status_code == 200:
                                file_name = '_'.join(st.session_state.user_name.split())
                                with open(resume_path, "wb") as f:
                                    f.write(response.content)
                                st.rerun()

                    if os.path.exists(letter_path):
                        with open(letter_path, "rb") as file:
                            col1.download_button(
                                label="📥 Download Cover Letter PDF",
                                data=file,
                                file_name=os.path.basename(letter_path),
                                mime="application/pdf"
                            )
                    else:
                        if col1.button("Generate Cover Letter for this Job", key=f"btn_cover_letter_{job_name}"):
                            response = requests.get("http://backend:8000/load-details",
                                            params={"unique_id": st.session_state.user_email})
                            response_json = dict(response.json())
                            data = {}
                            for k,v in response_json.items():
                                data[k] = v
                            response = requests.post("http://backend:8000/generate-cover-letter",
                                        json={"resume": data ,"job_desc" : st.session_state[job_desc_key]}
                            )
                            if response.status_code == 200:
                                file_name = '_'.join(st.session_state.user_name.split())
                                with open(letter_path, "wb") as f:
                                    f.write(response.content)
                                st.rerun()
                        
                    # Chatbot
                    with col2.container():
                        st.header("Ask our AI expert about your job fit.")
                        chat_key = f"messages_{job_name}"
                        history = st.container(height=650)
                        if "chat_input_count" not in st.session_state:
                            st.session_state.chat_input_count = 0
                        if chat_key not in st.session_state:
                            response = requests.get("http://backend:8000/load-details",
                                                params={"unique_id": st.session_state.user_email})
                            response_json = dict(response.json())
                            data = {}
                            for k,v in response_json.items():
                                data[k] = v
                            st.session_state[chat_key] = [
                                {"role": "developer", "content": f"""You are a helpful career assistant who is given the information about a job, along with its requirements and qualifications. Evaluate a person's resume using its JSON and answer the questions asked by the person. Do not make up any new information. Do not ask any questions back. Always be straight to the points and your responses must be very brief.
                                                                \nJob Description: {st.session_state[job_desc_key]}
                                                                \nJob Requirements and Qualifications: {st.session_state[job_req_key]}
                                                                \nPerson's Resume: {data}"""}
                            ]
                        # Display chat messages
                        for msg in st.session_state[chat_key][1:]:  # Skip the system prompt
                            with history.chat_message(msg["role"]):
                                st.markdown(msg["content"])
                        
                        if prompt := st.chat_input("Ask our AI whether the job suits you...", key=f"{job_name}_chat_input"):
                            st.session_state[chat_key].append({"role": "user", "content": prompt})
                            with history.chat_message("user"):
                                st.markdown(prompt)

                            with history.chat_message("assistant"):
                                stream = openai_client.chat.completions.create(
                                    model="gpt-4.1-nano-2025-04-14",
                                    messages=st.session_state[chat_key],
                                    stream=True
                                )
                                response = st.write_stream(stream)
                            st.session_state[chat_key].append({"role": "assistant", "content": response})
                        
                    st.divider()

                    # Questions
                    coll_1, coll_2 = st.columns(2)
                    coll_1.subheader("Find Relevant Interview Questions for the Job")

                    check_response = requests.get("http://backend:8000/get-questions", json={"unique_id": st.session_state.user_email, "job_name": job_name})
                    if check_response.status_code == 200 and check_response.json().get("isFound"):
                        response_json = check_response.json()
                        
                        with coll_1.expander("Technical Questions"):
                            st.markdown(response_json["technical_questions"])
                        with coll_1.expander("HR Questions"):
                            st.markdown(response_json["hr_questions"])
                        
                        coll_2.subheader("DSA Questions")
                        with coll_2.container():
                            questions = response_json["leetcode_questions"]
                            for q in questions:
                                for title, url in q.items():
                                    with st.expander(title):
                                        st.markdown(url)
                                        if st.button(f"🔍 Show Tips to solve this question", key=f"{job_name}_{title}_desc_button"):
                                            with st.spinner("Trying to solve the problem..."):
                                                lc_response = requests.get("http://backend:8000/get-leetcode-description",
                                                                        json={"question": title, "url": url})
                                                lc_response_json = lc_response.json()
                                                st.markdown(lc_response_json['desc'])
                    else:
                        if coll_1.button("❓ Find Interview Questions", key=f"{job_name}_find_tech"):
                            response_user = requests.get("http://backend:8000/load-details",
                                                params={"unique_id": st.session_state.user_email})
                            response_user_json = dict(response_user.json())
                            data = {}
                            for k,v in response_user_json.items():
                                data[k] = v
                            with st.spinner("Finding Questions... (This may take a minute)"):
                                requests.post("http://backend:8000/find-questions",
                                                        json={
                                                            "job_name": job_name,
                                                            "job_desc": st.session_state[job_desc_key],
                                                            "job_req": st.session_state[job_req_key],
                                                            "user_info": data,
                                                            "unique_id": st.session_state.user_email
                                                        })
                            st.rerun()
                    

    else:
        st.info("No Jobs available. Add one from the sidebar to get started.")






else:
    st.switch_page("Home_Page.py")