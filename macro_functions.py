import requests
import json


def num_to_letter(col_num):
    """Convert a column number to an Excel-style column letter."""
    col_letter = ""
    while col_num > 0:
        col_num, remainder = divmod(col_num - 1, 26)
        col_letter = chr(65 + remainder) + col_letter
    return col_letter


def letter_to_num(col_letter):
    """Convert Excel-style column letter to a number."""
    col_num = 0
    for char in col_letter:
        col_num = col_num * 26 + (ord(char) - ord('A') + 1)
    return col_num


def get_cell_range(row, col, length):
    """Convert row and column numbers to a spreadsheet cell name."""
    if not isinstance(col, int):
        col = letter_to_num(col.upper())  # Convert letter to number
    col_start = num_to_letter(col)
    col_end = num_to_letter(col + length - 1)

    return f"{col_start}{row}:{col_end}{row}"


def add_new_month(web_app_url, sheet_name, month):
    params = {'function_name': "add new month", 'sheet_name': sheet_name, 'month': month}
    call_macro_fn(web_app_url, params)


def call_macro_fn(web_app_url, function_params):
    try:
        response = requests.get(web_app_url, params=function_params)
        response.raise_for_status()  # Raises an error for bad HTTP responses (4xx or 5xx)

        print("Response Status Code:", response.status_code)  # Debugging
        print("Response Text:", response.text)  # Print the actual response

        return response.text  # Return the actual response from the web app

    except requests.exceptions.RequestException as e:
        print(f"Error calling web app: {e}")
        return f"Error calling web app: {e}"


def insert_delete_data(web_app_url, sheet_name, operation, row, col, values):
    cell_range = [get_cell_range(row, col, len(values)), get_cell_range(row, col, len(values) + 1)]
    print(cell_range)
    params = {'sheet_name': sheet_name, 'range': json.dumps(cell_range), "values": json.dumps(values)}
    if operation == "insert":
        params["function_name"] = "insert cells"
    elif operation == "delete":
        params["function_name"] = "delete cells"
    call_macro_fn(web_app_url, params)


if __name__ == "__main__":
    # Trigger macro
    # add_new_month("Sheet1", "02/2025")
    values = ["202501061816", "2025-01-09", "18:16", "165451315461", "Banu R", "", "", "", "5000"]
    row = 5
    col = "b"

    web_app_url = "https://script.google.com/macros/s/AKfycbyfDk_AXKgGzpVQR9z7J9i0xPsn8sNG0lY0byeP5ZhP6ZyagcLkq-o5TsCLFfj4tp-i/exec"
    values = ['121516', '2025-02-12', '15:16', '503989807114', 'Harsha', 'College', 'Report', '456']
    add_new_month(web_app_url, "KBL-Prashanth", "2025-02")
