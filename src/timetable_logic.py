# timetable_generator/src/timetable_logic.py
from datetime import datetime, timedelta
import random
import pulp
from itertools import combinations
from collections import defaultdict

def parse_time(t_str):
    try:
        return datetime.strptime(t_str, "%I:%M %p").time()
    except ValueError:
        raise ValueError(f"Invalid time format: {t_str}. Use e.g., '8:00 AM'.")

def generate_timetable(constraints, courses):
    start = parse_time(constraints["start_time"])
    end = parse_time(constraints["end_time"])
    break_start = parse_time(constraints["break_start"])
    break_end = parse_time(constraints["break_end"])
    periods = constraints["periods_per_day"]
    min_d = constraints["min_duration"]
    max_d = constraints["max_duration"]

    base_date = datetime(2000, 1, 1)
    start_dt = datetime.combine(base_date, start)
    end_dt = datetime.combine(base_date, end)
    break_start_dt = datetime.combine(base_date, break_start)
    break_end_dt = datetime.combine(base_date, break_end)

    if break_start_dt >= break_end_dt or start_dt >= end_dt:
        raise ValueError("Invalid time ranges.")

    break_duration = (break_end_dt - break_start_dt).total_seconds() / 3600.0
    total_time = (end_dt - start_dt).total_seconds() / 3600.0 - break_duration
    if total_time <= 0:
        raise ValueError("No available time after break.")

    duration = total_time / periods
    if not (min_d <= duration <= max_d):
        raise ValueError(f"Lecture duration {duration:.2f} hours is outside min/max range ({min_d}-{max_d}).")

    # Generate time slots
    current = start_dt
    time_slots = []
    for _ in range(periods):
        if break_start_dt <= current < break_end_dt:
            current = break_end_dt
        slot_start = current
        slot_end = current + timedelta(hours=duration)
        if slot_end > end_dt:
            raise ValueError("Slots exceed end time.")
        time_slots.append(f"{slot_start.strftime('%I:%M %p')} - {slot_end.strftime('%I:%M %p')}")
        current = slot_end

    # Collect periods (sessions)
    periods_list = []
    for c in courses:
        for _ in range(c["weekly_periods"]):
            periods_list.append({"course": c["name"], "lecturer": c["lecturer"] or "N/A"})

    if not periods_list:
        raise ValueError("No periods to schedule.")

    # Use PuLP for scheduling
    problem = pulp.LpProblem("University_Timetable", pulp.LpMinimize)

    days_range = range(5)
    times_range = range(len(time_slots))
    sessions = range(len(periods_list))

    # Map sessions to lecturers
    lect_to_sessions = defaultdict(list)
    for s in sessions:
        lect = periods_list[s]["lecturer"]
        lect_to_sessions[lect].append(s)

    # Variables: x[session, day, time_slot]
    x = pulp.LpVariable.dicts("x", (sessions, days_range, times_range), 0, 1, pulp.LpBinary)

    # Each session assigned exactly once
    for s in sessions:
        problem += pulp.lpSum(x[s][d][t] for d in days_range for t in times_range) == 1

    # At most one session per slot (day, time)
    for d in days_range:
        for t in times_range:
            problem += pulp.lpSum(x[s][d][t] for s in sessions) <= 1

    # No back-to-back for same lecturer on same day
    for lect, ss in lect_to_sessions.items():
        if len(ss) < 2:
            continue
        for pair in combinations(ss, 2):
            s1, s2 = pair
            for d in days_range:
                for t in range(len(times_range) - 1):
                    problem += x[s1][d][t] + x[s2][d][t + 1] <= 1
                    problem += x[s2][d][t] + x[s1][d][t + 1] <= 1

    # Solve
    status = problem.solve(pulp.PULP_CBC_CMD(msg=0))
    if pulp.LpStatus[status] != 'Optimal':
        raise ValueError("Could not generate timetable satisfying constraints.")

    # Build grid [time][day]
    grid = [[None for _ in days_range] for _ in times_range]
    for s in sessions:
        for d in days_range:
            for t in times_range:
                if x[s][d][t].value() == 1:
                    grid[t][d] = periods_list[s]

    return grid, time_slots