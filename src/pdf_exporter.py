# timetable_generator/src/pdf_exporter.py
from weasyprint import HTML

def export_to_pdf(timetable, time_slots, days):
    html_str = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>University Computer Science Timetable</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 text-gray-800 p-6">
        <h1 class="text-3xl font-bold text-green-600 mb-6">Generated University Timetable - Computer Science Department</h1>
        <div class="bg-white shadow-md rounded overflow-x-auto">
            <table class="w-full table-auto border-collapse">
                <thead>
                    <tr class="bg-green-500 text-white">
                        <th class="p-3 border">Time Slot</th>
                        {"".join(f'<th class="p-3 border">{day}</th>' for day in days)}
                    </tr>
                </thead>
                <tbody>
                    { "".join(
                        f'<tr class="hover:bg-gray-50 transition duration-200">'
                        f'<td class="p-3 border bg-gray-200 font-medium">{time_slots[i]}</td>'
                        + "".join(
                            f'<td class="p-3 border text-center">'
                            f'{timetable[i][d]["course"] if timetable[i][d] else "-"} <br>'
                            f'<span class="text-sm text-gray-600">({timetable[i][d]["lecturer"] if timetable[i][d] else ""})</span>'
                            f'</td>'
                            for d in range(len(days))
                        )
                        + '</tr>'
                        for i in range(len(time_slots))
                    ) }
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    pdf = HTML(string=html_str).write_pdf()
    return pdf