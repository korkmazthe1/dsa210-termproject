import xmltodict
import matplotlib
matplotlib.use('TkAgg')
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Function to read and parse an XML file into a structured format
def parse_and_load_xml(xml_file_path):
    with open(xml_file_path, 'r', encoding='utf-8') as xml_file:
        parsed_data = xmltodict.parse(xml_file.read())
    return parsed_data

# Function to filter and extract relevant information from the parsed dataset
def extract_relevant_data(parsed_health_data):
    health_records = parsed_health_data['HealthData']['Record']
    extracted_steps_data = []
    for single_record in health_records:
        if single_record['@type'] == "HKQuantityTypeIdentifierStepCount":
            extracted_steps_data.append({
                'record_created': single_record['@creationDate'],
                'step_start_time': single_record['@startDate'],
                'step_end_time': single_record['@endDate'],
                'step_count_value': int(single_record['@value'])
            })
    return pd.DataFrame(extracted_steps_data)

# Function to format and preprocess the dataset for analysis
def preprocess_and_clean_data(step_data_frame):
    step_data_frame['step_start_time'] = pd.to_datetime(step_data_frame['step_start_time'])
    step_data_frame['step_end_time'] = pd.to_datetime(step_data_frame['step_end_time'])
    step_data_frame['record_created'] = pd.to_datetime(step_data_frame['record_created'])
    step_data_frame['step_date'] = step_data_frame['step_start_time'].dt.date
    step_data_frame['step_date'] = pd.to_datetime(step_data_frame['step_date'])
    return step_data_frame

# Function to perform exploratory data analysis and create visualizations
def generate_visualizations(cleaned_step_data):
    # Group the data by date and compute the daily step totals
    daily_totals = cleaned_step_data.groupby('step_date')['step_count_value'].sum().reset_index()

    # Compute a 7-day rolling average for the step counts
    daily_totals['seven_day_avg'] = daily_totals['step_count_value'].rolling(window=7).mean()

    # Visualization of daily steps with a rolling average
    plt.figure(figsize=(12, 6))
    sns.lineplot(x='step_date', y='step_count_value', data=daily_totals, label='Daily Total', alpha=0.6)
    sns.lineplot(x='step_date', y='seven_day_avg', data=daily_totals, label='7-Day Average', color='red')
    plt.title('Daily Steps with Moving Average')
    plt.xlabel('Date')
    plt.ylabel('Step Count')
    plt.grid(True)
    plt.legend()
    plt.show()

    # Histogram to display the distribution of daily step counts
    plt.figure(figsize=(10, 5))
    sns.histplot(daily_totals['step_count_value'], kde=True, bins=30)
    plt.title('Distribution of Daily Steps')
    plt.xlabel('Step Count')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.show()

    # Analysis of monthly trends
    cleaned_step_data['analysis_month'] = cleaned_step_data['step_date'].dt.to_period('M')
    monthly_totals = cleaned_step_data.groupby('analysis_month')['step_count_value'].sum().reset_index()
    monthly_totals['analysis_month'] = monthly_totals['analysis_month'].dt.to_timestamp()

    # Visualization of step changes across months
    monthly_totals['step_difference'] = monthly_totals['step_count_value'].diff()
    monthly_totals['step_difference'] = monthly_totals['step_count_value'].diff()
    bar_colors = ['green' if value > 0 else 'red' for value in monthly_totals['step_difference']] # coloring of the columns
    plt.figure(figsize=(12, 6))
    sns.barplot(x='analysis_month', y='step_difference', data=monthly_totals, palette=bar_colors)
    plt.title('Monthly Step Change')
    plt.xlabel('Month')
    plt.ylabel('Step Count Change')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.show()

    # Regression analysis to highlight trends
    plt.figure(figsize=(12, 6))
    sns.regplot(x=monthly_totals.index, y='step_count_value', data=monthly_totals,
                scatter_kws={'color': 'blue'}, line_kws={'color': 'red'})
    plt.title('Step Trend with Regression Line')
    plt.xlabel('Month Index')
    plt.ylabel('Total Step Count')
    plt.grid(True)
    plt.show()

    return daily_totals

# Main function to execute the data analysis workflow
def execute_analysis_workflow(xml_file_path):
    print("Loading and parsing XML data.")
    parsed_data = parse_and_load_xml(xml_file_path)

    print("Extracting relevant step count data.")
    step_data_frame = extract_relevant_data(parsed_data)

    print("Cleaning, processing the data.")
    cleaned_data_frame = preprocess_and_clean_data(step_data_frame)

    print("Generating visual insights.")
    generate_visualizations(cleaned_data_frame)

    print("The visualizations and other processes are done.")

# Specify the path to the dataset and execute the analysis
dataset_file_path = 'dataset.xml'
execute_analysis_workflow(dataset_file_path)
