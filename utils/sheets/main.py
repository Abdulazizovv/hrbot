from utils.sheets import get_google_sheet
from datetime import datetime

def write_to_google_sheet(user_id, step, data):
    try:
        sheet = get_google_sheet()
        all_values = sheet.get_all_values()
    except Exception as e:
        print(f"Error accessing Google Sheet: {e}")
        return False

    row_num = None

    # Find last row for user_id
    for i in reversed(range(len(all_values))):
        row = all_values[i]
        if row and row[0] == str(user_id):
            last_status = row[13] if len(row) > 13 else ''  # Status is in 12th col (index 11)
            print(f"Last status for user {user_id}: {last_status}")
            if last_status in ['Vazifa bajarildi', 'Tasdiqlandi', 'Bekor qilindi']:
            # if not last_status or not last_status == "Yangi":
                row_num = None
            else:
                row_num = i + 1  # gspread is 1-indexed
            break

    # If no row or completed, insert new row with blank values (up to 13 columns)
    if row_num is None:
        row_num = len(all_values) + 1
        sheet.insert_row([str(user_id)] + [''] * 12, row_num)  # 13 columns total

    # Map step to column index
    step_to_col = {
        'start': 1,
        'vacancy': 2,
        'name': 3,
        'phone': 4,
        'age': 5,
        'portfolio': 6,
        'about': 7,
        'task': 8,
        'select_deadline': 9,
        'deadline': 10,
        'task_start': 11,
        'task_end': 12,
        'status': 13,
        'timestamp': 14,
        'task_link': 15,
    }

    col = step_to_col.get(step)
    if col:
        # If step is 'timestamp', use current time
        if step == 'timestamp' and not data:
            data = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            sheet.update_cell(row_num, col, data)
        except Exception as e:
            print(f"Error updating cell at row {row_num}, col {col}: {e}")
            return False
        return True

    print(f"Invalid step: {step}")
    return False
