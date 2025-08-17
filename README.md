# Timetable Generation System MVP - Computer Science Department

## Overview
This Minimum Viable Product (MVP) is designed for university-level timetable generation, specifically for the Computer Science department. Built with FastAPI, Jinja2 templates, and styled with TailwindCSS, it supports manual input or CSV/Excel upload for course details and constraints. The system uses PuLP for optimized scheduling, ensuring no back-to-back classes for lecturers, and generates a Monday–Friday timetable displayed in a responsive, animated table. It provides styled PDF exports matching the web view. The UI is enriched with a hero section, features list, and footer for a professional, visually appealing experience. Template downloads are dynamically generated for flexibility. Automation scripts (`runserver.sh` for Ubuntu, `runserver.bat` for Windows) simplify setup, package installation, server startup, and browser opening.

## Features
- **Dynamic Input**: Manual form or CSV/Excel upload with dynamically generated templates.
- **Constraints**: Start/end times, break periods, periods per day, minimum/maximum lecture durations.
- **Courses**: Computer Science courses with optional lecturers and weekly periods.
- **Optimized Scheduling**: PuLP-based optimization avoids lecturer conflicts and back-to-back classes on the same day, ensuring balanced distribution.
- **UI**: Gray + green palette with subtle animations (fade-in, hover effects, transitions), hero banner, features list, and footer.
- **Output**: Responsive timetable table and styled PDF export matching the web view.
- **Automation**: Cross-platform scripts (`runserver.sh` for Ubuntu, `runserver.bat` for Windows) to set up virtual environment, install packages, start the server, and open the browser.

## Setup Instructions
### Prerequisites
- **Python 3.8+**: Ensure Python is installed (`python3 --version` on Ubuntu, `python --version` on Windows).
- **Git**: Required for cloning the repository (`git --version`).
- **System Dependencies** (for WeasyPrint):
  - **Ubuntu**:
    ```bash
    sudo apt-get update
    sudo apt-get install -y libpango-1.0-0 libpangocairo-1.0-0 libcairo2 python3 python3-pip python3-venv xdg-utils
    ```
  - **Windows**: Install GTK3 runtime for WeasyPrint (download from [WeasyPrint docs](https://weasyprint.readthedocs.io/en/stable/install.html#windows)).

### Clone the Repository
```bash
git clone git@github.com:Levi-Chinecherem/timetable-generator.git
cd timetable-generator
```

### Running the Application
The project includes automation scripts for both Ubuntu (`runserver.sh`) and Windows (`runserver.bat`). Choose the appropriate script for your operating system.

#### Ubuntu
1. Make the script executable:
   ```bash
   chmod +x runserver.sh
   ```
2. Run the script:
   ```bash
   ./runserver.sh
   ```
   The script will:
   - Create a virtual environment (`.venv`) if it doesn’t exist, or activate the existing one.
   - Check and install missing packages from `requirements.txt`.
   - Start the Uvicorn server in the background.
   - Open `http://127.0.0.1:8000` in your default browser.
   - Keep the terminal open until you stop the server (Ctrl+C).

#### Windows
1. Run the script:
   ```cmd
   runserver.bat
   ```
   The script will:
   - Create a virtual environment (`.venv`) if it doesn’t exist, or activate the existing one.
   - Check and install missing packages from `requirements.txt`.
   - Start the Uvicorn server in a new window.
   - Open `http://127.0.0.1:8000` in your default browser.
   - Keep the server window open until you close it.

#### Manual Setup (Alternative)
If you prefer manual setup:
1. Create and activate a virtual environment:
   - **Ubuntu**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - **Windows**:
     ```cmd
     python -m venv .venv
     .venv\Scripts\activate
     ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the server:
   ```bash
   uvicorn main:app --reload
   ```
4. Open `http://127.0.0.1:8000` in your browser.

## Usage
### Manual Entry
- Select the "Manual Entry" tab.
- Enter constraints (e.g., 8:00 AM–4:00 PM, 12:00 PM–1:00 PM break, 6 periods/day, 1–2 hour duration).
- Add Computer Science courses (e.g., "Machine Learning", "Dr. Ng", 3 weekly periods) using the "Add Course" button.
- Click "Generate Timetable" to view the optimized schedule.

### File Upload
- Select the "File Upload" tab.
- Download the dynamic CSV or Excel template via the provided links.
- Fill the template with constraints and courses:
  - Row 1: Headers (`StartTime`, `EndTime`, `BreakStart`, `BreakEnd`, `PeriodsPerDay`, `MinDuration`, `MaxDuration`).
  - Row 2: Constraint values (e.g., `8:00 AM,4:00 PM,12:00 PM,1:00 PM,6,1,2`).
  - Row 3: Course headers (`Course`, `Lecturer`, `WeeklyPeriods`).
  - Row 4+: Course data (e.g., `Algorithms,Dr. Knuth,3`).
- Upload the filled file and click "Generate Timetable".

### Viewing Results
- The timetable displays with a fade-in animation in a responsive table.
- Download the styled PDF using the "Download PDF" button, which matches the web view’s gray + green styling.

### Sample CSV for Testing
```csv
StartTime,EndTime,BreakStart,BreakEnd,PeriodsPerDay,MinDuration,MaxDuration
8:00 AM,4:00 PM,12:00 PM,1:00 PM,6,1,2
Course,Lecturer,WeeklyPeriods
Algorithms,Dr. Knuth,3
Data Structures,Dr. Cormen,4
Operating Systems,Prof. Tanenbaum,3
Database Systems,Dr. Silberschatz,3
Computer Networks,Prof. Peterson,3
```

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
├── runserver.bat
├── runserver.sh
├── README.md
└── static/  # (empty, optional for custom CSS/JS)
```

## Notes
- **Time Format**: Use `H:MM AM/PM` (e.g., `8:00 AM`) for all time inputs.
- **Dynamic Templates**: CSV/Excel templates are generated dynamically from configurable defaults in `main.py`.
- **Optimization**: PuLP ensures no back-to-back lecturer classes, suitable for university-level scheduling.
- **PDF Styling**: PDFs use TailwindCSS for consistency with the web view.
- **Error Handling**: Descriptive messages for invalid inputs or infeasible schedules.
- **Cross-Platform Support**:
  - **Ubuntu**: Requires `libpango`, `libcairo`, and `xdg-utils` for WeasyPrint and browser opening.
  - **Windows**: Requires GTK3 runtime for WeasyPrint (see WeasyPrint documentation).
- **Git Setup**: Ensure SSH keys are configured for GitHub (see below for Ubuntu instructions; Windows users can follow GitHub Desktop or similar tools).

## Troubleshooting
- **Server Fails to Start**: Check terminal logs for missing dependencies or syntax errors.
- **PDF Issues**: Ensure WeasyPrint system dependencies are installed (GTK3 for Windows, `libpango`/`libcairo` for Ubuntu).
- **Browser Not Opening**:
  - **Ubuntu**: Verify `xdg-utils` is installed (`sudo apt-get install xdg-utils`).
  - **Windows**: Ensure the default browser is set correctly.
- **Package Installation Errors**: Ensure `pip` and Python 3 are installed and up-to-date.
