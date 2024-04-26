import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import base64, requests
import requests
import pandas as pd
from firebase_authentication import FirebaseAuthentication


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)


def fetch_data(endpoint, resource, api_token):
    headers = {"Authorization": f"Bearer {api_token}"}
    full_endpoint = f"{endpoint}/api/{resource}"
    response = requests.get(full_endpoint, headers=headers)
    
    # Check and print the status code
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)
    
    if response.status_code == 200:
        df = pd.DataFrame({
        	"Words": [ w["word"] for w in response.json() ]
    	})
        return df  
    else:
        return None  

endpoint = 'https://lingo-api-server-xwzwrv5rxa-ue.a.run.app'

categories = ["word", "team", "meaning", "reflection"]

# SVG data
svg_data = """<svg xmlns="http://www.w3.org/2000/svg" width="113" height="113" viewBox="0 0 113 113" fill="none">
<circle cx="56.5" cy="56.5" r="56.5" fill="#739255"/>
</svg>"""

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
            ], width=8),
            dbc.Col([
                dbc.Button("Login", color="primary", style={'background-color': '#ADD8E6'}, className="ml-2"),
            ], width=4, style={'display': 'flex', 'justify-content': 'flex-end', 'align-items': 'center'}),
        ], style={'background': '#f2f2f2', 'padding': '10px', 'display': 'flex', 'align-items': 'center'}),

        # Welcome header
        dbc.Row([
            dbc.Col([
                html.H3("Welcome back !", id='welcome-header', style={'margin-top': '20px', 'margin-bottom': '20px'}),
            ], width=12),
        ]),
        
        dbc.Row([
            dbc.Col([
		        html.Div(id='login_pane',hidden=True,children=[
        			FirebaseAuthentication(id='firebase_auth'),
    			])
            ], width=12),
        ]),

        # Navigation and content
        dbc.Row([
            dbc.Col([
                dbc.Nav([
                    dbc.NavLink('Dashboard', href='/dashboard', id='dashboard-link', style={'color': 'inherit', 'text-decoration': 'none', 'padding': '10px', 'margin-bottom': '5px'}),
                    dbc.NavLink('Overall Meanings', href='/glossary', id='glossary-link', style={'color': 'inherit', 'text-decoration': 'none', 'padding': '10px', 'margin-bottom': '5px'}),
                    dbc.NavLink('New Entry', href='/reflections', id='reflections-link', style={'color': 'inherit', 'text-decoration': 'none', 'padding': '10px', 'margin-bottom': '5px'}),
                    dbc.NavLink('Teams', href='/teams', id='teams-link', style={'color': 'inherit', 'text-decoration': 'none', 'padding': '10px', 'margin-bottom': '5px'}),
                ], vertical=True, pills=True, style={'background': '#f2f2f2', 'border-radius': '10px', 'padding': '20px', 'height': 'calc(100vh - 140px)', 'position': 'sticky', 'top': '20px'}),
            ], width=2),

            
            dbc.Col([
                dcc.Location(id='url', refresh=False),
                html.Div(id='page-content'),
            ], width=10),
        ]),
    ], style={'margin-left': '20px'}
)  




@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    Input(component_id='firebase_auth', component_property='apiToken')
)
def update_page_content(pathname, apiToken):
    if pathname == '/dashboard':
        team_data = fetch_data(endpoint, "teams", apiToken)
        profile_data = fetch_data(endpoint, "profiles", apiToken) 
        team_name = team_data.iloc[0]['TeamName'] if not team_data.empty else "No Team Data"
        user_profile = profile_data.iloc[0]['Username'] if not profile_data.empty else "No Profile Data"
        return [
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader('Teams'),
                        dbc.CardBody([
                            html.Label('Current Team'),
                            html.Div(f"Team Name: {team_name}", id='current-team-display'),
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
            ], id='dashboard-center-boxes', justify='left', style={'margin-top': '20px'}),
        ]
        
        
        
    elif pathname == '/glossary':
        # token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImEyMzhkZDA0Y2JhYTU4MGIzMDRjODgxZTFjMDA4ZWMyOGZiYmFkZGMiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiRWxsZSBSdXNzZWxsIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0pEMGk1enJpZ1p1VGd3c3FhMTZkdEF5bUppRDF2T1NMWWh5bFRFTUVQWVpTSVk2YWM9czk2LWMiLCJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vbGluZ28tNWJjMWEiLCJhdWQiOiJsaW5nby01YmMxYSIsImF1dGhfdGltZSI6MTcxMzg5NjQxNywidXNlcl9pZCI6InJoSUk5OXBsSTRXZHY5UjlwWUNodUw5SjluMTMiLCJzdWIiOiJyaElJOTlwbEk0V2R2OVI5cFlDaHVMOUo5bjEzIiwiaWF0IjoxNzEzODk2NDE3LCJleHAiOjE3MTM5MDAwMTcsImVtYWlsIjoicnVzc2VsbGVtQGFwcHN0YXRlLmVkdSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7Imdvb2dsZS5jb20iOlsiMTA2ODg0MDMwMTc0NDI1MDM0NDU5Il0sImVtYWlsIjpbInJ1c3NlbGxlbUBhcHBzdGF0ZS5lZHUiXX0sInNpZ25faW5fcHJvdmlkZXIiOiJnb29nbGUuY29tIn19.1QYVZm7HgJ5tFQZ3QRMyn6aD4p2ily53zb28BSPv6As9jn4henwTE9we9TaBbdC9uYjqJleYxQ8I8cJJ9eEDAfSpnYUGaGFB8RnRdD6LGIUhWYkeSkCQ-6sekI1I0ssLq-yUApoW-QRtNgOx6QZiu-RsZzVuExUcxipTH30-Sxox-wqgaz3s9EB9KKPEo9RAVOka_FAbU8IHR6mZM6SMMEJJuC_qrF47W7Ym2oo5Emqm9H_h_sR6CRo0Eh86Xa5SSwVSdD770zszJi9gdB2IJM_62cNBSGmLRVCNYi87WD74oA9Hu8Efx7jBPHudEfdKwx7lwAwd7TY8HaldNY2BGg"
        data = fetch_data(endpoint, "words", apiToken) 
        if data is not None:
            table_content = dbc.Table.from_dataframe(data, striped=True, bordered=True, hover=True)
            return html.Div([html.H1("Glossary"), table_content])
        else:
            return html.Div("Failed to fetch data from API")

    elif pathname == '/reflections':
        data = fetch_data(endpoint, "reflections")
        if data:
            word_options = [{'label': entry["Word"], 'value': entry["Word"]} for entry in data]
            word_dropdown = dcc.Dropdown(
                id='word-dropdown',
                options=word_options,
                placeholder='Select a word...',
                style={'margin-bottom': '10px'}
            )
            table_content = dbc.Table(
                id='selected-word-table',
                data=[{'label': entry['Word']} for entry in data],
                columns=[{"name": "Word", "id": "Word"}],
                bordered=True,
                dark=False,
                responsive=True,
                striped=True,
                hover=True,
            )
            word_input = dcc.Input(id='word-input', type='text', placeholder='Enter word...')
            reflection_input = dcc.Input(id='reflection-input', type='text', placeholder='Enter reflection...')
            submit_button = dbc.Button('Submit', id='submit-reflection', color='success', className='mt-2')
            return html.Div([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader('Reflections'),
                            dbc.CardBody([
                                word_dropdown,
                                table_content
                            ]),
                        ]),
                    ], width=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader('New Entry'),
                            dbc.CardBody([
                                word_input,
                                html.Br(),
                                reflection_input,
                                html.Br(),
                                submit_button,
                            ]),
                        ]),
                    ], width=6),
                ]),
            ])
        else:
            return html.Div("Failed to fetch data from API")

    elif pathname == '/teams':
        return [
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
                style={'width': '70%', 'margin': '20px auto 0'}  
            ),
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
        ]
        pass
    

if __name__ == '__main__':
    app.run_server(debug=True)
