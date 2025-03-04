# Money Management Tool

## Overview

This project is a money management tool that helps segregate and manage transactions from a bank. The system retrieves transaction details via SMS, categorizes them, and stores them in a Google Spreadsheet using a Telegram bot.

## Features

- **Automatic Transaction Retrieval**: Parses SMS messages from the bank.
- **Telegram Bot Integration**: Notifies users about new transactions and allows categorization.
- **Google Sheets Integration**: Stores and organizes transaction details.
- **User-based Categorization**: Segregates transactions based on users.
- **Cloud Deployment**: Runs online via PythonAnywhere without requiring a personal laptop to be turned on.

## Technologies Used

- **Python**
- **Flask**
- **Telegram Bot API**
- **Google Sheets API**
- **Regular Expressions (**``** module)**
- **PythonAnywhere (Cloud Hosting)**

## Installation & Setup

1. **Clone the Repository**

   ```sh
   git clone https://github.com/your-username/money-management-bot.git
   cd money-management-bot
   ```

2. **Create a Virtual Environment** (Optional but recommended)

   ```sh
   python -m venv venv
   source venv/bin/activate   # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```sh
   pip install -r requirements.txt
   ```

4. **Set Up Google Sheets API**

   - Create a Google Cloud account.
   - Enable Google Sheets API and Google Apps Script API.
   - Create a service account and download the `credentials.json` file in the following format:
     ```json
     {
       "type": "service_account",
       "project_id": "your_id",
       "private_key_id": "your_key",
       "private_key": "-----BEGIN PRIVATE KEY-----\nyour_key\n-----END PRIVATE KEY-----\n",
       "client_email": "name@name.iam.gserviceaccount.com",
       "client_id": "id",
       "auth_uri": "https://accounts.google.com/o/oauth2/auth",
       "token_uri": "https://oauth2.googleapis.com/token",
       "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
       "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/name/name.iam.gserviceaccount.com",
       "universe_domain": "googleapis.com"
     }
     ```
   - Share your Google Sheet with your service account email.
   - Copy the provided template sheet: **[https://docs.google.com/spreadsheets/d/1R8nfg6QV43dv8PCheT4lmUfIJGlNqI2QFbXTngVKjEI/edit?usp=sharing]**
   - Deploy the Google Apps Script macro and add the `web_app_url` to `user_data.json`.

5. **Configure User Data** Update `user_data.json` with user details:

   ```json
   {
     "User_name_1": {
       "user_id": 1234567890,
       "web_app_url": "https://script.google.com/macros/s/Your_scripts_random_text/exec",
       "accounts": {
         "ac_no_1": {
           "bank_name": "Name1",
           "sub_users": {
             "sub_user_1": ["My Self", "Category_1", "Category_2"],
             "sub_user_2": ["Home expenses", "Category_1", "Category_2"],
             "sub_user_3": ["Category_"]
           }
         },
         "ac_no_2": {
           "bank_name": "Name2",
           "sub_users": {
             "sub_user_1": ["My Self", "Category_1", "Category_2"],
             "sub_user_2": ["Home expenses", "Category_1", "Category_2"],
             "sub_user_3": ["Category_"]
           }
         }
       }
     }
   }
   ```

6. **Get Your Telegram Chat ID**

   - Run `get_chat_id.py` to retrieve your chat ID.

7. **Create a `.env` File** and add the following details:
   ```sh
   TELEGRAM_BOT_TOKEN="TELEGRAM_BOT_TOKEN"
   TELEGRAM_API_SET="https://api.telegram.org/botTELEGRAM_BOT_TOKEN/setWebhook?url=web_api_url/telegram_webhook"
   YOUR_NGROK_URL="https://c250-2409-40f2-204f-efa2-68f9-5d53-9a30-6198.ngrok-free.app"  # for local testing
   ```

8. **Run the Application Locally**

   ```sh
   python app.py
   ```

## Using Ngrok for Local Testing

To use Ngrok with Node.js for local testing:

1. **Install Ngrok globally using npm:**
   ```sh
   npm install -g ngrok
   ```
2. **Start Ngrok for your Flask server (default port 5000):**
   ```sh
   ngrok http 5000
   ```
3. **Copy the generated public URL** and update it in `.env` under `YOUR_NGROK_URL`.
4. **Set the Telegram webhook using the updated URL:**
   ```sh
   curl -X POST "https://api.telegram.org/botTELEGRAM_BOT_TOKEN/setWebhook?url=YOUR_NGROK_URL/telegram_webhook"
   ```

## Deployment

This project is deployed on PythonAnywhere. Follow these steps to deploy:

1. Push your code to GitHub.
2. Set up a PythonAnywhere account.
3. Clone the repository on PythonAnywhere.
4. Configure environment variables.
5. Deploy the application.

## Usage

- Start the Telegram bot and add it to your contacts.
- Upon receiving an SMS, the bot sends a notification.
- Select a category and add a description for each transaction.
- Transactions are logged into the Google Spreadsheet.

## Future Enhancements

- Ability to add cash transactions
- Email scraping to fetch transaction data real time or at the end of the day.
- Account statement processing to reconcile and add any missed transactions at the end of the month.

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss.

## License

This project is licensed under the MIT License. See `LICENSE` for details.

