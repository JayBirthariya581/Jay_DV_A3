import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Load the dataset from CSV
df = pd.read_csv('Fifa_world_cup_matches.csv')
df['ts'] = pd.to_datetime(df['date'], format='%d %b %Y')

# Sort the DataFrame by the parsed date column
df = df.sort_values(by='ts')

# Rename columns to replace spaces with underscores
df.columns = df.columns.str.replace(" ", "_")

# Check if the required columns exist
required_columns = [
    "possession_team1", "possession_team2", "possession_in_contest",
    "number_of_goals_team1", "number_of_goals_team2", "total_attempts_team1",
    "total_attempts_team2", "on_target_attempts_team1", "on_target_attempts_team2",
    "team1", "team2", "date", "hour", "category", "assists_team1", "assists_team2"
]
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    raise ValueError(f"Missing columns in dataset: {missing_columns}")

# Preprocessing
df["possession_team1"] = df["possession_team1"].str.rstrip('%').astype(float)
df["possession_team2"] = df["possession_team2"].str.rstrip('%').astype(float)
df["possession_in_contest"] = df["possession_in_contest"].str.rstrip('%').astype(float)

# Prepare the data for the 3D Stacked Bar Chart
teams = pd.concat([df['team1'], df['team2']]).unique() 
categories = df['category'].unique()

# Calculate offensive metrics for each category
metrics = {}
for category in categories:
    category_metrics = []
    for team in teams:
        team_data = df[(df['team1'] == team) | (df['team2'] == team)]
        category_data = team_data[team_data['category'] == category]
        if category_data.empty:
            attempts = on_target = goals = assists = 0
        else:
            attempts = round(category_data['total_attempts_team1'].sum() + category_data['total_attempts_team2'].sum(), 2)
            on_target = round(((category_data['on_target_attempts_team1'].sum() + category_data['on_target_attempts_team2'].sum()) /
                              (category_data['total_attempts_team1'].sum() + category_data['total_attempts_team2'].sum())) * 100, 2)
            goals = round(category_data['number_of_goals_team1'].sum() + category_data['number_of_goals_team2'].sum(), 2)
            assists = round(category_data['assists_team1'].sum() + category_data['assists_team2'].sum(), 2)
        category_metrics.append([team, attempts, on_target, goals, assists])
    metrics[category] = pd.DataFrame(category_metrics, columns=['Team', 'Total Attempts', 'On-Target %', 'Goals', 'Assists'])

# Create the initial 3D stacked bar chart using the first category as default
default_category = categories[0]
metrics_df = metrics[default_category]

fig4 = go.Figure()

# Define a new dark color scheme
colors = ['#1F77B4', '#FF7F0E', '#2CA02C', '#D62728']  # Darker, catchy colors

# Add traces for each metric with improved hover info and rounded values
fig4.add_trace(go.Bar(
    x=metrics_df['Team'], 
    y=metrics_df['Total Attempts'], 
    name='Total Attempts',
    marker=dict(color=colors[0], line=dict(width=0)),
    hoverinfo='x+y+text',
    text=[f'{val:.2f}' for val in metrics_df['Total Attempts']]
))

fig4.add_trace(go.Bar(
    x=metrics_df['Team'], 
    y=metrics_df['On-Target %'], 
    name='On-Target %',
    marker=dict(color=colors[1], line=dict(width=0)),
    hoverinfo='x+y+text',
    text=[f'{val:.2f}' for val in metrics_df['On-Target %']]
))

fig4.add_trace(go.Bar(
    x=metrics_df['Team'], 
    y=metrics_df['Goals'], 
    name='Goals',
    marker=dict(color=colors[2], line=dict(width=0)),
    hoverinfo='x+y+text',
    text=[f'{val:.2f}' for val in metrics_df['Goals']]
))

fig4.add_trace(go.Bar(
    x=metrics_df['Team'], 
    y=metrics_df['Assists'], 
    name='Assists',
    marker=dict(color=colors[3], line=dict(width=0)),
    hoverinfo='x+y+text',
    text=[f'{val:.2f}' for val in metrics_df['Assists']]
))

# Update layout to create the appearance of 3D stacking
fig4.update_layout(
    title='3D Stacked Bar Chart: Offensive Efficiency',
    barmode='stack',
    xaxis=dict(title='Teams', showgrid=False, zeroline=False),
    yaxis=dict(title='Offensive Metrics', showgrid=False, zeroline=False),
    plot_bgcolor='rgb(50, 50, 50)',
    paper_bgcolor='rgb(50, 50, 50)',
    font_color='white',
    scene=dict(
        camera=dict(
            eye=dict(x=1.5, y=1.5, z=0.5)
        ),
        aspectratio=dict(x=2, y=1, z=0.5)
    ),
    updatemenus=[
        dict(
            buttons=[
                dict(
                    args=[{'x': [metrics[category]['Team']] * 4,
                           'y': [metrics[category]['Total Attempts'], metrics[category]['On-Target %'], metrics[category]['Goals'], metrics[category]['Assists']],
                           'text': [metrics[category]['Total Attempts'], metrics[category]['On-Target %'], metrics[category]['Goals'], metrics[category]['Assists']]}],
                    label=category,
                    method='update'
                ) for category in categories
            ],
            direction='down',
            showactive=True,
            x=0.5,
            xanchor='left',
            y=1.15,
            yanchor='top'
        )
    ]
)

# Interactive Visualization 1: Parallel Coordinates for Key Metrics
fig1 = px.parallel_coordinates(
    df,
    dimensions=["possession_team1", "possession_team2", "number_of_goals_team1", "number_of_goals_team2", "total_attempts_team1", "total_attempts_team2"],
    color="number_of_goals_team1",
    title="Parallel Coordinates for Match Performance",
    color_continuous_scale=px.colors.sequential.Viridis
)
fig1.update_layout(
    title_font_size=18,
    plot_bgcolor="black",
    paper_bgcolor="rgb(50, 50, 50)",
    font_color="white"
)





fig2 = go.Figure()

# Add traces for Team 1
for i, row in df.iterrows():
    fig2.add_trace(go.Scatter3d(
        x=[row['total_attempts_team1']],
        y=[row['possession_team1']],
        z=[row['number_of_goals_team1']],
        mode='markers',
        marker=dict(size=row['on_target_attempts_team1'], opacity=0.8),
        name=f"{row['team1']} vs {row['team2']} ({row['date']})",
        text=f"{row['team1']} ({row['date']})",
        hovertemplate=(
            f"Team: {row['team1']}<br>"
            f"Total Attempts: {row['total_attempts_team1']}<br>"
            f"Possession: {row['possession_team1']}%<br>"
            f"Goals: {row['number_of_goals_team1']}<br>"
            f"On Target Attempts: {row['on_target_attempts_team1']}<br>"
        ),
        visible=True
    ))

# Add traces for Team 2
for i, row in df.iterrows():
    fig2.add_trace(go.Scatter3d(
        x=[row['total_attempts_team2']],
        y=[row['possession_team2']],
        z=[row['number_of_goals_team2']],
        mode='markers',
        marker=dict(size=row['on_target_attempts_team2'], opacity=0.8),
        name=f"{row['team1']} vs {row['team2']} ({row['date']})",
        text=f"{row['team2']} ({row['date']})",
        hovertemplate=(
            f"Team: {row['team2']}<br>"
            f"Total Attempts: {row['total_attempts_team2']}<br>"
            f"Possession: {row['possession_team2']}%<br>"
            f"Goals: {row['number_of_goals_team2']}<br>"
            f"On Target Attempts: {row['on_target_attempts_team2']}<br>"
        ),
        visible=False
    ))

# Create dropdown buttons for Team 1 and Team 2
buttons = [
    {
        'args': [{'visible': [i < len(df) for i in range(len(df)*2)]}],
        'label': 'Team 1',
        'method': 'update'
    },
    {
        'args': [{'visible': [i >= len(df) for i in range(len(df)*2)]}],
        'label': 'Team 2',
        'method': 'update'
    }
]

# Update layout with dropdown
fig2.update_layout(
    updatemenus=[{
        'buttons': buttons,
        'direction': 'down',
        'showactive': True
    }],
    title="3D Scatter: Match-wise Attempts vs Possession vs Goals",
    plot_bgcolor="black",
    paper_bgcolor="rgb(50, 50, 50)",
    font_color="white",
    scene=dict(
        xaxis_title='Attempts',
        yaxis_title='Possession (%)',
        zaxis_title='Goals'
    )
)


# Interactive Visualization 3: Animated Bubble Chart for Goals Over Tim
# Define a color map for teams
color_map = {
    'Australia': '#1f77b4', 'Iran': '#ff7f0e', 'Japan': '#2ca02c', 'Qatar': '#d62728',
    'Saudi Arabia': '#9467bd', 'South Korea': '#8c564b', 'Cameroon': '#e377c2',
    'Ghana': '#7f7f7f', 'Morocco': '#bcbd22', 'Senegal': '#17becf', 'Tunisia': '#1f77b4',
    'Canada': '#ff7f0e', 'Costa Rica': '#2ca02c', 'Mexico': '#d62728', 'United States': '#9467bd',
    'Argentina': '#8c564b', 'Brazil': '#e377c2', 'Ecuador': '#7f7f7f', 'Uruguay': '#bcbd22',
    'Belgium': '#17becf', 'Croatia': '#1f77b4', 'Denmark': '#ff7f0e', 'England': '#2ca02c',
    'France': '#d62728', 'Germany': '#9467bd', 'Netherlands': '#8c564b', 'Poland': '#e377c2',
    'Portugal': '#7f7f7f', 'Serbia': '#bcbd22', 'Spain': '#17becf', 'Switzerland': '#1f77b4',
    'Wales': '#ff7f0e'
}
df_sorted = df.sort_values('ts')

    
# Create the base figure for Team 1
fig3 = px.scatter(
    df_sorted,
    x='team1',  # x-axis will be the teams
    y='number_of_goals_team1',  # y-axis will be goals for team 1
    size='total_attempts_team1',  # bubble size based on total attempts
    color='team1',  # color each team differently
    hover_name='team1',  # show team name on hover
    animation_frame='ts',  # animate by date
    animation_group='team1',
    range_y=[0, df_sorted['number_of_goals_team1'].max() + 2],  # set y-axis range
    title='Goals Over Time: Team Performance',
    labels={
        'team1': 'Team',
        'number_of_goals_team1': 'Goals',
        'total_attempts_team1': 'Total Attempts',
        'ts': 'Match Date'
    },
    color_discrete_map=color_map  # Apply the color map to the scatter plot
)

# Add Team 2 data as a separate trace with detailed hover template
team2_trace = go.Scatter(
    x=df_sorted['team2'],
    y=df_sorted['number_of_goals_team2'],
    mode='markers',
    marker=dict(
        size=df_sorted['total_attempts_team2'],
        sizemode='area',
        sizeref=2. * max(df_sorted['total_attempts_team2']) / (40. ** 2),
        sizemin=4,
        color=[color_map.get(team, '#000000') for team in df_sorted['team2']],  # Map the color for Team 2
        showscale=False
    ),
    name='Team 2 Goals',
    hovertemplate=(
        '<b>Match Details</b><br>'
        'Team 1: %{customdata[0]}<br>'
        'Team 2: %{x}<br>'
        'Team 1 Goals: %{customdata[1]}<br>'
        'Team 2 Goals: %{y}<br>'
        'Team 1 Attempts: %{customdata[2]}<br>'
        'Team 2 Attempts: %{marker.size}<br>'
        'Date: %{customdata[3]}<extra></extra>'
    ),
    customdata=list(zip(
        df_sorted['team1'], 
        df_sorted['number_of_goals_team1'], 
        df_sorted['total_attempts_team1'], 
        df_sorted['ts']
    )),
    visible=True
)

# Add Team 2 trace to the figure
fig3.add_trace(team2_trace)

# Customize layout
fig3.update_layout(
    plot_bgcolor='rgb(50, 50, 50)',
    paper_bgcolor='rgb(50, 50, 50)',
    font_color='white',
    title_font_size=18,
    height=600,
    xaxis_title='Teams',
    yaxis_title='Number of Goals',
    showlegend=False,
    
    # Customize animation menu
    updatemenus=[{
        'buttons': [
            {
                'args': [None, {
                    'frame': {'duration': 2000, 'redraw': True},  # Slow down animation (2 seconds per frame)
                    'fromcurrent': True,
                    'transition': {
                        'duration': 500,
                        'easing': 'quadratic-in-out'
                    }
                }],
                'label': 'Play',
                'method': 'animate'
            },
            {
                'args': [[None], {
                    'frame': {'duration': 0, 'redraw': False},
                    'mode': 'immediate',
                    'transition': {'duration': 0}
                }],
                'label': 'Pause',
                'method': 'animate'
            }
        ],
        'direction': 'left',
        'pad': {'r': 10, 't': 87},
        'showactive': False,
        'type': 'buttons',
        'x': 0.1,
        'xanchor': 'right',
        'y': 0,
        'yanchor': 'top'
    }]
)

# Customize slider to be visible and show only current date
fig3.update_layout(
    sliders=[{
        'active': 0,
        'yanchor': 'top',
        'xanchor': 'left',
        'currentvalue': {
            'font': {'size': 20, 'color': 'white'},
            'prefix': 'Date: ',
            'visible': True,
            'xanchor': 'right'
        },
        'transition': {'duration': 300, 'easing': 'cubic-in-out'},
        'pad': {'b': 10, 't': 50},
        'len': 0.9,
        'x': 0.1,
        'xanchor': 'left',
        'y': 0,
        'yanchor': 'top',
        # Styling to make slider visible but minimal
        'bgcolor': 'rgba(100, 100, 100, 0.2)',  # Slightly visible background
        'bordercolor': 'rgba(200, 200, 200, 0.5)',
        'borderwidth': 1,
        'steps': [
            {
                'method': 'animate',
                'args': [[str(date)], {'mode': 'immediate', 'transition': {'duration': 300}, 'frame': {'duration': 300, 'redraw': True}}],
                'label': str(date)
            } for date in df_sorted['ts'].unique()
        ]
    }]
)

# Create frames for animation
frames = []
for date in df_sorted['ts'].unique():
    frame_data = df_sorted[df_sorted['ts'] == date]
    
    frame = go.Frame(
        name=str(date),
        data=[
            go.Scatter(
                x=frame_data['team1'],
                y=frame_data['number_of_goals_team1'],
                mode='markers',
                marker=dict(
                    size=frame_data['total_attempts_team1'],
                    color=[color_map.get(team, '#000000') for team in frame_data['team1']]
                )
            ),
            go.Scatter(
                x=frame_data['team2'],
                y=frame_data['number_of_goals_team2'],
                mode='markers',
                marker=dict(
                    size=frame_data['total_attempts_team2'],
                    color=[color_map.get(team, '#000000') for team in frame_data['team2']]
                )
            )
        ]
    )
    frames.append(frame)

# Add frames to the figure
fig3.frames = frames



# Dash application
app = dash.Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div([
    html.H1("FIFA World Cup Match Analysis Dashboard", style={'text-align': 'center', 'color': 'white'}),
    html.Div([
        dcc.Graph(figure=fig1, style={'width': '48%', 'display': 'inline-block'}),
        dcc.Graph(figure=fig2, style={'width': '48%', 'display': 'inline-block'}),
    ]),
    html.Div([
        dcc.Graph(figure=fig3, style={'width': '48%', 'display': 'inline-block'}),
        dcc.Graph(figure=fig4, style={'width': '48%', 'display': 'inline-block'}),
    ], style={'backgroundColor': 'rgb(50, 50, 50)'}),
], style={'backgroundColor': 'rgb(50, 50, 50)'})


def create_standalone_html(app):
    # Extract the layout
    layout_html = app.index()
    
    # Write to file
    with open('fifa_world_cup_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(layout_html)




# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=False)
    
    

