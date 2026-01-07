📄 Student Reimbursement Portal

A web-based reimbursement management system built using Flask, SQLite, HTML, CSS, and JavaScript.
The application allows students (clubs) to submit reimbursement requests with bills and passbook documents, and admins to review, approve, or disapprove them.

🚀 Features
👨‍🎓 Student Module

Login using Student role

Upload multiple bill PDFs

Upload passbook PDF

Enter bank details once (auto-filled for all bills)

Enter bill amount per bill

Automatic Grand Total calculation

View request status (Pending / Approved / Disapproved)

Download submitted data as Excel

🧑‍💼 Admin Module

Login using Admin role

View all student reimbursement requests

View uploaded bills and passbook PDFs in a new tab

View consolidated purchase details

Approve or Disapprove requests

Download approved requests as Excel

🛠️ Tech Stack

Backend: Python (Flask)

Database: SQLite

Frontend: HTML, CSS, JavaScript

File Uploads: PDF (Bills & Passbook)

Version Control: Git

📁 Project Structure
reimbursement_system/
│
├── app.py
├── database.db              (ignored in git)
├── templates/
│   ├── login.html
│   ├── student.html
│   ├── admin.html
│   └── admin_view.html
│
├── static/
│   ├── style.css
│   ├── script.js
│   └── images/
│       ├── login-bg.jpg
│       └── college-banner.png
│
├── uploads/                 (ignored in git)
│   ├── bills/
│   └── passbooks/
│
├── .gitignore
└── README.md

🔐 Login Details (Sample)
Admin

User ID: admin

Password: admin123

Student

User ID: student

Passwords (example clubs):

sport123 → Sports Team

lib123 → Library Team

eco123 → Eco Team

⚠️ All passwords are stored securely in the database and cannot be changed from UI.

⚙️ Setup Instructions
1️⃣ Clone the Repository
git clone https://github.com/<your-username>/reimbursement-system.git
cd reimbursement-system

2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate

3️⃣ Install Dependencies
pip install flask

4️⃣ Run the Application
python app.py

5️⃣ Open in Browser
http://127.0.0.1:5000/

🗃️ Database Design
Tables Used

users → Admin credentials

student_passwords → Club passwords

requests → Reimbursement submissions

The application auto-creates missing tables at startup, ensuring safe execution even after DB reset.

🎨 UI Highlights

Clean, modern dashboard UI

Responsive tables

Long filenames handled safely

Background image + college banner on login page

Inline error messages (no page redirects)

🧪 Validation & UX

Inline login error messages

Mandatory file and field validation

Dynamic table generation based on uploaded bills

Automatic grand total calculation

Consistent PDF viewing behavior

📌 Git Best Practices Followed

.gitignore excludes:

venv/

database.db

uploads/

Clean commit history

No runtime or sensitive files tracked

🎓 Academic Use

This project is suitable for:

Mini Project

Web Development Lab

Database Management System Lab

Software Engineering Demonstration

✨ Future Enhancements

Password hashing

Role-based access decorators

Email notifications

Admin analytics dashboard

Deployment (Render / Railway / AWS)