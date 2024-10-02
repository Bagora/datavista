from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import os
import pandas as pd
import plotly.express as px
import plotly.io as pio
from faker import Faker
import random
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

app = Flask(__name__)
app.secret_key = 'supersecretkey' #for faker
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static', exist_ok=True)

# Disable scientific notation for pandas
pd.set_option('display.float_format', lambda x: '%.3f' % x)

# Home route to render the upload form
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            return redirect(url_for('eda_dashboard', filename=file.filename))
    return render_template('index.html')

# EDA Dashboard route with plots for all columns
@app.route('/dashboard/<filename>', methods=['GET'])
def eda_dashboard(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_csv(filepath)
    
    # Basic statistics (summary)
    summary = df.describe().to_html(classes='table table-striped')

    # Generate plots for all columns
    plots_html = ""
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            fig = px.histogram(df, x=col, title=f'Distribution of {col}')
            plots_html += pio.to_html(fig, full_html=False)
    
    return render_template('dashboard.html', eda_content=summary + plots_html, filename=filename)

# Generate random data using Faker
@app.route('/generate', methods=['GET', 'POST'])
def generate_random_data():
    if request.method == 'GET':
        return render_template('generate_random_data.html')
    
    elif request.method == 'POST':
        try:
            # Initialize Faker
            fake = Faker()
            random.seed(42)

            # Function to generate random names, ages, and salaries
            def generate_sample_data(num_samples=100):
                data = []
                for _ in range(num_samples):
                    name = fake.name()
                    age = random.randint(18, 60)
                    salary = random.randint(12000, 5000000)
                    data.append({"Name": name, "Age": age, "Salary": salary})
                return pd.DataFrame(data)

            # Generate random data
            sample_data = generate_sample_data(300)
            
            # Save to CSV
            csv_filepath = os.path.join('static', 'test_data.csv')
            sample_data.to_csv(csv_filepath, index=False)

            # Send the CSV file for download
            return send_file(csv_filepath, as_attachment=True)
        
        except Exception as e:
            flash(f"An error occurred while generating data: {str(e)}")
            return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
