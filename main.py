import gspread
import plotly.graph_objects as go
import numpy as np

# Authenticate and open the spreadsheet
gc = gspread.service_account()
sh = gc.open("Megan Diulus Training Log")
sheet = sh.worksheet('2024-2025')

# Get and filter data
data = sheet.get_all_values()[9::8]  # Start from the 9th row, step by 8
filtered_data = [[row[col] for col in [8, 13, 14, 15]] for row in data]

# Map the filtered data to a dictionary, ignoring '0' or '#DIV/0!'
labels = ['Distance', 'Heart Rate', 'Rating', 'Sleep']
result_dict = {label: [] for label in labels}

for row in filtered_data:
    for i, label in enumerate(labels):
        value = row[i]
        if value not in ['0', '#DIV/0!', '']:  # Filter out invalid values
            if ':' in value:
                hour = float(value[0:1])
                min = float(value[2:4])
                minpercentofhour = min / 60
                finalTime = hour + minpercentofhour
                result_dict[label].append(finalTime)
            else:
                result_dict[label].append(float(value))  # Convert to float for plotting

# Create interactive plots using Plotly
fig = go.Figure()

# Add traces for each label
for label in labels:
    fig.add_trace(go.Scatter(
        x=list(range(len(result_dict[label]))),
        y=result_dict[label],
        mode='lines+markers',
        name=label,
        hoverinfo='x+y',
        marker=dict(size=8),
        line=dict(width=2),
        showlegend=True
    ))

# Calculate regression lines for each metric
regression_lines = {}

for label in labels:
    x = np.arange(len(result_dict[label]))  # Weeks as x-values
    y = np.array(result_dict[label])
    
    # Perform linear regression
    coefficients = np.polyfit(x, y, 1)  # Linear fit (degree 1)
    regression_line = np.polyval(coefficients, x)
    regression_lines[label] = regression_line

# Add regression lines to the interactive plot
for label in labels:
    fig.add_trace(go.Scatter(
        x=list(range(len(result_dict[label]))),
        y=regression_lines[label],
        mode='lines',
        name=f'{label} Trend',
        line=dict(dash='dash')
    ))

# Customize layout
fig.update_layout(
    title='Training Data Over Time',
    xaxis_title='Weeks',
    yaxis_title='Values',
    template='plotly_white',
    legend=dict(x=0, y=1, traceorder='normal')
)

fig.show()

# Calculate correlation coefficients between different metrics
correlations = {}
for i in range(len(labels)):
    for j in range(i + 1, len(labels)):
        label1 = labels[i]
        label2 = labels[j]
        correlation = np.corrcoef(result_dict[label1], result_dict[label2])[0, 1]
        correlations[(label1, label2)] = correlation

# Print the correlation results
print("Correlation Coefficients:")
for (label1, label2), correlation in correlations.items():
    print(f"Correlation between {label1} and {label2}: {correlation:.2f}")
