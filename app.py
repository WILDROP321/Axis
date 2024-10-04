from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
import pandas as pd
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from send_email import Transfer

#Sentinel (Social Engagement for New Technology in Innovative Networking and Learning)
#AXIS     (Analytical X-factor Investment Signal)

app = Flask(__name__)
app.secret_key = 'secret_key'  # Needed for session management

# Mock login credentials (for demonstration purposes)
valid_username = 'user'
valid_password = 'password'

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('main'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == valid_username and password == valid_password:
            session['username'] = username
            return redirect(url_for('main'))
        else:
            return "Invalid credentials, please try again."
    return render_template('login.html')

@app.route('/main')
def main():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Path to the PREDICTIONS directory
    predictions_dir = 'PREDICTIONS'
    
    # Lists to hold predictions
    india_predictions = []
    usa_predictions = []
    all_files = []

    latest_date = None

    # Loop through files in the predictions directory
    for filename in os.listdir(predictions_dir):
        if filename.endswith('.csv'):
            # Add to all_files for history section
            all_files.append(filename)

            # Extract the date from the filename
            date_str = filename.split(' ~ ')[0]  # Get the date part before ' ~ '
            file_date = datetime.strptime(date_str, '%Y-%m-%d')

            # Check for the latest date
            if latest_date is None or file_date > latest_date:
                latest_date = file_date

    # Loop again to collect predictions for the latest date
    for filename in all_files:  # Use all_files to ensure we collect all relevant predictions
        if filename.endswith('.csv'):
            date_str = filename.split(' ~ ')[0]  # Extract date again for filtering
            file_date = datetime.strptime(date_str, '%Y-%m-%d')
            if file_date == latest_date:  # Only process files with the latest date
                if 'India' in filename:
                    # Read India predictions
                    india_predictions.append(pd.read_csv(os.path.join(predictions_dir, filename)).to_html(index=False))
                elif 'USA' in filename:
                    # Read USA predictions
                    usa_predictions.append(pd.read_csv(os.path.join(predictions_dir, filename)).to_html(index=False))

    return render_template('main.html', india_predictions=india_predictions, usa_predictions=usa_predictions, all_files=all_files)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('PREDICTIONS', filename, as_attachment=True)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

