# timetable_generator/main.py
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import io
import pandas as pd
from src.parser import parse_file
from src.timetable_logic import generate_timetable
from src.pdf_exporter import export_to_pdf

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="secret-string")
templates = Jinja2Templates(directory="templates")

# Default configuration for dynamic template generation
DEFAULT_CONSTRAINTS = {
    "start_time": "8:00 AM",
    "end_time": "4:00 PM",
    "break_start": "12:00 PM",
    "break_end": "1:00 PM",
    "periods_per_day": 6,
    "min_duration": 1.0,
    "max_duration": 2.0
}
DEFAULT_COURSES = [
    {"name": "Algorithms", "lecturer": "Dr. Knuth", "weekly_periods": 3},
    {"name": "Data Structures", "lecturer": "Dr. Cormen", "weekly_periods": 4},
    {"name": "Operating Systems", "lecturer": "Prof. Tanenbaum", "weekly_periods": 3},
    {"name": "Database Systems", "lecturer": "Dr. Silberschatz", "weekly_periods": 3},
    {"name": "Computer Networks", "lecturer": "Prof. Peterson", "weekly_periods": 3}
]

def generate_csv_template():
    """Dynamically generate CSV template content."""
    csv_lines = [
        "StartTime,EndTime,BreakStart,BreakEnd,PeriodsPerDay,MinDuration,MaxDuration",
        f"{DEFAULT_CONSTRAINTS['start_time']},{DEFAULT_CONSTRAINTS['end_time']},"
        f"{DEFAULT_CONSTRAINTS['break_start']},{DEFAULT_CONSTRAINTS['break_end']},"
        f"{DEFAULT_CONSTRAINTS['periods_per_day']},{DEFAULT_CONSTRAINTS['min_duration']},"
        f"{DEFAULT_CONSTRAINTS['max_duration']}",
        "Course,Lecturer,WeeklyPeriods"
    ]
    for course in DEFAULT_COURSES:
        csv_lines.append(f"{course['name']},{course['lecturer']},{course['weekly_periods']}")
    return "\n".join(csv_lines)

def generate_excel_template():
    """Dynamically generate Excel template content."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer) as writer:
        pd.DataFrame([["StartTime", "EndTime", "BreakStart", "BreakEnd", 
                       "PeriodsPerDay", "MinDuration", "MaxDuration"]]).to_excel(
            writer, index=False, header=False, startrow=0)
        pd.DataFrame([[
            DEFAULT_CONSTRAINTS["start_time"],
            DEFAULT_CONSTRAINTS["end_time"],
            DEFAULT_CONSTRAINTS["break_start"],
            DEFAULT_CONSTRAINTS["break_end"],
            DEFAULT_CONSTRAINTS["periods_per_day"],
            DEFAULT_CONSTRAINTS["min_duration"],
            DEFAULT_CONSTRAINTS["max_duration"]
        ]]).to_excel(writer, index=False, header=False, startrow=1)
        pd.DataFrame([["Course", "Lecturer", "WeeklyPeriods"]]).to_excel(
            writer, index=False, header=False, startrow=2)
        course_data = [
            [course["name"], course["lecturer"], course["weekly_periods"]]
            for course in DEFAULT_COURSES
        ]
        pd.DataFrame(course_data).to_excel(writer, index=False, header=False, startrow=3)
    buffer.seek(0)
    return buffer.getvalue()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "error": None})

@app.post("/generate", response_class=HTMLResponse)
async def generate(request: Request, input_type: str = Form(...)):
    error = None
    courses = []
    constraints = {}
    form_data = await request.form()
    if input_type == "manual":
        try:
            constraints = {
                "start_time": form_data["start_time"],
                "end_time": form_data["end_time"],
                "break_start": form_data["break_start"],
                "break_end": form_data["break_end"],
                "periods_per_day": int(form_data["periods_per_day"]),
                "min_duration": float(form_data["min_duration"]),
                "max_duration": float(form_data["max_duration"]),
            }
            course_names = form_data.getlist("course_name[]")
            lecturers = form_data.getlist("lecturer[]")
            weekly_periods = form_data.getlist("weekly_periods[]")
            if len(course_names) != len(lecturers) or len(course_names) != len(weekly_periods):
                raise ValueError("Mismatch in course inputs.")
            for name, lecturer, wp in zip(course_names, lecturers, weekly_periods):
                if not name or not wp:
                    raise ValueError("Course name and weekly periods are required.")
                courses.append({
                    "name": name,
                    "lecturer": lecturer,
                    "weekly_periods": int(wp)
                })
        except Exception as e:
            error = f"Invalid input data: {str(e)}. Please check all fields."
    elif input_type == "upload":
        file = form_data["file"]
        if file.filename == "":
            error = "No file uploaded."
        else:
            try:
                constraints, courses = await parse_file(file)
            except Exception as e:
                error = f"File processing error: {str(e)}"
    if error:
        return templates.TemplateResponse("index.html", {"request": request, "error": error})

    total_required = sum(c["weekly_periods"] for c in courses)
    total_available = 5 * constraints["periods_per_day"]
    if total_required > total_available:
        error = f"Not enough slots available ({total_required} periods required, {total_available} available)."
    if error:
        return templates.TemplateResponse("index.html", {"request": request, "error": error})

    try:
        timetable, time_slots = generate_timetable(constraints, courses)
        request.session["timetable"] = timetable
        request.session["time_slots"] = time_slots
        return templates.TemplateResponse("result.html", {
            "request": request,
            "timetable": timetable,
            "time_slots": time_slots,
            "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "department": "Computer Science"
        })
    except Exception as e:
        error = f"Timetable generation failed: {str(e)}"
        return templates.TemplateResponse("index.html", {"request": request, "error": error})

@app.get("/download_template")
def download_template():
    csv_content = generate_csv_template()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=template.csv"}
    )

@app.get("/download_template_excel")
def download_template_excel():
    excel_content = generate_excel_template()
    return Response(
        content=excel_content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=template.xlsx"}
    )

@app.get("/download_pdf")
def download_pdf(request: Request):
    timetable = request.session.get("timetable")
    time_slots = request.session.get("time_slots")
    if not timetable or not time_slots:
        return "No timetable generated."
    pdf_bytes = export_to_pdf(timetable, time_slots, ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=timetable.pdf"}
    )