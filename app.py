import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import base64

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# SVG data for the ellipse
svg_data = """<svg xmlns="http://www.w3.org/2000/svg" width="113" height="113" viewBox="0 0 113 113" fill="none">
<circle cx="56.5" cy="56.5" r="56.5" fill="#739255"/>
</svg>"""
# Encode SVG data to base64
svg_data_url = f"data:image/svg+xml;charset=utf-8;base64,{base64.b64encode(svg_data.encode()).decode()}"

app.layout = html.Div(
    children=[
        # Top bar with search bar
        dbc.Row([
            dbc.Col([
                dbc.InputGroup([
                    dbc.Input(type='text', id='search-bar', placeholder='Search...', style={'border-radius': '20px', 'margin-right': '5px'}),
                    html.Img(src=dash.get_asset_url('rieee.png'), style={'width': '33px', 'height': '33px', 'vertical-align': '', 'order': 2, 'background': 'transparent'}),
                ]),
            ], width=9),
            dbc.Col([], width=3),  
        ], style={'background': '#f2f2f2', 'padding': '10px', 'display': 'flex', 'align-items': 'center'}),

        # Welcome header
        dbc.Row([
            dbc.Col([
                html.H3("Welcome back, Foo", id='welcome-header', style={'margin-top': '20px', 'margin-bottom': '20px'}),
            ], width=12),
        ]),

        dbc.Row([
            # Vertical navi bar on the left
            dbc.Col([
                dbc.Nav([
                    dbc.NavLink('Dashboard', href='/dashboard', id='dashboard-link', style={'color': 'inherit', 'text-decoration': 'none', 'padding': '10px', 'margin-bottom': '5px'}),
                    dbc.NavLink('Overall Meanings', href='/glossary', id='glossary-link', style={'color': 'inherit', 'text-decoration': 'none', 'padding': '10px', 'margin-bottom': '5px'}),
                    dbc.NavLink('My Reflections', href='/reflections', id='reflections-link', style={'color': 'inherit', 'text-decoration': 'none', 'padding': '10px', 'margin-bottom': '5px'}),
                    dbc.NavLink('Teams', href='/teams', id='teams-link', style={'color': 'inherit', 'text-decoration': 'none', 'padding': '10px', 'margin-bottom': '5px'}),
                ], vertical=True, pills=True, style={'background': '#f2f2f2', 'border-radius': '10px', 'padding': '20px', 'height': 'calc(100vh - 140px)', 'position': 'sticky', 'top': '20px'}),
            ], width=2),

            # Content of the page
            dbc.Col([
                dcc.Location(id='url', refresh=False, pathname='/dashboard'),
                html.Div(id='page-content'),
            ], width=8),
        ]),
    ], style={'margin-left': '20px'})  


# Callback to update the content of the page 
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
)
def update_page_content(pathname):
    if pathname == '/dashboard':
        # subject to change
        return [
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader('Teams'),
                        dbc.CardBody([
                            html.Label('Current Team'),
                            html.Div('Team Name: Team LINGO', id='current-team-display'),
                            dbc.Button('Update Team', id='update-team-button', color='success', className='mt-2'),
                        ]),
                    ]),
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader('User Profile'),
                        dbc.CardBody([
                            dcc.Input(id='username-input', type='text', placeholder='Enter your username'),
                            html.Div([
                                dbc.Button('Update Profile', id='update-profile-button', color='success', className='mt-2'),
                            ], style={'margin-top': '10px'}),
                            html.Div(id='profile-info-display'),
                        ]),
                    ]),
                ], width=6),
            ], id='dashboard-center-boxes', justify='center', style={'margin-top': '20px'}),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader('Previous Reflections'),
                        dbc.CardBody('Display info'),
                    ]),
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader('New Entry'),
                        dbc.CardBody([
                            dcc.Input(id='word-input', type='text', placeholder='Enter word...'),
                            dcc.Input(id='reflection-input', type='text', placeholder='Enter reflection...'),
                            html.Br(),
                            dbc.Button('Submit', id='submit-reflection', color='success', className='mt-2'),
                        ]),
                    ]),
                ], width=6),
            ], id='dashboard-bottom-boxes', justify='center', style={'margin-top': '20px'}),
        ]
    
    elif pathname == '/glossary':
        
        glossary_data = [
            {"Word": "Example Word 1", "Meaning": "Example Meaning 1"},
            {"Word": "Example Word 2", "Meaning": "Example Meaning 2"},
            {"Word": "Example Word 3", "Meaning": "Example Meaning 3"},
        ]

        table_content = dbc.Table(
            [
                html.Tr([html.Th("Word"), html.Th("Meaning")]),
                *[html.Tr([html.Td(entry["Word"]), html.Td(entry["Meaning"])]) for entry in glossary_data],
            ],
            bordered=True,
            dark= False,
            responsive=True,
            striped=True,
            hover=True,
            style={'width': '90%', 'margin': '0 auto', 'background-color': 'white'},
        )
        #back button to return to dashboard!
        back_button = dcc.Link('Back to Dashboard', href='/dashboard', style={'color': 'blue'})
        return [html.H1("Words and Meanings"), html.P("Shows all words and meanings."), table_content, html.Br(), back_button]
    
    elif pathname == '/reflections':
        return [
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader('Your Reflections'),
                        dbc.CardBody([
                            dcc.Dropdown(
                                id='word-dropdown',
                                options=[
                                    {'label': 'Word 1', 'value': 'Word 1'},
                                    {'label': 'Word 2', 'value': 'Word 2'},
                                    {'label': 'Word 3', 'value': 'Word 3'}
                                ],
                                placeholder='Select a word...',
                                style={'margin-bottom': '10px'}
                            ),
                            dbc.Table(
                                id='selected-word-table',
                                bordered=True,
                                dark=False,
                                responsive=True,
                                striped=True,
                                hover=True,
                            )
                        ]),
                    ]),
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader('New Entry'),
                        dbc.CardBody([
                            dcc.Input(id='word-input', type='text', placeholder='Enter word...'),
                            html.Br(),  # Add a new line
                            dcc.Input(id='reflection-input', type='text', placeholder='Enter reflection...'),
                            html.Br(),  # Add a new line
                            dbc.Button('Submit', id='submit-reflection', color='success', className='mt-2'),
                        ]),
                    ]),
                ], width=6),
            ]),
            html.Br(),  # Add a new line
            dbc.Row([
                dbc.Col([
                    html.Div(id='reflection-table-content')
                ]),
            ]),
            html.Br(),  # Add a new line
            dcc.Link('Back to Dashboard', href='/dashboard', style={'color': 'blue'})  # Add backlink to the dashboard
        ]
    
    elif pathname == '/teams':
    	return [
        html.Div(
            children=[
                # My Projects section
                html.Div(
                    children=[
                        html.H2("My Projects"),
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        html.Div('Team', className='team', style={'position': 'absolute', 'top': '50%', 'left': '50%', 'transform': 'translate(-50%, -50%)'}),
                                        html.Div([html.Img(src=svg_data_url, style={'width': '60px', 'height': '60px'})], style={'position': 'relative', 'margin': '20px auto'}),
                                        html.P("Teams", style={'position': 'absolute', 'top': '80%', 'left': '50%', 'transform': 'translate(-50%, -50%)'})
                                    ],
                                    className='rectangle-1',
                                    style={'background': '#ecffda', 'border-radius': '15px', 'width': '180px', 'height': '220px', 'position': 'relative', 'box-shadow': '0px 4px 4px 0px rgba(0, 0, 0, 0.25)', 'margin': '20px 10px', 'text-align': 'center'}
                                ),
                                html.Div(
                                    children=[
                                        html.Div('Team', className='team', style={'position': 'absolute', 'top': '50%', 'left': '50%', 'transform': 'translate(-50%, -50%)'}),
                                        html.Div([html.Img(src=svg_data_url, style={'width': '60px', 'height': '60px'})], style={'position': 'relative', 'margin': '20px auto'}),
                                        html.P("Teams", style={'position': 'absolute', 'top': '80%', 'left': '50%', 'transform': 'translate(-50%, -50%)'})
                                    ],
                                    className='rectangle-1',
                                    style={'background': '#ecffda', 'border-radius': '15px', 'width': '180px', 'height': '220px', 'position': 'relative', 'box-shadow': '0px 4px 4px 0px rgba(0, 0, 0, 0.25)', 'margin': '20px 10px', 'text-align': 'center'}
                                ),
                                html.Div(
                                    children=[
                                        html.Div('Team', className='team', style={'position': 'absolute', 'top': '50%', 'left': '50%', 'transform': 'translate(-50%, -50%)'}),
                                        html.Div([html.Img(src=svg_data_url, style={'width': '60px', 'height': '60px'})], style={'position': 'relative', 'margin': '20px auto'}),
                                        html.P("Teams", style={'position': 'absolute', 'top': '80%', 'left': '50%', 'transform': 'translate(-50%, -50%)'})
                                    ],
                                    className='rectangle-1',
                                    style={'background': '#ecffda', 'border-radius': '15px', 'width': '180px', 'height': '220px', 'position': 'relative', 'box-shadow': '0px 4px 4px 0px rgba(0, 0, 0, 0.25)', 'margin': '20px 10px', 'text-align': 'center'}
                                ),
                            ],
                            style={'display': 'flex', 'justify-content': 'space-between'}
                        ),
                    ],
                    style={'width': '70%', 'margin': '20px auto 0'}  # Adjusted margin
                ),
                # Recent Words section
                html.Div(
                    children=[
                        html.H3("Recent Words"),
                        html.Div("Word 1", className='word', style={'background-color': '#b3ecff', 'border-radius': '10px', 'padding': '10px', 'margin-bottom': '10px'}),
                        html.Div("Word 2", className='word', style={'background-color': '#b3ecff', 'border-radius': '10px', 'padding': '10px', 'margin-bottom': '10px'}),
                        html.Div("Word 3", className='word', style={'background-color': '#b3ecff', 'border-radius': '10px', 'padding': '10px', 'margin-bottom': '10px'}),
                        html.Div("Word 4", className='word', style={'background-color': '#b3ecff', 'border-radius': '10px', 'padding': '10px', 'margin-bottom': '10px'}),
                        html.Div("Word 5", className='word', style={'background-color': '#b3ecff', 'border-radius': '10px', 'padding': '10px', 'margin-bottom': '10px'}),
                    ],
                    style={'margin-top': '20px', 'padding-left': '20px', 'border-left': '2px solid #ccc', 'height': 'calc(100vh - 140px)', 'overflow-y': 'auto', 'flex': '1'}
                )
            ],
            style={'display': 'flex', 'justify-content': 'space-between'}
        )
    ]


if __name__ == '__main__':
    app.run_server(debug=True)