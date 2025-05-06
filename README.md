# CareerHub

This is a containerized version of the CareerHub platform, a cutting-edge AI-powered solution designed to simplify and optimize the job application process. This repository includes a full Docker Compose setup to deploy the frontend and backend services in isolated containers for seamless development and deployment.


## 🚀 About CareerHub

CareerHub is an AI-powered platform that streamlines the job application journey through intelligent automation and personalized support. Its key capabilities include:
- 🔄 One-time information entry to generate professional resumes using LaTeX templates.
- 🧠 AI-powered resume personalization using OpenAI’s GPT-4.1-nano, matching resumes to job descriptions with ATS-friendly formatting.
- 📊 Resume-to-job compatibility analysis, skill gap detection, and actionable improvement suggestions.
- 💬 Interview assistance powered by GPT-o4-mini, helping candidates craft thoughtful responses to challenging questions.
- 🏢 Company-specific insights such as standard interview questions and key organizational data.

By combining resume generation, job search optimization, and interview preparation into a unified interface, CareerHub transforms the traditional job application process into a structured, efficient, and data-driven experience.


## 🐳 Dockerized Architecture

This repo uses Docker Compose to manage the platform’s components as isolated services:
```
careerhub-docker/
├── backend/              # API logic (Python FastAPI)
├── frontend/             # Client-side app (Python Streamlit)
├── .env                  # Environment variables (optional)
├── .gitignore            # Files to be ignored by git
├── docker-compose.yaml    # Docker Compose config for multi-service orchestration
└── README.md
```

## ⚙️ Getting Started

### Prerequisites
- Docker
- Docker Compose (v2 or higher)

### Step-by-Step
1. Clone this repo

```bash
git clone https://github.com/Udit-Krishna/CareerHub.git
cd CareerHub
```

2. Create a Firebase Application and save the credentials JSON file in `./frontend/` as `careerhub.json`

3. Create .env file. Enter relevant details in place of `...`
```env
PSQL_DRIVERNAME="postgresql"
PSQL_USERNAME="..."
PSQL_PASSWORD="..."
PSQL_HOST="db"
PSQL_PORT=5432
PSQL_DATABASE="careerhub"
OPENAI_API_KEY="..."
GOOGLE_OAUTH_CLIENT_ID="..."
GOOGLE_OAUTH_CLIENT_SECRET="..."
GOOGLE_OAUTH_REDIRECT_URI="http://localhost:8501/"
PGADMIN_DEFAULT_EMAIL="admin@admin.com"
PGADMIN_DEFAULT_PASSWORD="admin"
```
4.	Build and run the services
- If there are any changes made to the files, use
    ```bash
    docker-compose up --build
    ```
- Else, use
    ```bash
    docker-compose up
    ```

5.	Access the website using this URL in your browser: http://localhost:8501

6.	To Access pgAdmin

    Open your browser and go to: http://localhost:5050

  	Login with:
       - Email: admin@admin.com
       - Password: admin


## 🧠 Technologies Used
- Docker, Docker Compose
- Frontend: Streamlit (Python)
- Backend: FastAPI (Python)
- OpenAI GPT-4.1-nano & GPT-o4-mini integrations
- LaTeX for resume generation
- Database: PostgreSQL for data persistence
