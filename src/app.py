import dash
import pandas as pd
from dash import dcc, html, Input, Output
import seaborn as sns
import plotly.express as px
import dash_bootstrap_components as dbc

df = pd.read_csv('NFL.csv')

# Get the categorical columns
columns = df.columns.to_list()
numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
categorical_columns = df.columns.difference(numeric_columns).to_list()
drop_1 = df.columns.difference(['Year', 'Age', 'Player', 'Drafted..tm.rnd.yr.', 'Player_Type']).tolist()
drop_34 = df.columns.difference(categorical_columns + ['Year', 'Age']).tolist()

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(className="parent", children=[
    html.Div(className="title-container", children=[
    html.H1("NFL Combine Analysis", className="title")
]),
    html.Div(className="main-container", children=[
    html.Div(className="grid-container", children=[
        html.Div(className="grid-item", children=[
            html.Div([dcc.Dropdown(id='drop1', options=drop_1, value=drop_1[0])], className="dropdown"),
            html.Div(dcc.Graph(id='graph1'), className="graph")
        ]),
        html.Div(className="grid-item", children=[
            html.Div([
                html.Div(children=[
                    html.Div([
                        dcc.Checklist(
                            id='position_checklist',
                            options=[{'label': pos, 'value': pos} for pos in df['Position'].unique()],
                            inline=True,
                            labelStyle={'display': 'inline-block', 'margin-right': '10px'}
                        )
                    ], style={'display': 'grid', 'grid-template-columns': 'repeat(3, 1fr)', 'gap': '10px'})
                ], className="checklist-container"),
                html.Div(dcc.Graph(id='graph2'), className="graph")
            ])
        ]),
        html.Div(className="grid-item", children=[
            html.Div([
                dcc.Dropdown(id='drop3', options=drop_34, value=drop_34[0]),
                dcc.Dropdown(  # Add this dropdown
                    id='position_dropdown',
                    options=[{'label': pos, 'value': pos} for pos in df['Position'].unique()],
                    placeholder="Select a position (optional)"
                )
            ], className="dropdown"),
            html.Div(dcc.Graph(id='graph3'), className="graph")
        ]),
        html.Div(className="grid-item", children=[
            html.Div([dcc.Dropdown(id='drop4', options=drop_34, value=drop_34[0])], className="dropdown"),
            html.Div(dcc.Graph(id='graph4'), className="graph")
        ])
    ]),
        html.Div(className="player-container", children=[
            html.Div([
                dcc.Dropdown(
                    id='player_dropdown',
                    options=[{'label': player, 'value': player} for player in df['Player'].unique()],
                    placeholder="Select a player"
                )
            ], className="dropdown"),
            html.Div(dbc.Table(id='player_table', bordered=True, hover=True, responsive=True), className="table")
        ])
    ])

])

@app.callback(
    Output('graph1', 'figure'),
    Input('drop1', 'value')
)
def update_scatter(selected_column):
    fig = px.scatter(df, x=selected_column, y="Sprint_40yd", title="Scatter Plot", labels={"x": selected_column, "y": "Sprint_40yd"})
    return fig

@app.callback(
    Output('graph2', 'figure'),
    Input('position_checklist', 'value')
)
def update_heatmap(selected_positions):
    if not selected_positions:
        selected_positions = df['Position'].unique().tolist()
    filtered_df = df[df['Position'].isin(selected_positions)]
    corr_matrix = filtered_df[numeric_columns].corr()
    fig = px.imshow(corr_matrix, x=corr_matrix.columns, y=corr_matrix.columns)
    return fig

@app.callback(
    Output('graph3', 'figure'),
    Input('drop3', 'value'),
    Input('position_dropdown', 'value')  # Add this input
)
def update_drafted_bar(selected_column, selected_position=None):
    if selected_column in numeric_columns:
        filtered_df = df.copy()  # Create a copy of the original DataFrame
        
        # Filter by position if selected
        if selected_position:
            filtered_df = filtered_df[filtered_df['Position'] == selected_position]
        
        avg_by_drafted = filtered_df.groupby('Drafted')[selected_column].mean().reset_index()
        fig = px.bar(avg_by_drafted, x='Drafted', y=selected_column, title=f"Average {selected_column} by Drafted")
        return fig
    else:
        return {}

@app.callback(
    Output('graph4', 'figure'),
    Input('drop4', 'value')
)
def update_school_bar(selected_column):
    if selected_column in numeric_columns and selected_column not in ['Year', 'Age']:
        avg_by_school = df.groupby('School')[selected_column].mean().reset_index()
        
        if selected_column in ['BMI', 'Shuttle', 'Agility_3cone', 'Sprint_40yd']:
            avg_by_school = avg_by_school.sort_values(by=selected_column, ascending=True).head(6)
            title_text = f"Top 6 Schools by Average {selected_column}"
        else:
            avg_by_school = avg_by_school.sort_values(by=selected_column, ascending=False).head(6)
            title_text = f"Top 6 Schools by Average {selected_column}"

        fig = px.bar(avg_by_school, x='School', y=selected_column, title=title_text)
        return fig
    else:
        return {}
    
@app.callback(
    Output('player_table', 'children'),
    Input('player_dropdown', 'value')
)
def update_player_table(selected_player):
    if selected_player:
        player_row = df[df['Player'] == selected_player].iloc[0]
        table_header = [html.Thead(html.Tr([html.Th(col, className="text-center") for col in df.columns]))]
        table_rows = [html.Tr([html.Td(value, className="text-center") for value in player_row]) for _, player_row in df[df['Player'] == selected_player].iterrows()]
        table_body = [html.Tbody(table_rows)]
        return table_header + table_body
    else:
        return []
    
if __name__ == '__main__':
    app.run_server(debug=True, host='localhost', port='8005')