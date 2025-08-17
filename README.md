
# Automatic Timetable Generation System MVP

## Overview
This is a Minimum Viable Product (MVP) for an automatic timetable generation system built with FastAPI, Jinja2 templates, and styled with TailwindCSS. It supports manual input or CSV/Excel upload for course details and constraints, generates a weekly timetable (Monday-Friday), displays it in a responsive table with animations, and allows PDF download.

## Features
- **Input Methods**: Manual form or CSV/Excel upload using a template.
- **Constraints**: Start/end times, break period, periods per day, min/max lecture duration.
- **Courses**: Name, optional lecturer, weekly periods (added for functionality).
- **Generation**: Distributes periods evenly, avoids back-to-back classes for the same lecturer on the same day.
- **UI**: Gray + green palette, subtle animations (fade-in, hover effects, transitions).
- **Output**: Responsive table, PDF export.

## Setup Instructions
1. Clone the repository or create the project structure as specified.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   Note: WeasyPrint may require additional system dependencies (e.g., `libpango` on Linux).

3. Run the server:
   ```
   uvicorn main:app --reload
   ```
   Access at `http://localhost:8000`.

## Usage
### Manual Entry
- Select "Manual Entry" tab.
- Fill in timetable constraints (times, periods, durations).
- Add courses (name, lecturer, weekly periods) using the "Add Course" button.
- Submit to generate the timetable.

### File Upload
- Select "File Upload" tab.
- Download the template (CSV or Excel).
- Fill the template:
  - Row 1: Headers (StartTime, EndTime, etc.).
  - Row 2: Constraint values.
  - Row 3: Course headers.
  - Row 4+: Course data.
- Upload the filled file and submit.

### Viewing Results
- Timetable displays with fade-in animation.
- Download PDF via the button.

## Project Structure
```
timetable_generator/
├── templates/
│   ├── index.html
│   └── result.html
├── uploads/  # (runtime, optional)
├── generated/  # (runtime, optional)
├── src/
│   ├── parser.py
│   ├── timetable_logic.py
│   ├── pdf_exporter.py
├── main.py
├── requirements.txt
├── README.md
└── static/  # (empty, optional for custom CSS/JS)
```

## Notes
- Times must be in "H:MM AM/PM" format.
- The system shuffles assignments randomly but checks for no back-to-back lecturer classes.
- For production, add more robust error handling and security.
- No persistent storage; sessions used for PDF download.
