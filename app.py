import dash
from dash import html, dcc, Input, Output, callback_context, State
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
    
    print("Status Code:", response.status_code)  # Debugging line to check the status code
    print("Response Text:", response.text)       # Debugging line to check the raw response text
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("Data received:", data)  
            df = pd.DataFrame({
                "Words": [w["word"] for w in data]  
            })
            print("DataFrame:", df)  # Debugging line to see the DataFrame structure
            return df  
        except Exception as e:
            print("Error processing data:", e)  # Print any error during data processing
            return None
    else:
        return None   
    
def fetch_reflections(endpoint, word_id, api_token):
    headers = {"Authorization": f"Bearer {api_token}"}
    full_endpoint = f"{endpoint}/api/words/{word_id}/reflections"
    response = requests.get(full_endpoint, headers=headers)
    
    print("Status Code:", response.status_code)  # Debugging line to check the status code
    print("Response Text:", response.text)       # Debugging line to check the raw response text
    
    if response.status_code == 200:
        try:
            reflections_data = response.json()
            print("Reflections Data Received:", reflections_data)  # Debugging line to check what data is received
            return reflections_data
        except Exception as e:
            print("Error processing reflections data:", e)  # Print any error during data processing
            return None
    else:
        print("Failed to fetch reflections data")
        return None

endpoint = 'https://lingo-api-server-xwzwrv5rxa-ue.a.run.app'

categories = ["word", "team", "meaning", "reflection"]

# SVG data
svg_data = """<svg xmlns="http://www.w3.org/2000/svg" width="113" height="113" viewBox="0 0 113 113" fill="none">
<circle cx="56.5" cy="56.5" r="56.5" fill="#739255"/>
</svg>"""

svg_data_url = f"data:image/svg+xml;charset=utf-8;base64,{base64.b64encode(svg_data.encode()).decode()}"

logout_button = dbc.Button("Logout", id="logout-button", color="danger", style={'background-color': '#ADD8E6'}, className="ml-2")


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
                dbc.Button("Login", id = "login-button", color="primary", style={'background-color': '#ADD8E6'}, className="ml-2"), logout_button
                
            ], width=4, style={'display': 'flex', 'justify-content': 'flex-end', 'align-items': 'center'}),
        ], style={'background': '#f2f2f2', 'padding': '10px', 'display': 'flex', 'align-items': 'center'}),

        # Welcome header
        dbc.Row([
            dbc.Col([
                html.H3("Welcome back !", id='welcome-header', style={'margin-top': '20px', 'margin-bottom': '20px'}),
            ], width=12),
        ]),
        
        html.Div(id='login_pane',hidden=True,children=[
        FirebaseAuthentication(id='firebase_auth'),
        ]),
        dcc.Interval(
        id='interval-component',
        interval=30*1000,
        n_intervals=0
    ),
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
    Output(component_id='user_display_name', component_property='children'),
    Input(component_id='firebase_auth', component_property='userDisplayName')
)
def show_display_name(userDisplayName):
    return f"Name: {userDisplayName}"
@app.callback(
    Output(component_id='user_email', component_property='children'),
    Input(component_id='firebase_auth', component_property='userEmail')
)
def show_display_name(userEmail):
    return f"Email: {userEmail}"
@app.callback(
    Output(component_id='api_token', component_property='children'),
    Input(component_id='firebase_auth', component_property='apiToken')
)
def show_display_name(apiToken):
    return f"Current Token: {apiToken}"

@app.callback(
    Output(component_id='user_profile_image', component_property='children'),
    Input(component_id='firebase_auth', component_property='userPhotoUrl')
)
def show_display_name(photoUrl):
    if photoUrl is not None and len(photoUrl.strip()) > 0:
        return [html.Img(src=photoUrl,height=100,width=100)]
    else:
        return []
@app.callback(
    Output('firebase_auth', 'user'),
    [Input('login-button', 'n_clicks'),
     Input('logout-button', 'n_clicks')],
    prevent_initial_call=True
)
def handle_login_logout(login_clicks, logout_clicks):
    if callback_context.triggered:
        # Determine which button was clicked
        button_id = callback_context.triggered[0]['prop_id'].split('.')[0]

        # Handle login
        if button_id == 'login-button' and login_clicks:
            return None  
        
        # Handle logout
        elif button_id == 'logout-button' and logout_clicks:
            return None  

    
    return dash.no_update

@app.callback(
    Output('reflection-content', 'children'),
    [Input('word-dropdown', 'value'), Input(component_id='firebase_auth', component_property='apiToken')],
)
def update_reflections(selected_word_id, apiToken):
    if selected_word_id:
        selected_word_id = int(selected_word_id)
        reflections_data = fetch_reflections(endpoint, selected_word_id, apiToken)
        if reflections_data:
            try:
                df = pd.DataFrame(reflections_data)
                df = df[['reflection', 'created_at']].rename(columns={
                    'reflection': 'Reflection',
                    'created_at': 'Created At'
                })
                table_content = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)
                return table_content
            except Exception as e:
                print(f"Error processing reflection data into DataFrame: {e}")
                return html.Div("Failed to process reflection data")
        else:
            return html.Div("No reflections found for the selected word")
    return html.Div("Select a word to see reflections")

@app.callback(
    Output('word-dropdown', 'options'),
    [Input('url', 'pathname'), Input(component_id='firebase_auth', component_property='apiToken')],
)
def update_word_options(pathname, apiToken):
    if pathname == '/reflections':
        words_data = fetch_data(endpoint, "words", apiToken)  # Endpoint that returns all words
        if not words_data.empty:  
            word_options = [{'label': word, 'value': index} for index, word in enumerate(words_data['Words'])]
            return word_options
        else:
            return []
    return []
@app.callback(
    Output('submit-message', 'children'),
    Input('submit-reflection', 'n_clicks'),
    State('word-input', 'value'),
    State('reflection-input', 'value'),
    State(component_id='firebase_auth', component_property='apiToken')
)
def submit_reflection(n_clicks, word, reflection, apiToken):
    if n_clicks:
        if word and reflection:
            endpoint = 'https://lingo-api-server-xwzwrv5rxa-ue.a.run.app'
            headers = {
                "Authorization": f"Bearer {apiToken}",
                "Content-Type": "application/json"
            }
            data = {
                "word": word,
                "reflection": reflection
            }
            response = requests.post(f"{endpoint}/api/reflections", json=data, headers=headers)
            if response.status_code == 200:
                return html.Div("Reflection submitted successfully!", style={'color': 'green'})
            else:
                return html.Div(f"Failed to submit reflection. Error: {response.text}", style={'color': 'red'})
        else:
            return html.Div("Please enter both word and reflection before submitting.", style={'color': 'red'})
    return html.Div()

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    Input(component_id='firebase_auth', component_property='apiToken')
)
def update_page_content(pathname, apiToken):
    if pathname == '/dashboard':
        return [
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader('User Profile'),
                        dbc.CardBody([
                            html.Div([
                                html.Div(id='user_profile_image'),  # Placeholder for the user image
                                html.H3(id='user_display_name', style={'marginTop': '20px'}),  # Display user name
                                html.P(id='user_email'),  # Display user email
                            ], style={'textAlign': 'center'}),
                        ]),
                    ]),
                ], width=6),
            ], id='dashboard-center-boxes', justify='start', style={'margin-top': '20px'}),
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
        return html.Div([
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Reflections"),
                                dbc.CardBody([
                                    dcc.Dropdown(
                                        id='word-dropdown',
                                        options=[],  
                                        value=2,
                                        placeholder='Select a word...',
                                        style={'margin-bottom': '10px'}
                                    ),
                                html.Div(id='reflection-content')  
                                ])
                            ])
                        ], width=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("New Entry"),
                            dbc.CardBody([
                                dcc.Input(id='word-input', type='text', placeholder='Enter word...', style={'margin-top': '10px'}),
                                dcc.Input(id='reflection-input', type='text', placeholder='Enter reflection...', style={'margin-top': '10px'}),
                                html.Button('Submit', id='submit-reflection', n_clicks=0, className='btn btn-success', style={'margin-top': '10px'})
                            ])
                        ])
                    ], width=6)
                    ])
                ]) 

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





