import os
from datetime import datetime
import pandas as pd
from mailjet_rest import Client
from premailer import transform
import html  # Import the html module for escaping HTML

folder_path = 'PREDICTIONS'

recovery_code = "6SXJJJA2A1LWFPZLL1XJJR2U"


def get_latest_prediction_files():
    indian_file = None
    usa_file = None
    latest_indian_date = None
    latest_usa_date = None

    for filename in os.listdir(folder_path):
        if "India predictions" in filename:
            # Extract the date from the filename
            date_str = filename.split(" ~ ")[0]
            date = datetime.strptime(date_str, "%Y-%m-%d")

            # Check if it's the latest Indian file
            if latest_indian_date is None or date > latest_indian_date:
                latest_indian_date = date
                indian_file = filename

        elif "USA predictions" in filename:
            # Extract the date from the filename
            date_str = filename.split(" ~ ")[0]
            date = datetime.strptime(date_str, "%Y-%m-%d")

            # Check if it's the latest USA file
            if latest_usa_date is None or date > latest_usa_date:
                latest_usa_date = date
                usa_file = filename

    return indian_file, usa_file, latest_indian_date, latest_usa_date


def formatted_data():
    ind_file, us_file, ind_date, us_date = get_latest_prediction_files()
    ind_data = pd.read_csv(f"PREDICTIONS/{ind_file}")
    us_data = pd.read_csv(f"PREDICTIONS/{us_file}")
    return ind_data, us_data, ind_date  # You can return ind_date or us_date based on your preference


def send_mailjet_email(api_key, api_secret, to_emails, subject, html_content):
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
        'Messages': [
            {
                'From': {
                    'Email': 'axisbysentinel@gmail.com',
                    'Name': 'Sentinel Axis'
                },
                'To': [{'Email': email} for email in to_emails],
                'Subject': subject,
                'HTMLPart': html_content
            }
        ]
    }
    result = mailjet.send.create(data=data)
    return result


def Transfer():
    ind, us, date = formatted_data()
    api_key = 'f7e4223ed2577efbeae06c030b3d59f3'
    api_secret = '7967e03caa456f8dbca32df6631ef35d'

    to_emails = ['wildrop321@gmail.com', 'tochandrasp@gmail.com', 'hellosubashgm@gmail.com']  # Make this a list
    formatted_date = date.strftime("%Y-%m-%d")  # Change the format as needed
    subject = f'Stock Predictions {formatted_date}'

    # Convert DataFrames to HTML
    ind_html = ind.to_html(classes='dataframe', index=False, escape=False)
    us_html = us.to_html(classes='dataframe', index=False, escape=False)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        .container {{
            display: flex;
        }}
        .column {{
            flex: 50%; /* Each column takes up 50% of the width */
            padding: 10px;
            box-sizing: border-box; /* Prevent padding from increasing width */
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
        }}
        th, td {{
            border: 1px solid #ddd;
            text-align: left;
            padding: 8px;
        }}
        th {{
            background-color: #f2f2f2;
        }}
    </style>
    </head>
    <body>
    <h1>Today's Prediction</h1>
    <div class="container">
        <div class="column" style="background-color: #f2f2f2;">
            <h2>IND Stock</h2>
            {ind_html} <!-- Display ind here -->
        </div>
        <div class="column" style="background-color: #e7e7e7;">
            <h2>US Stock</h2>
            {us_html} <!-- Display us here -->
        </div>
    </div>

    </body>
    </html>
    """

    response = send_mailjet_email(api_key, api_secret, to_emails, subject, html_content)
    print(response.status_code)
    print(response.json())

if __name__ == "__main__":
    Transfer()