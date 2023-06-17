import json
import plotly
import plotly.graph_objects as go
from app import app
from flask import make_response, render_template, request
from data import combined_df
import pandas as pd


@app.route('/')
def home():
    # Sort the DataFrame by date in descending order
    sorted_df = combined_df.sort_values('Date of Registration', ascending=False)

    # Get the latest 5 societies
    latest_societies = sorted_df.head(3)

    # Extract the society names and states of the latest societies
    society_data = list(zip(latest_societies['Name of Society'], latest_societies['State']))

    return render_template('home.html', society_data=society_data)

@app.route('/state-wise')
def state_wise():
    # Count the number of societies in each state
    state_counts = combined_df['State'].value_counts().reset_index()
    state_counts.columns = ['State/UT Name', 'No. of Society']

    # Add the Sno (serial number) column
    state_counts['Sno'] = range(1, len(state_counts) + 1)
    # Define the desired column sequence
    desired_columns = ['Sno' , 'State/UT Name' , 'No. of Society']

    # Reindex the DataFrame with the desired column sequence
    state_counts = state_counts.reindex(columns=desired_columns)

    # Calculate the total count
    total_count = state_counts['No. of Society'].sum()

    # Append the total count row to the state counts DataFrame
    total_row = pd.DataFrame([['' , 'Total Number of Socities - ', total_count]], columns=['Sno', 'State/UT Name', 'No. of Society'])
    state_counts = pd.concat([ state_counts , total_row ]).reset_index(drop=True)

    # Convert the state counts DataFrame to HTML table
    state_counts_table = state_counts.to_html(index=False)

    return render_template('STATEWISE.html', table=state_counts_table)


@app.route('/all-reg-society')
def all_reg_society():

    # Convert the DataFrame to an HTML table
    table_html = combined_df.to_html(index=False)

    return render_template('ALLREGSOCIETY.html', table=table_html)

@app.route('/society-before-1986')
def society_before_1986():
    combined_df['Date of Registration'] = pd.to_datetime(combined_df['Date of Registration'])
    filtered_df = combined_df[combined_df['Date of Registration'].dt.year < 1986]

    table_html = filtered_df.to_html(index=False)

    return render_template('SOCIETYBEFOR1968.html', table_html=table_html)



@app.route('/calender-wise', methods=['GET', 'POST'])
def calender_wise():

    # Extract the calendar year from the 'Date of Registration' column
    combined_df['Calendar Year'] = pd.DatetimeIndex(combined_df['Date of Registration']).year

    # Group the DataFrame by calendar year and count the number of societies
    grouped_df = combined_df.groupby('Calendar Year').size().reset_index(name='No. of Societies')

    # Convert the grouped DataFrame to an HTML table
    table_html = grouped_df.to_html(index=False)

    if request.method == 'POST':
        selected_state = request.form.get('state')

        # Filter the DataFrame by selected state
        filtered_df = combined_df[combined_df['State'] == selected_state]

        # Extract the calendar year from the 'Date of Registration' column
        filtered_df['Calendar Year'] = pd.DatetimeIndex(filtered_df['Date of Registration']).year

        # Group the filtered DataFrame by calendar year
        grouped_df = filtered_df.groupby('Calendar Year').size().reset_index(name='No. of Societies')

        # Convert the grouped DataFrame to an HTML table
        table_html = grouped_df.to_html(index=False)

        return render_template('CALENDARWISE.html', table_html=table_html)

    # Create a list of unique states from the DataFrame
    states_list = combined_df['State'].unique()

    return render_template('CALENDARWISE.html', states_list = states_list, table_html=table_html)


@app.route('/financial-wise' , methods=['GET', 'POST'])
def financial_wise():
    # Extract the financial year from the 'Date of Registration' column
    combined_df['Financial Year'] = pd.PeriodIndex(combined_df['Date of Registration'], freq='A-APR')
    # Group the DataFrame by financial year
    grouped_df = combined_df.groupby('Financial Year').size().reset_index(name='No. of Society')
    # Convert the grouped DataFrame to an HTML table
    table_html = grouped_df.to_html(index=False)
    if request.method == 'POST':
        selected_state = request.form.get('state')

        # Filter the DataFrame by selected state
        filtered_df = combined_df[combined_df['State'] == selected_state]

        # Extract the financial year from the 'Date of Registration' column
        filtered_df['Financial Year'] = pd.PeriodIndex(filtered_df['Date of Registration'], freq='A-APR')

        # Group the filtered DataFrame by financial year
        grouped_df = filtered_df.groupby('Financial Year').size().reset_index(name='No. of Society')

        # Convert the grouped DataFrame to an HTML table
        table_html = grouped_df.to_html(index=False)

        return render_template('FINANCIALWISE.html', table_html=table_html)

    # Create a list of unique states from the DataFrame
    states_list = combined_df['State'].unique()

    return render_template('FINANCIALWISE.html', states_list=states_list , table_html=table_html)


@app.route('/full-list')
def full_list():
    society_list = list(zip(combined_df['Name of Society'], combined_df['State']))
    return render_template('FULLLIST.html', society_list=society_list)

@app.route('/bank-list')
def bank_list():
    # Filter the DataFrame to include only Cooperative Banks
    bank_df = combined_df[combined_df['Sector Type'] == 'Cooperative Bank']
    table_html = bank_df.to_html(index=False)
    return render_template('BANKLIST.html', table_html=table_html)

@app.route('/state-wise-chart')
def state_wise_chart():
    # Count the occurrences of each state in the combined_df DataFrame
    state_counts = combined_df['State'].value_counts()
    colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']

    # Create a histogram using Plotly
    fig = go.Figure(data=[go.Bar(x=state_counts.index, y=state_counts.values, marker_color=colors)])
    fig.update_layout(title='State-wise Count of all Society', xaxis_title='State', yaxis_title='No. of Society', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    # Convert the chart to HTML
    chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    

    return render_template('STATEWISECHART.html', chart_html=chart_html)


@app.route('/year-wise-chart')
def year_wise_char():
    combined_df['Year'] = combined_df['Date of Registration'].dt.year

    # Count the occurrences of each year in the combined_df DataFrame
    year_counts = combined_df['Year'].value_counts().sort_index()
    colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']

    # Create a bar chart using Plotly
    fig = go.Figure(data=[go.Bar(x=year_counts.index, y=year_counts.values , marker_color=colors)])
    fig.update_layout(title='Year-wise Count of Registered Societies', xaxis_title='Year', yaxis_title='No. of Society' , paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    # Convert the chart to HTML
    chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    return render_template('YEARWISECHART.html', chart_html=chart_html)
   
@app.route('/type-wise-chart')
def typr_wise_char():
    # Count the occurrences of each type in the combined_df DataFrame
    type_counts = combined_df['Sector Type'].value_counts()
    colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']

    # Create a bar chart using Plotly
    fig = go.Figure(data=[go.Bar(x=type_counts.index, y=type_counts.values, marker_color=colors)])
    fig.update_layout(title='Type-wise Count of Registered Societies', xaxis_title='Type', yaxis_title='No. of Society' , paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    # Convert the chart to HTML
    chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    return render_template('TYPEWISECHART.html', chart_html=chart_html)

