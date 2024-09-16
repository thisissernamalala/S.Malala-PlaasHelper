import io
import base64
import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/weather')
def weather():
    # Load your weather data (update the path to your data file)
    file_path = './weather.xlsx'
    data = pd.read_excel(file_path)

    # Convert 'datetime' column to datetime type
    data['datetime'] = pd.to_datetime(data['datetime'], format='%Y-%m-%d')

    # Generate a line graph
    fig, ax = plt.subplots()
    ax.plot(data['datetime'], data['tempmax'], label='Max Temperature', color='red')
    ax.plot(data['datetime'], data['tempmin'], label='Min Temperature', color='blue')
    ax.plot(data['datetime'], data['temp'], label='Average Temperature', color='green')
    ax.set_xlabel('Date')
    ax.set_ylabel('Temperature (°C)')
    ax.set_title('Temperature Trends')
    ax.legend()
    ax.grid(True)

    # Save the plot to a BytesIO object and encode it as base64
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    line_graph_url = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()

    # Generate a bar graph for a different metric (e.g., precipitation)
    fig, ax = plt.subplots()
    data['date'] = data['datetime'].dt.date  # Convert datetime to date for x-axis
    ax.bar(data['date'], data['precip'], color='cyan')
    ax.set_xlabel('Date')
    ax.set_ylabel('Precipitation (mm)')
    ax.set_title('Precipitation Levels')
    ax.grid(True)

    # Save the plot to a BytesIO object and encode it as base64
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    bar_graph_url = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()

    return render_template('weather.html', line_graph_url=line_graph_url, bar_graph_url=bar_graph_url)

if __name__ == '__main__':
    app.run(debug=True)
