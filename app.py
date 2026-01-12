from flask import Flask, render_template, request, redirect, session, send_from_directory
import sqlite3, os, json
from werkzeug.utils import secure_filename
from openpyxl import Workbook
from flask import send_file
import io
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle,
    Spacer, Image
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib import colors


import pdfkit
from flask import make_response

import inflect
import io


app = Flask(__name__)
app.secret_key = "secret123"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
BILL_FOLDER = os.path.join(UPLOAD_FOLDER, "bills")
PASSBOOK_FOLDER = os.path.join(UPLOAD_FOLDER, "passbooks")

os.makedirs(BILL_FOLDER, exist_ok=True)
os.makedirs(PASSBOOK_FOLDER, exist_ok=True)

def init_db():
    db = get_db()
    cur = db.cursor()

    # Admin table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )
    """)

    # Student club passwords
    cur.execute("""
    CREATE TABLE IF NOT EXISTS student_passwords (
        club_name TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )
    """)

    # Requests table (THIS FIXES YOUR ERROR)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        bill TEXT,
        passbook TEXT,
        table_data TEXT,
        status TEXT DEFAULT 'PENDING'
    )
    """)

    db.commit()

# ---------------- DB CONNECTION ----------------
def get_db():
    return sqlite3.connect(DB_PATH)



def number_to_words(n):
    
    p = inflect.engine()
    return p.number_to_words(n).replace("-", " ").title()

# ---------------- LOGIN ----------------
@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    role = request.form["role"]
    userid = request.form["userid"]
    password = request.form["password"]

    db = get_db()
    cur = db.cursor()

    # ---------- ADMIN LOGIN ----------
    if role == "admin":
        if userid != "admin":
            return render_template(
                "login.html",
                error="Invalid admin user ID"
            )

        cur.execute("SELECT password FROM users WHERE username='admin'")
        row = cur.fetchone()

        if row and row[0] == password:
            session["role"] = "admin"
            session["user"] = "admin"
            return redirect("/admin")
        else:
            return render_template(
                "login.html",
                error="Invalid admin password"
            )

    # ---------- STUDENT LOGIN ----------
    if role == "student":
        if userid != "student":
            return render_template(
                "login.html",
                error="Invalid student user ID"
            )

        cur.execute(
            "SELECT club_name FROM student_passwords WHERE password=?",
            (password,)
        )
        row = cur.fetchone()

        if row:
            session["role"] = "student"
            session["user"] = row[0]
            return redirect("/student")
        else:
            return render_template(
                "login.html",
                error="Invalid student password"
            )

    return render_template(
        "login.html",
        error="Invalid login attempt"
    )


# ---------------- STUDENT ----------------
@app.route("/student")
def student():
    if session.get("role") != "student":
        return redirect("/")
    return render_template("student.html")

@app.route("/submit", methods=["POST"])
def submit():

    if session.get("role") != "student":
        return redirect("/")

    # 🔹 MULTIPLE BILLS
    bills = request.files.getlist("bills")
    if not bills or bills[0].filename == "":
        return "No bills uploaded", 400

    bill_paths = []
    for bill in bills:
        filename = secure_filename(bill.filename)
        path = f"uploads/bills/{filename}"
        bill.save(os.path.join(BASE_DIR, path))
        bill_paths.append(path)

    # 🔹 PASSBOOK
    passbook = request.files["passbook"]
    pb_name = secure_filename(passbook.filename)
    pb_path = f"uploads/passbooks/{pb_name}"
    passbook.save(os.path.join(BASE_DIR, pb_path))

    # 🔹 TABLE DATA
    table_data = request.form["tableData"]

    # 🔹 SAVE TO DB
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        INSERT INTO requests (student_id, bill, passbook, table_data, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        session["user"],
        json.dumps(bill_paths),   # IMPORTANT: list of bills
        pb_path,
        table_data,
        "PENDING"
    ))
    db.commit()
    db.close()

    return render_template("success.html")


@app.route("/student/status")
def student_status():
    if session.get("role") != "student":
        return redirect("/")

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT id, status FROM requests WHERE student_id=?",
        (session["user"],)
    )
    requests = cur.fetchall()
    db.close()

    return render_template("student_status.html", requests=requests)

@app.route("/student/download/<int:req_id>")
def student_download(req_id):
    if session.get("role") != "student":
        return redirect("/")

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT table_data FROM requests WHERE id=?", (req_id,))
    data = json.loads(cur.fetchone()[0])
    db.close()

    return generate_excel(data, f"student_request_{req_id}.xlsx")




    db = get_db()
    cur = db.cursor()
    cur.execute("""
        INSERT INTO requests (student_id, bill, passbook, table_data, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        session["user"],
        bill_path,
        passbook_path,
        table_data,
        "PENDING"
    ))
    db.commit()
    db.close()

    return "Submitted Successfully! <br><a href='/student'>Go Back</a>"

# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect("/")

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM requests")
    data = cur.fetchall()
    db.close()

    return render_template("admin.html", data=data)

# ---------------- CONSOLIDATED VIEW ----------------
@app.route("/admin/request/<int:req_id>")
def admin_view(req_id):
    if session.get("role") != "admin":
        return redirect("/")

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM requests WHERE id=?", (req_id,))
    r = cur.fetchone()
    db.close()

    table_json = json.loads(r[4])   # FULL table data
    bill_list = json.loads(r[2])    # list of bill PDFs

    return render_template(
        "admin_view.html",
        request_data=r,
        bills=bill_list,
        table_data=table_json
    )


# ---------------- APPROVE / DISAPPROVE ----------------
@app.route("/update/<int:req_id>/<status>")
def update(req_id, status):
    if session.get("role") != "admin":
        return redirect("/")

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "UPDATE requests SET status=? WHERE id=?",
        (status, req_id)
    )
    db.commit()
    db.close()

    return redirect("/admin")

@app.route("/admin/download/<int:req_id>")
def admin_download(req_id):
    if session.get("role") != "admin":
        return redirect("/")

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT table_data FROM requests WHERE id=?", (req_id,))
    data = json.loads(cur.fetchone()[0])
    db.close()

    return generate_excel(data, f"admin_request_{req_id}.xlsx")

def generate_excel(table_json, filename):
    wb = Workbook()
    ws = wb.active
    ws.title = "Reimbursement"

    headers = [
        "S. No",
        "Description",
        "Bill Amount",
        "To Pay Amount",
        "Name & Bank Acc. No.",
        "IFSC Code",
        "Branch"
    ]
    ws.append(headers)

    rows = table_json.get("rows", [])
    if not rows:
        return

    start_row = 2  # first data row
    for r in rows:
        ws.append(r)

    end_row = start_row + len(rows) - 1

    # 🔥 MERGE COLUMNS (VERTICALLY)
    ws.merge_cells(start_row=start_row, start_column=4,
                   end_row=end_row, end_column=4)

    ws.merge_cells(start_row=start_row, start_column=5,
                   end_row=end_row, end_column=5)

    ws.merge_cells(start_row=start_row, start_column=6,
                   end_row=end_row, end_column=6)

    ws.merge_cells(start_row=start_row, start_column=7,
                   end_row=end_row, end_column=7)

    # Center align merged cells
    from openpyxl.styles import Alignment
    for col in [4, 5, 6, 7]:
        ws.cell(row=start_row, column=col).alignment = Alignment(
            vertical="center", horizontal="center"
        )

    file_stream = io.BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    return send_file(
        file_stream,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route("/admin/generate-letter", methods=["POST"])
def generate_letter():
    if session.get("role") != "admin":
        return redirect("/")

    subject = request.form["subject"]
    date_raw = request.form["letter_date"]
    y, m, d = date_raw.split("-")
    letter_date = f"{d}-{m}-{y}"

    request_ids = request.form.getlist("request_ids")

    db = get_db()
    cur = db.cursor()

    grouped_data = []   # 🔥 each request stays separate
    grand_total = 0

    for rid in request_ids:
        cur.execute(
            "SELECT table_data FROM requests WHERE id=?",
            (rid,)
        )
        table_json = json.loads(cur.fetchone()[0])

        rows = table_json["rows"]

        to_pay = rows[0][3]
        bank = rows[0][4]
        ifsc = rows[0][5]
        branch = rows[0][6]

        subtotal = sum(float(r[2]) for r in rows)
        grand_total += subtotal

        grouped_data.append({
            "rows": rows,
            "to_pay": to_pay,
            "bank": bank,
            "ifsc": ifsc,
            "branch": branch,
            "subtotal": subtotal
        })

    db.close()

    session["letter_data"] = {
    "subject": subject,
    "letter_date": letter_date,
    "groups": grouped_data,
    "total": grand_total,
    "total_words": number_to_words(int(grand_total))
}
    session["letter_subject"] = subject
    session["letter_date"] = letter_date
    session["letter_groups"] = grouped_data
    session["letter_total"] = grand_total
    session["letter_total_words"] = number_to_words(int(grand_total))


    
    return render_template(
    "letter.html",
    subject=subject,
    letter_date=letter_date,
    groups=grouped_data,
    total=grand_total,
    total_words=number_to_words(int(grand_total))
)







def generate_letter_pdf(subject, letter_date, groups, total, total_words):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    content = []

    # ================= HEADER =================
    logo = Image("static/images/psg_logo.png", width=55, height=55)

    title_style = ParagraphStyle(
        "title",
        parent=styles["Normal"],
        fontSize=13,
        leading=16,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold"
    )

    header = Table(
        [[
            logo,
            Paragraph(
                "PSG INSTITUTE OF TECHNOLOGY AND APPLIED RESEARCH<br/>"
                "STUDENT COUNCIL",
                title_style
            ),
            Paragraph(f"<b>Date:</b> {letter_date}", styles["Normal"])
        ]],
        colWidths=[70, 330, 115]
    )

    header.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN", (2,0), (2,0), "RIGHT"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
    ]))

    content.append(header)
    content.append(Spacer(1, 15))

    # ================= BODY =================
    content.append(Paragraph("<b>Submitted to Principal:</b>", styles["Normal"]))
    content.append(Spacer(1, 6))
    content.append(Paragraph(f"<b>Sub:</b> {subject}", styles["Normal"]))
    content.append(Spacer(1, 10))

    content.append(Paragraph(
        "Principal’s kind permission is requested to settle the list of bills given below. "
        "Photocopy of the bills are enclosed for your kind perusal.",
        styles["Normal"]
    ))

    content.append(Spacer(1, 15))

    cell_style = ParagraphStyle(
     "cell",
      parent=styles["Normal"],
      fontSize=9,
      leading=11,
      alignment=TA_CENTER
    )

    header_style = ParagraphStyle(
      "header",
       parent=styles["Normal"],
       fontSize=9,
       leading=11,
       alignment=TA_CENTER,
       fontName="Helvetica-Bold"
    )


    # ================= TABLE =================
    table_data = [[
     Paragraph("S. No", header_style),
     Paragraph("Description", header_style),
     Paragraph("Bill Amount", header_style),
     Paragraph("To Pay Amount", header_style),
     Paragraph("Name & Bank Acc. No.", header_style),
     Paragraph("IFSC Code", header_style),
     Paragraph("Branch", header_style),
    ]]


    style_cmds = [
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("FONT", (0,0), (-1,0), "Helvetica-Bold"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN", (2,1), (-1,-1), "CENTER"),
    ]

    row_index = 1
    sno = 1

    for g in groups:
      start = row_index
      first = True

      for r in g["rows"]:
        table_data.append([
            Paragraph(str(sno), cell_style),
            Paragraph(str(r[1]), cell_style),
            Paragraph(str(r[2]), cell_style),
            Paragraph(str(g["to_pay"]) if first else "", cell_style),
            Paragraph(str(g["bank"]) if first else "", cell_style),
            Paragraph(str(g["ifsc"]) if first else "", cell_style),
            Paragraph(str(g["branch"]) if first else "", cell_style),
        ])
        first = False
        
        row_index += 1

      end = row_index - 1

      style_cmds += [
        ("SPAN", (0, start), (0, end)),  # ✅ S. No
        ("SPAN", (3, start), (3, end)),
        ("SPAN", (4, start), (4, end)),
        ("SPAN", (5, start), (5, end)),
        ("SPAN", (6, start), (6, end)),
        ]

      sno += 1

    # ================= TOTAL ROW =================
    table_data.append([
      Paragraph("", cell_style),
      Paragraph("Total", header_style),
      Paragraph("", cell_style),
      Paragraph("", cell_style),
      Paragraph(f"{total} ({total_words} Only)", header_style),
      Paragraph("", cell_style),
      Paragraph("", cell_style),
   ])


    style_cmds += [
      ("SPAN", (0, row_index), (1, row_index)),
      ("SPAN", (4, row_index), (6, row_index)),
      ("ALIGN", (4, row_index), (6, row_index), "CENTER"),
    ]


    table = Table(
        table_data,
        colWidths=[35, 110, 65, 70, 140, 55, 40],  # ✅ fits A4 margins
        repeatRows=1
    )

    table.setStyle(TableStyle(style_cmds))
    content.append(table)

    content.append(Spacer(1, 40))

    # ================= FOOTER =================
    footer = Table(
        [["Faculty Advisor – Student Council", "Principal"]],
        colWidths=[250, 250]
    )

    footer.setStyle(TableStyle([
        ("ALIGN", (0,0), (0,0), "LEFT"),
        ("ALIGN", (1,0), (1,0), "RIGHT"),
    ]))

    content.append(footer)

    doc.build(content)
    buffer.seek(0)
    return buffer



@app.route("/admin/letter/download")
def download_letter():
    if session.get("role") != "admin":
        return redirect("/")

    buffer = generate_letter_pdf(
        session["letter_subject"],
        session["letter_date"],
        session["letter_groups"],
        session["letter_total"],
        session["letter_total_words"]
    )

    return send_file(
        buffer,
        as_attachment=True,
        download_name="Official_Letter.pdf",
        mimetype="application/pdf"
    )

# ---------------- FILE SERVING ----------------
@app.route("/files/<path:filepath>")
def serve_file(filepath):
    return send_from_directory(BASE_DIR, filepath)


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

with app.app_context():
    init_db()

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
