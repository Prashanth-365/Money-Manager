import gspread
from oauth2client.service_account import ServiceAccountCredentials
from macro_functions import insert_delete_data, add_new_month

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


def initiate_sheet(spread_sheet, sheet_name):
    # Open the Google Sheet by its name
    spreadsheet = client.open(spread_sheet)  # Replace with your sheet name
    return spreadsheet.worksheet(sheet_name)


def find(web_app_url, spread_sheet, sheet_name, date):
    date_val = f"date : {date}"
    sheet = initiate_sheet(spread_sheet, sheet_name)
    try:
        cell = sheet.find(date_val)
        if cell:
            return cell.row, cell.col  # Returns the cell object if found
    except Exception as e:
        print(e)
        print(web_app_url, sheet_name, date)
        add_new_month(web_app_url, sheet_name, date)
        find(web_app_url, spread_sheet, sheet_name, date)  # Return None if the value is not found



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
