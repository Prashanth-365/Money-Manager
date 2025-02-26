import gspread
from oauth2client.service_account import ServiceAccountCredentials
from macro_functions import insert_delete_data, add_new_month

from gspread.exceptions import SpreadsheetNotFound, WorksheetNotFound
# Define the scope for Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Add your JSON key file
creds = ServiceAccountCredentials.from_json_keyfile_name("google_creds.json", scope)

# Authorize the client
client = gspread.authorize(creds)


def col_idx(col):
    col = col.upper()  # Convert to uppercase to handle lowercase inputs
    index = 0
    for char in col:
        index = index * 26 + (ord(char) - ord('A') + 1)
    return index


def initiate_sheet(spread_sheet, sheet_name, rows=100, cols=20):
    try:
        # Try to open the spreadsheet
        spreadsheet = client.open(spread_sheet)
        print(f"Spreadsheet '{spread_sheet}' found.")
    except SpreadsheetNotFound:
        print(f"Spreadsheet '{spread_sheet}' not found. Creating a new spreadsheet.")
        spreadsheet = client.create(spread_sheet)
        # Share the sheet if needed (e.g., to a specific email)
        spreadsheet.share('your_email@example.com', perm_type='user', role='writer')

    try:
        # Try to get the worksheet
        sheet = spreadsheet.worksheet(sheet_name)
        print(f"Worksheet '{sheet_name}' found.")
    except WorksheetNotFound:
        print(f"Worksheet '{sheet_name}' not found. Creating a new worksheet.")
        sheet = spreadsheet.add_worksheet(title=sheet_name, rows=str(rows), cols=str(cols))

    return sheet


def find(web_app_url, spread_sheet, sheet_name, date):
    date_val = f"date : {date}"
    sheet = initiate_sheet(spread_sheet, sheet_name)
    try:
        cell = sheet.find(date_val)
        if cell:
            return cell.row, cell.col  # ✅ Return row and column if found
    except Exception as e:
        print(f"Error finding date {date}: {e}")
        print(web_app_url, sheet_name, date)

    # If the date is not found, try adding a new month
    add_new_month(web_app_url, sheet_name, date)

    # Try finding again
    result = find(web_app_url, spread_sheet, sheet_name, date)
    return result if result else (None, None)  # ✅ Ensure it always returns (row, col)


def add_transaction(web_app_url, spread_sheet, sheet_name, data):
    start = 5
    date = data[1][:7]
    row, col = find(web_app_url, spread_sheet, sheet_name, date)
    lst = get_values(spread_sheet, sheet_name, "col", col - 1, start, row - 1)
    r = 0
    # find on which row to insert data based on slno(combination of date and time)
    for i, a in enumerate(lst):
        if int(data[0]) >= int(a):
            r = i
            break
        r = len(lst)
    updated_row = start + r
    print(updated_row)
    insert_delete_data(web_app_url, sheet_name, "insert", updated_row, col - 1, data)


def get_values(spread_sheet, sheet_name, type, val, start, end):
    sheet = initiate_sheet(spread_sheet, sheet_name)
    if type == "row":
        result = sheet.row_values(val)[start - 1:end]
    elif type == "col":
        result = sheet.col_values(val)[start - 1:end]
    return result


if __name__ == "__main__":
    pass

    # values = ["", "202501061816", "2025-01-09", "18:16", "165451315461", "My Self", "Banu R", "Sample Description", ""
    # , "5000"]
    # insert_values_in_between("Transaction Datasheet - Prashanth", "Sheet1", 5, 2, values)
