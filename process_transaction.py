import re
import json
from sheet_operations import initiate_sheet, add_transaction, get_values
from macro_functions import insert_delete_data

debit = ["debited", "sent"]
credit = ["credited", "received"]


def get_user_data():
    with open("Database/User_data/users.json", "r") as file:
        return json.load(file)


def creds_from_user_id(user_id):
    credentials = {}
    user_data = get_user_data()
    for name, values in user_data.items():
        if user_id == values["user_id"]:
            credentials["account_holder"] = name
            credentials["web_app_url"] = values["web_app_url"]
    return credentials


def creds_from_ac_no(ac_no):
    credentials = {}
    user_data = get_user_data()
    for name, values in user_data.items():
        if ac_no in values["accounts"].keys():
            credentials["account_holder"] = name
            credentials["user_id"] = values["user_id"]
            credentials["web_app_url"] = values["web_app_url"]
    return credentials


def spread_sheet_names(account_holder, bank_name, sub_user):
    spread_sheet = f"Transaction Datasheet - {account_holder}"
    sheet_name = f"{bank_name}-{sub_user}"
    return spread_sheet, sheet_name


def get_pending_transaction(spread_sheet):
    return get_values(spread_sheet, "Pending Transactions", "row", 5, 2, 9)


def message_data(message):
    message = message.replace("from kotak bank", "")
    new_txn = {}
    try:
        # print(f"Processing message: {message}")  # Debugging step

        account_match = re.search(r'x+(\d+)', message)
        date_match = re.search(r'date: (\d+)', message)
        time_match = re.search(r'time: (\d+)', message)
        txn_id_match = re.search(r'(?:upi|ref|ref no|upi ref)\s*[: ]\s*(\d+)', message)
        txn_type_match = re.search(r'(debited|credited|sent|received)', message)
        amount_match = re.search(r'rs\.(\d+\.\d{2})', message)
        name_match = re.search(r'(?:to|from)\s([\w@.]+)', message)

        if not all([account_match, date_match, time_match, txn_id_match, txn_type_match, amount_match, name_match]):
            raise ValueError("One or more regex patterns did not match.")

        account_number = account_match.group(1)
        date = date_match.group(1)
        time = time_match.group(1)
        transaction_id = txn_id_match.group(1)
        transaction_type = txn_type_match.group(1).lower()
        amount = amount_match.group(1)
        name = name_match.group(1).strip()

        new_txn["date"] = date
        new_txn["time"] = time
        new_txn["txn ID"] = transaction_id
        new_txn["name"] = f'{name}'

        if transaction_type in debit:
            new_txn["debit"] = f'{amount}'
            new_txn["credit"] = ""
        elif transaction_type in credit:
            new_txn["debit"] = ""
            new_txn["credit"] = f'{amount}'

        print(f"Extracted data: {new_txn}, Account Number: {account_number}")
        return new_txn, account_number

    except Exception as e:
        print(f"Error in message_data: {e}")
        return None, None


def calculate_balance(df):
    for i in range(1, len(df["balance"]) + 1):
        bal = df["credit"].iloc[:i].sum() - df["debit"].iloc[:i].sum()
        df.loc[df.index[i - 1], "balance"] = round(bal, 2)
    return df


def process(sms_text):
    try:
        sms_text = f"{sms_text}".lower()
        new_txn, ac_no = message_data(sms_text)
        if new_txn is None or ac_no is None:
            return None
        creds = creds_from_ac_no(ac_no)
        slno = new_txn["date"][-2:] + new_txn["time"]
        date = new_txn["date"]
        time = new_txn["time"]
        data = [ac_no, slno, date, time, new_txn["txn ID"], new_txn["name"], new_txn["debit"], new_txn["credit"]]
        insert_delete_data(creds["web_app_url"], "Pending Transactions", "insert", 5, "b", data)
        print(f"Data to insert: {data}")
        return creds["user_id"]
    except Exception as e:
        print(f"Error in process: {e}")
        return None


if __name__ == "__main__":
    message = {"time":"22/02, 9:16 pm","key":"date: 20250222\ntime: 2116\nSent Rs.20.00 from Kotak Bank AC X6869 to 8123426823@axl on 22-02-25.UPI Ref 505317212798. Not you, https://kotak.com/KBANKT/Fraud"}
    process(message)