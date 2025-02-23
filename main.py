from flask import Flask, request
import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv

from process_transaction import creds_from_user_id, get_user_data, process
from sheet_operations import get_values
from macro_functions import insert_delete_data
from sheet_operations import add_transaction

load_dotenv()  # Load variables from .env file
app = Flask(__name__)

# Telegram Bot Setup
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")  # Replace with your token
bot = telebot.TeleBot(BOT_TOKEN)

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("google_creds.json", scope)
client = gspread.authorize(credentials)
spreadsheet = client.open("Transaction Datasheet - Prashanth")  # Replace with your sheet name
sheet = spreadsheet.worksheet("Sheet1")  # Replace with your sheet name

# User data storage
user_data = {}


@app.route('/receive_sms', methods=['POST'])
def receive_sms():
    sms_data = request.get_data(as_text=True)
    if sms_data:
        print(f"Received SMS: {sms_data}")  # Add print statement for debugging
        user_id = process(sms_data)
        yes_no(user_id)
        return 'SMS received and processed', 200
    else:
        return 'No SMS data received', 400


@app.route('/telegram_webhook', methods=['POST'])
def telegram_webhook():
    update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
    if update.message:
        handle_message(update.message)
    elif update.callback_query:
        handle_callback(update.callback_query)
    return 'OK'


def handle_message(message):
    global user_data
    user_id = message.chat.id
    text = message.text
    if user_id not in user_data:
        user_data[user_id] = {}
    if text == '/start':
        yes_no(user_id)
    else:
        process_input("", user_id, text)


def handle_callback(call):
    user_id = call.message.chat.id
    data = call.data
    process_input(call.id, user_id, data)


def yes_no(user_id):
    bot.send_message(user_id, "Do you want to enter transaction", reply_markup=generate_markup("yes_no", ["Yes"]))


def generate_markup(category_name, category_lst):
    """Generates an inline keyboard markup with buttons."""
    markup = telebot.types.InlineKeyboardMarkup()
    for name in category_lst:
        markup.add(telebot.types.InlineKeyboardButton(name, callback_data=f"{category_name}_{name}"))
    markup.add(telebot.types.InlineKeyboardButton("Cancel", callback_data=f"{category_name}_cancel"))
    return markup


def process_input(call_id, user_id, input_value):
    global user_data
    if "yes_no" or "transaction" in input_value:
        response = input_value.split("_")[-1]
        response_lower = response.lower()

        if response_lower == "cancel":
            bot.answer_callback_query(call_id, text="Canceled")
            bot.send_message(user_id, "Canceled")
            user_data = {}

        elif "sub_user" in user_data[user_id] and "category" in user_data[user_id] and "description" not in user_data[user_id]:
            user_data[user_id]["description"] = response
            insert_to_database(user_id, "")

        elif response_lower != "cancel":
            bot.answer_callback_query(call_id, text=f"{response}")  # Notify user
            if response_lower != "yes":
                bot.send_message(user_id, f"You choose: {response}")
            else:
                bot.send_message(user_id, f"You choose: {response}")
            insert_to_database(user_id, input_value)


def get_input(user_id, txn, input_value):
    global user_data
    if len(txn) == 7:
        txn_type = "debited"
        from_to = "to"
    else:
        txn_type = "credited"
        from_to = "from"
    txn_message = (f"Your a/c XX{txn[0]} {txn_type} for Rs.{round(float(txn[-1]), 2)} on {txn[2]} {txn[3]}"
                   f" trf {from_to} {txn[5].capitalize()}. UPI:{txn[4]}.")
    ac_num = txn[0]
    user_creds = get_user_data()
    users = user_creds["Prashanth"]["accounts"][ac_num]["sub_users"]
    sub_users_lst = list(users.keys())
    # {1624670859: {'sub_user': 'user', 'category': 'Category2'}}

    if "Yes" in input_value:
        # user_data[user_id]["sub_user"] = input_value.split("_")[1]
        txn_message = (f"Your a/c XX{txn[0]} {txn_type} for Rs.{round(float(txn[-1]), 2)} on {txn[2]} {txn[3]}"
                       f" trf {from_to} {txn[5].capitalize()}. UPI:{txn[4]}.")
        bot.send_message(user_id, txn_message)
        if len(sub_users_lst) == 1:
            user_data[user_id]["sub_user"] = sub_users_lst[0]
            user = user_data[user_id]["sub_user"]
            bot.send_message(user_id, "Select a Category",
                             reply_markup=generate_markup("transaction_category", users[user]))
        else:
            bot.send_message(user_id, "Select a User",
                             reply_markup=generate_markup("transaction_sub_user", sub_users_lst))

    elif "sub_user" in input_value:
        user_data[user_id]["sub_user"] = input_value.split("_")[-1]
        user = user_data[user_id]["sub_user"]

        if len(users[user]) == 1:
            user_data[user_id]["category"] = users[user][0]
            bot.send_message(user_id, "Enter the description",
                             reply_markup=generate_markup("transaction_description", []))
        else:
            bot.send_message(user_id, "Select a Category",
                             reply_markup=generate_markup("transaction_category", users[user]))

    elif "category" in input_value:
        user_data[user_id]["category"] = input_value.split("_")[-1]
        bot.send_message(user_id, "Enter the description",
                         reply_markup=generate_markup("transaction_description", ["No description"]))


def insert_to_database(user_id, input_value):
    global user_data
    # get credentials
    creds = creds_from_user_id(user_id)
    spread_sheet = f"Transaction Datasheet - {creds["account_holder"]}"

    data = get_values(spread_sheet, "Pending Transactions", "row", 5, 2, 9)
    if input_value:
        get_input(user_id, data, input_value)
    if user_data:
        ln = len(list(user_data[user_id].keys()))
        if ln != 3:
            return
    else:
        return
    sub_user = user_data[user_id]["sub_user"]
    data.insert(6, user_data[user_id]["description"])
    data.insert(6, user_data[user_id]["category"])
    user_creds = get_user_data()
    bank_name = user_creds[creds["account_holder"]]["accounts"][data[0]]["bank_name"]
    sheet_name = f"{bank_name}-{sub_user}"

    data.pop(0)
    if len(data) < 9:
        data.append("")
    # format date and time
    data[1] = f"{data[1][:4]}-{data[1][4:6]}-{data[1][6:]}"
    data[2] = f"{data[2][:2]}:{data[2][2:]}"
    add_transaction(creds["web_app_url"], spread_sheet, sheet_name, data)
    insert_delete_data(creds["web_app_url"], "Pending Transactions", "delete", 5, "b", data[:8])
    print(data)
    bot.send_message(user_id, "Data saved to sheet")
    user_data[user_id] = {}



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)