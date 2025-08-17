# timetable_generator/src/parser.py
import csv
import io
import pandas as pd
from fastapi import UploadFile  # Add this import

async def parse_file(file: UploadFile):
    content = await file.read()
    filename = file.filename
    constraints = {}
    courses = []
    if filename.endswith('.csv'):
        text = content.decode('utf-8')
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)
        if len(rows) < 3:
            raise ValueError("Invalid file format.")
        header = rows[0]
        if header != ['StartTime', 'EndTime', 'BreakStart', 'BreakEnd', 'PeriodsPerDay', 'MinDuration', 'MaxDuration']:
            raise ValueError("Invalid constraints header.")
        cons_row = rows[1]
        constraints = {
            "start_time": cons_row[0],
            "end_time": cons_row[1],
            "break_start": cons_row[2],
            "break_end": cons_row[3],
            "periods_per_day": int(cons_row[4]),
            "min_duration": float(cons_row[5]),
            "max_duration": float(cons_row[6]),
        }
        if rows[2] != ['Course', 'Lecturer', 'WeeklyPeriods']:
            raise ValueError("Invalid courses header.")
        for row in rows[3:]:
            if row and len(row) >= 3:
                courses.append({
                    "name": row[0],
                    "lecturer": row[1],
                    "weekly_periods": int(row[2])
                })
    elif filename.endswith('.xlsx'):
        df = pd.read_excel(io.BytesIO(content), header=None)
        if df.shape[0] < 4:
            raise ValueError("Invalid file format.")
        cons_row = df.iloc[1]
        constraints = {
            "start_time": str(cons_row[0]),
            "end_time": str(cons_row[1]),
            "break_start": str(cons_row[2]),
            "break_end": str(cons_row[3]),
            "periods_per_day": int(cons_row[4]),
            "min_duration": float(cons_row[5]),
            "max_duration": float(cons_row[6]),
        }
        courses_df = df.iloc[3:]
        for _, row in courses_df.iterrows():
            if pd.notna(row[0]):
                courses.append({
                    "name": str(row[0]),
                    "lecturer": str(row[1]) if pd.notna(row[1]) else "",
                    "weekly_periods": int(row[2])
                })
    else:
        raise ValueError("Unsupported file type. Use CSV or XLSX.")
    if not courses:
        raise ValueError("No courses found in file.")
    return constraints, courses