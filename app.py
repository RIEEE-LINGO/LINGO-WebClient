import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    children=[
        # Top bar with search bar
        dbc.Row([
            dbc.Col([
                dbc.InputGroup([
                    dbc.Input(type='text', placeholder='Search...', style={'border-radius': '20px', 'margin-right': '5px'}),
                    dbc.InputGroupText(html.Img(src=dash.get_asset_url('icon.png'), style={'width': '30px', 'height': '30px', 'vertical-align': 'middle', 'order': 2})),
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
                    dbc.NavLink('Glossary', href='/glossary', id='glossary-link', style={'color': 'inherit', 'text-decoration': 'none', 'padding': '10px', 'margin-bottom': '5px'}),
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
                            dcc.Textarea(id='team-lingo-input', placeholder='Enter team-specific word/phrase'),
                            html.Div([
                                dbc.Button('Submit', id='team-submit-button', color='success', className='mt-2'),
                            ], style={'margin-top': '10px'}),
                            html.Div(id='team-lingo-display'),
                        ]),
                    ]),
                ], width=6),
            ], id='dashboard-bottom-boxes', justify='center', style={'margin-top': '20px'}),
        ]
    
	#this section down is broke for the time being, working on the glossary page 
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
            dark=True,
            responsive=True,
            striped=True,
            hover=True,
            style={'width': '90%', 'margin': '0 auto', 'background-color': 'white'},
        )
        #back button to return to dashboard!
        back_button = dcc.Link('Back to Dashboard', href='/dashboard', style={'color': 'blue'})
        return [html.H1("Glossary Content"), html.P("Shows all words and meanings."), table_content, html.Br(), back_button]
    else:
        # Default content for placeholder
        return []


if __name__ == '__main__':
    app.run_server(debug=True)
