import subprocess
import os

async def generate_latex(data, rand_uuid):
    first_name = data["personal_details"]["first_name"]
    last_name = data["personal_details"]["last_name"]
    email = data["personal_details"]["email"]
    phone = data["personal_details"]["phone"]
    linkedin = data["personal_details"]["linkedin"]
    github = data["personal_details"]["github"]

    # Extract education dynamically
    education_list = []
    for i, edu in enumerate(data["education"], start=1):
        vars()[f"university_{i}"] = edu["university"]
        vars()[f"degree_{i}"] = edu["degree"]
        vars()[f"start_year_{i}"] = edu["start_year"]
        vars()[f"graduation_year_{i}"] = edu["graduation_year"]
        vars()[f"gpa_{i}"] = edu["gpa"]
        vars()[f"description_{i}"] = edu["description"]
        education_list.append(edu)

    # Extract work experience dynamically
    work_experience_list = []
    for i, work in enumerate(data["work_experience"], start=1):
        vars()[f"company_{i}"] = work["company"]
        vars()[f"location_{i}"] = work["location"]
        vars()[f"job_title_{i}"] = work["job_title"]
        vars()[f"start_year_{i}"] = work["start_year"]
        vars()[f"end_year_{i}"] = work["end_year"]
        vars()[f"work_desc_{i}"] = work["work_desc"]
        work_experience_list.append(work)

    # Extract projects dynamically
    projects_list = []
    for i, proj in enumerate(data["projects"], start=1):
        vars()[f"project_name_{i}"] = proj["project_name"]
        vars()[f"project_tech_{i}"] = proj["project_tech"]
        vars()[f"project_link_{i}"] = proj["project_link"]
        vars()[f"project_desc_{i}"] = proj["project_desc"]
        projects_list.append(proj)

    # Extract skills
    skills_list = data["skills"]["skills"]

    # Print extracted values (for debugging purposes)
    print(f"Name: {first_name} {last_name}")
    print(f"Email: {email}")
    print(f"Phone: {phone}")
    print(f"LinkedIn: {linkedin}")
    print(f"GitHub: {github}")
    print("Education:", education_list)
    print("Work Experience:", work_experience_list)
    print("Projects:", projects_list)
    print("Skills:", skills_list)
    
    # Extract personal details
    # LaTeX template
    latex_string = r"""
\documentclass[letterpaper,11pt]{article}

\usepackage{fontawesome5}
\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\input{glyphtounicode}

% Custom font
\usepackage[default]{lato}

\pagestyle{fancy}
\fancyhf{} % clear all header and footer fields
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

% Adjust margins
\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.5in}
\addtolength{\textheight}{1.0in}

\urlstyle{same}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

% Sections formatting
\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large
}{}{0em}{}[\color{black}\titlerule\vspace{-5pt}]

% Ensure that generate pdf is machine readable/ATS parsable
\pdfgentounicode=1

%-------------------------%
% Custom commands
\begin{document}
\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubSubheading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \textit{\small#1} & \textit{\small #2} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & #2 \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

\definecolor{Black}{RGB}{0, 0, 0}
\newcommand{\seticon}[1]{\textcolor{Black}{\csname #1\endcsname}}

%-------------------------------------------%
%%%%%%  RESUME STARTS HERE  %%%%%

%----------HEADING----------%
\begin{center}
    \textbf{\Huge \scshape """ + f"{first_name} {last_name}" + r"""} \\ \vspace{1pt}
    \seticon{faPhone} \ \small """ + f"{phone}" + r""" \quad
    \href{mailto:""" + f"{email}" + r"""}{\seticon{faEnvelope} \underline{""" + f"{email}" + r"""}} \quad
    \href{https://www.linkedin.com/in/}{\seticon{faLinkedin} \underline{linkedin.com/""" + f"{linkedin}" + r"""}} \quad
    \href{https://github.com/}{\seticon{faGithub} \underline{github.com/""" + f"{github}" + r"""}}
\end{center}
"""
    latex_string += r"""
%-----------EDUCATION-----------%
\section{Education}
\resumeSubHeadingListStart
"""

    for edu in education_list:
        latex_string += rf"""
    \resumeSubheading
    {{{edu["university"]}}}{{{edu["start_year"]} - {edu["graduation_year"]}}}
    {{{edu["degree"]} (CGPA: {edu["gpa"]})}}{{}}
    \resumeItemListStart
    """
        for desc in edu["description"].split("\n"):
            latex_string += rf"     \resumeItem{{{desc}}}" + "\n"
    
        latex_string += r"""
    \resumeItemListEnd
    """

    latex_string += r"\resumeSubHeadingListEnd"

    latex_string += r"""
%-----------EXPERIENCE-----------%
\section{Experience}
\resumeSubHeadingListStart
"""

    for work in work_experience_list:
        latex_string += rf"""
    \resumeSubheading
    {{{work["company"]}}}{{{work["start_year"]} -- {work["end_year"]}}}
    {{{work["job_title"]}}}{{{work["location"]}}}
    \resumeItemListStart
    """
        for desc in work["work_desc"].split("\n"):
            latex_string += rf"     \resumeItem{{{desc}}}" + "\n"
    
        latex_string += r"    \resumeItemListEnd " + "\n"

    latex_string += r"\resumeSubHeadingListEnd"

 
    latex_string += r"""
%-----------PROJECTS-----------%
\section{Projects}
\resumeSubHeadingListStart
"""

    for project in projects_list:
        latex_string += rf"""
    \resumeProjectHeading
    {{\textbf{{{project["project_name"]}}} $|$ \emph{{{project["project_tech"]}}}}}""" + r"{\emph{\href{" + f'{project["project_link"]}' + r"}{\seticon{faLink} \underline{Project URL}}}}" + rf""" 
    \resumeItemListStart
    """
        for desc in project["project_desc"].split("\n"):
            latex_string += rf"     \resumeItem{{{desc}}}" + "\n"
    
        latex_string += r"    \resumeItemListEnd " + "\n"

    latex_string += r"""\resumeSubHeadingListEnd

%-----------SKILLS-----------%
\section{ Skills}
    \begin{itemize}[leftmargin=0.15in, label={}]
	\small{\item{""" + ', '.join(skills_list) + r"""}}
    \end{itemize}

%-------------------------------------------%
\end{document}
"""

    with open(f"resume/{rand_uuid}.tex", "w") as f:
        f.write(latex_string)

    subprocess.call(["pdflatex", "--interaction=nonstopmode", f"{rand_uuid}.tex"], cwd=os.path.dirname(os.path.realpath(__file__))+"/resume")

# res = generate_latex({
#     "personal_details": {
#         "first_name": "Udit",
#         "last_name": "Krishna",
#         "email": "uditkrishna2003@gmail.com",
#         "phone": "9543040506666",
#         "linkedin": "awfhagfugewjugyb",
#         "github": "hniygniyg"
#     },
#     "education": [
#         {
#             "university": "DHFXTD",
#             "degree": "awefwrghAWRG",
#             "start_year": 2020,
#             "graduation_year": 2024,
#             "gpa": 9.88,
#             "description": "SGDFGSZDFGBZDBHSZD"
#         },
#         {
#             "university": "fgnfthnfth",
#             "degree": "fbdhfhdxhx",
#             "start_year": 2024,
#             "graduation_year": 2026,
#             "gpa": 10,
#             "description": "dfhxtyhdxhxrth"
#         }
#     ],
#     "work_experience": [
#         {
#             "company": "natwest",
#             "location": "chennai",
#             "job_title": "intern",
#             "start_year": 2024,
#             "end_year": 2024,
#             "work_desc": "summa d&a intern"
#         }
#     ],
#     "projects": [
#         {
#             "project_name": "argeghaer",
#             "project_tech": "gszgszdgsz",
#             "project_link": "dfghstrsthr",
#             "project_desc": "thdtxghdrtxhdrxh"
#         },
#         {
#             "project_name": "tdhsrstsh",
#             "project_tech": "gdgsdxrgs",
#             "project_link": "kgyujyj",
#             "project_desc": "xfgxdrsgesrt"
#         }
#     ],
#     "skills": {
#         "skills": [
#             "sagfarswfasw",
#             "guyjgj",
#             "aqqsxq"
#         ]
#     }
# })

