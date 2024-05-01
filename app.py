import dash
from dash import html, dcc, Input, Output, callback_context, State
import dash_bootstrap_components as dbc
import base64, requests
import requests
import pandas as pd
from firebase_authentication import FirebaseAuthentication

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://www.gstatic.com/firebasejs/ui/6.1.0/firebase-ui-auth.css"  # For Firebase Auth styling
    ],
    suppress_callback_exceptions=True
)


def fetch_data(endpoint, resource, api_token):
    headers = {"Authorization": f"Bearer {api_token}"}
    full_endpoint = f"{endpoint}/api/{resource}"
    response = requests.get(full_endpoint, headers=headers)

    print("Status Code:", response.status_code)  # Debugging line to check the status code
    print("Response Text:", response.text)  # Debugging line to check the raw response text

    if response.status_code == 200:
        try:
            data = response.json()
            print("Data received:", data)
            # Note: it would be faster to run the list once, but the list should be
            # quite short so there is probably little difference...
            df = pd.DataFrame({
                "Ids": [w["id"] for w in data],
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
    print("Response Text:", response.text)  # Debugging line to check the raw response text

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


def fetch_meanings(endpoint, word_id, api_token):
    headers = {"Authorization": f"Bearer {api_token}"}
    full_endpoint = f"{endpoint}/api/words/{word_id}/meanings"
    response = requests.get(full_endpoint, headers=headers)

    print("Status Code:", response.status_code)  # Debugging line to check the status code
    print("Response Text:", response.text)  # Debugging line to check the raw response text

    if response.status_code == 200:
        try:
            meanings_data = response.json()
            print("Meanings Data Received:", meanings_data)  # Debugging line to check what data is received
            return meanings_data
        except Exception as e:
            print("Error processing meanings data:", e)  # Print any error during data processing
            return None
    else:
        print("Failed to fetch meanings data")
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
        dcc.Store(id='lingo-words-updated'),
        dcc.Store(id='user-logged-in', storage_type='session'),
        # Top bar with search bar
        dbc.Row([
            dbc.Col([
                dbc.InputGroup([
                    dbc.Input(type='text', id='search-bar', placeholder='Search...',
                              style={'borderRadius': '20px', 'marginRight': '5px'}),
                    html.Img(src=dash.get_asset_url('rieee.png'),
                             style={'width': '33px', 'height': '33px', 'verticalAlign': '', 'order': 2,
                                    'background': 'transparent'}),
                ]),
            ], width=8),
            dbc.Col([
                html.Div(
                    id='login-button-div', children=[
                        dbc.Button("Login", id="login-button", color="primary", style={'backgroundColor': '#ADD8E6'},
                                   className="ml-2")
                    ], hidden=False
                ),
                html.Div(
                    id='logout-button-div', children=[
                        dbc.Button("Logout", id="logout-button", color="danger", style={'backgroundColor': '#ADD8E6'},
                                   className="ml-2")
                    ], hidden=False
                )
            ], width=4, style={'display': 'flex', 'justifyContent': 'flex-end', 'alignItems': 'center'}),
        ], style={'background': '#f2f2f2', 'padding': '10px', 'display': 'flex', 'alignItems': 'center'}),

        # Welcome header
        dbc.Row([
            dbc.Col([
                html.H3("Welcome back !", id='welcome-header', style={'marginTop': '20px', 'marginBottom': '20px'}),
            ], width=12),
        ]),

        html.Div(id='login_pane', hidden=True, children=[
            FirebaseAuthentication(id='firebase_auth'),
        ]),
        dcc.Interval(
            id='interval-component',
            interval=30 * 1000,
            n_intervals=0
        ),
        # Navigation and content
        dbc.Row([
            dbc.Col([
                dbc.Nav([
                    dbc.NavItem(
                        dbc.NavLink('Dashboard', href='/', id='dashboard-link', active='exact',
                                    style={'color': 'inherit', 'textDecoration': 'none', 'padding': '10px',
                                           'marginBottom': '5px'})),
                    dbc.NavItem(
                        dbc.NavLink('New Entry', href='/glossary', id='glossary-link', active='exact',
                                    style={'color': 'inherit', 'textDecoration': 'none', 'padding': '10px',
                                           'marginBottom': '5px'})),
                    dbc.NavItem(
                        dbc.NavLink('Reflections', href='/reflections', id='reflections-link', active='exact',
                                    style={'color': 'inherit', 'textDecoration': 'none', 'padding': '10px',
                                           'marginBottom': '5px'})),
                    dbc.NavItem(dbc.NavLink('Teams', href='/teams', id='teams-link', active='exact',
                                            style={'color': 'inherit', 'textDecoration': 'none', 'padding': '10px',
                                                   'marginBottom': '5px'})),
                ], vertical=True, pills=True,
                    style={'background': '#f2f2f2', 'borderRadius': '10px', 'padding': '20px',
                           'height': 'calc(100vh - 140px)', 'position': 'sticky', 'top': '20px'}),
            ], width=2),

            dbc.Col([
                dcc.Location(id='url', refresh=False),
                html.Div(id='page-content'),
            ], width=10),
        ]),
    ], style={'marginLeft': '20px'}
)


@app.callback(
    Output(component_id='user_display_name', component_property='children'),
    Input(component_id='firebase_auth', component_property='userDisplayName'),
)
def show_display_name(userDisplayName):
    return f"Name: {userDisplayName}"


@app.callback(
    Output('user-logged-in', 'data', allow_duplicate=True),
    Input(component_id='firebase_auth', component_property='userDisplayName'),
    prevent_initial_call=True
)
def store_display_name(userDisplayName):
    return userDisplayName

@app.callback(
    Output(component_id='user_email', component_property='children'),
    Input(component_id='firebase_auth', component_property='userEmail'),
)
def show_user_email(userEmail):
    return f"Email: {userEmail}"


# @app.callback(
#     Output(component_id='user-logged-in', component_property='data'),
#     Input(component_id='firebase_auth', component_property='apiToken')
# )
# def show_api_token(api_token):
#     return api_token


@app.callback(
    Output(component_id='user_profile_image', component_property='children'),
    Input(component_id='firebase_auth', component_property='userPhotoUrl'),
)
def show_profile_image(photoUrl):
    if photoUrl is not None and len(photoUrl.strip()) > 0:
        return [html.Img(src=photoUrl, height=100, width=100)]
    else:
        return []


@app.callback(
    Output(component_id='login-button-div', component_property='hidden'),
    Input(component_id='user-logged-in', component_property='data')
)
def show_login_button(display_name):
    if display_name is None or len(display_name.strip()) == 0:
        return False
    else:
        return True


@app.callback(
    Output(component_id='logout-button-div', component_property='hidden'),
    Input(component_id='user-logged-in', component_property='data')
)
def show_logout_button(display_name):
    if display_name is None or len(display_name.strip()) == 0:
        return True
    else:
        return False


@app.callback(
    Output(component_id='firebase_auth', component_property='logoutFlag'),
    Output(component_id='user-logged-in', component_property='data', allow_duplicate=True),
    Input(component_id='logout-button', component_property='n_clicks'),
    prevent_initial_call=True
)
def logout_perform_logout(input_value):
    return True, ''


@app.callback(
    Output(component_id='login_pane', component_property='hidden', allow_duplicate=True),
    Input(component_id='login-button', component_property='n_clicks'),
    prevent_initial_call=True
)
def login_show_login_pane(input_value):
    return False


@app.callback(
    Output('reflection-content', 'children'),
    [Input('word-dropdown', 'value'), Input(component_id='firebase_auth', component_property='apiToken')],
)
def update_reflections(selected_word_id, apiToken):
    if selected_word_id is not None:
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
    Output('meaning-content', 'children'),
    [Input('word-dropdown', 'value'), Input(component_id='firebase_auth', component_property='apiToken')],
)
def update_meanings(selected_word_id, apiToken):
    if selected_word_id is not None:
        selected_word_id = int(selected_word_id)
        meanings_data = fetch_meanings(endpoint, selected_word_id, apiToken)
        if meanings_data:
            try:
                df = pd.DataFrame(meanings_data)
                df = df[['meaning', 'created_at']].rename(columns={
                    'meaning': 'Meaning',
                    'created_at': 'Created At'
                })
                table_content = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)
                return table_content
            except Exception as e:
                print(f"Error processing meaning data into DataFrame: {e}")
                return html.Div("Failed to process meaning data")
        else:
            return html.Div("No meanings found for the selected word")
    return html.Div("Select a word to see meanings")


@app.callback(
    Output('word-dropdown', 'options'),
    [Input('url', 'pathname'), Input(component_id='firebase_auth', component_property='apiToken')],
)
def update_word_options(pathname, apiToken):
    if pathname == '/reflections':
        words_data = fetch_data(endpoint, "words", apiToken)  # Endpoint that returns all words
        if words_data is not None:
            word_options = [{'label': word, 'value': index} for index, word in enumerate(words_data['Words'])]
            return word_options
        else:
            return []
    return []


@app.callback(
    Output('submit-word-message', 'children'),
    Output('lingo-words-updated', 'data'),
    Input('submit-word', 'n_clicks'),
    State('word-input', 'value'),
    State('firebase_auth', 'apiToken'),
    prevent_initial_call=True
)
def submit_word(n_clicks, word, apiToken):
    if word is not None:
        endpoint = 'https://lingo-api-server-xwzwrv5rxa-ue.a.run.app'
        headers = {
            "Authorization": f"Bearer {apiToken}",
            "Content-Type": "application/json"
        }
        data = {
            "word": word,
            "project": 1
        }
        response = requests.post(f"{endpoint}/api/words", json=data, headers=headers)
        if response.status_code == 201:
            return html.Div("Word submitted successfully!", style={'color': 'green'}), n_clicks
        else:
            return html.Div(f"Failed to submit word. Error: {response.text}", style={'color': 'red'}), n_clicks
    else:
        if n_clicks > 0:
            return html.Div("Please enter a word before submitting.", style={'color': 'red'}), n_clicks
        else:
            return html.Div([]), n_clicks


@app.callback(
    Output('submit-message', 'children'),
    Input('submit-reflection', 'n_clicks'),
    State('word-input', 'value'),
    State('reflection-input', 'value'),
    State('firebase_auth', 'apiToken'),
    prevent_initial_call=True
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
    Input(component_id='firebase_auth', component_property='apiToken'),
    Input('lingo-words-updated', 'data')
)
def update_page_content(pathname, apiToken, word_update_counter):
    if pathname == '/':
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
            ], id='dashboard-center-boxes', justify='start', style={'marginTop': '20px'}),
        ]

    elif pathname == '/glossary':
        data = fetch_data(endpoint, "words", apiToken)
        word_contents = html.Div("Failed to fetch data from API")
        if data is not None:
            table_content = dbc.Table.from_dataframe(data, striped=True, bordered=True, hover=True)
            word_contents = html.Div([table_content])
        return html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Glossary"),
                        dbc.CardBody([
                            word_contents
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("New Entry"),
                        dbc.CardBody([
                            dcc.Input(id='word-input', type='text', placeholder='Enter word...',
                                      style={'marginTop': '10px', 'marginRight': '10px'}),
                            html.Button('Submit', id='submit-word', n_clicks=0, className='btn btn-success',
                                        style={'marginTop': '10px'}),
                            html.Div(id='submit-word-message')
                        ])
                    ])
                ], width=6)
            ])
        ])
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
                                placeholder='Select a word...',
                                style={'marginBottom': '10px'}
                            ),
                            html.Div(id='meaning-content'),
                            html.Div(id='reflection-content')

                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("New Reflection"),
                        dbc.CardBody([
                            dcc.Input(id='word-input', type='text', placeholder='Enter word...',
                                      style={'marginTop': '10px'}),
                            dcc.Input(id='reflection-input', type='text', placeholder='Enter reflection...',
                                      style={'marginTop': '10px'}),
                            html.Button('Submit', id='submit-reflection', n_clicks=0, className='btn btn-success',
                                        style={'marginTop': '10px'}),
                            html.Div(id='submit-message')
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
                                    html.Div('Team', className='team',
                                             style={'position': 'absolute', 'top': '50%', 'left': '50%',
                                                    'transform': 'translate(-50%, -50%)'}),
                                    html.Div([html.Img(src=svg_data_url, style={'width': '60px', 'height': '60px'})],
                                             style={'position': 'relative', 'margin': '20px auto'}),
                                    html.P("Teams", style={'position': 'absolute', 'top': '80%', 'left': '50%',
                                                           'transform': 'translate(-50%, -50%)'})
                                ],
                                className='rectangle-1',
                                style={'background': '#ecffda', 'borderRadius': '15px', 'width': '180px',
                                       'height': '220px', 'position': 'relative',
                                       'box-shadow': '0px 4px 4px 0px rgba(0, 0, 0, 0.25)', 'margin': '20px 10px',
                                       'text-align': 'center'}
                            ),
                            html.Div(
                                children=[
                                    html.Div('Team', className='team',
                                             style={'position': 'absolute', 'top': '50%', 'left': '50%',
                                                    'transform': 'translate(-50%, -50%)'}),
                                    html.Div([html.Img(src=svg_data_url, style={'width': '60px', 'height': '60px'})],
                                             style={'position': 'relative', 'margin': '20px auto'}),
                                    html.P("Teams", style={'position': 'absolute', 'top': '80%', 'left': '50%',
                                                           'transform': 'translate(-50%, -50%)'})
                                ],
                                className='rectangle-1',
                                style={'background': '#ecffda', 'borderRadius': '15px', 'width': '180px',
                                       'height': '220px', 'position': 'relative',
                                       'box-shadow': '0px 4px 4px 0px rgba(0, 0, 0, 0.25)', 'margin': '20px 10px',
                                       'text-align': 'center'}
                            ),
                            html.Div(
                                children=[
                                    html.Div('Team', className='team',
                                             style={'position': 'absolute', 'top': '50%', 'left': '50%',
                                                    'transform': 'translate(-50%, -50%)'}),
                                    html.Div([html.Img(src=svg_data_url, style={'width': '60px', 'height': '60px'})],
                                             style={'position': 'relative', 'margin': '20px auto'}),
                                    html.P("Teams", style={'position': 'absolute', 'top': '80%', 'left': '50%',
                                                           'transform': 'translate(-50%, -50%)'})
                                ],
                                className='rectangle-1',
                                style={'background': '#ecffda', 'borderRadius': '15px', 'width': '180px',
                                       'height': '220px', 'position': 'relative',
                                       'box-shadow': '0px 4px 4px 0px rgba(0, 0, 0, 0.25)', 'margin': '20px 10px',
                                       'text-align': 'center'}
                            ),
                        ],
                        style={'display': 'flex', 'justifyContent': 'space-between'}
                    ),
                ],
                style={'width': '70%', 'margin': '20px auto 0'}
            ),
            html.Div(
                children=[
                    html.H3("Recent Words"),
                    html.Div("Word 1", className='word',
                             style={'backgroundColor': '#b3ecff', 'borderRadius': '10px', 'padding': '10px',
                                    'marginBottom': '10px'}),
                    html.Div("Word 2", className='word',
                             style={'backgroundColor': '#b3ecff', 'borderRadius': '10px', 'padding': '10px',
                                    'marginBottom': '10px'}),
                    html.Div("Word 3", className='word',
                             style={'backgroundColor': '#b3ecff', 'borderRadius': '10px', 'padding': '10px',
                                    'marginBottom': '10px'}),
                    html.Div("Word 4", className='word',
                             style={'backgroundColor': '#b3ecff', 'borderRadius': '10px', 'padding': '10px',
                                    'marginBottom': '10px'}),
                    html.Div("Word 5", className='word',
                             style={'backgroundColor': '#b3ecff', 'borderRadius': '10px', 'padding': '10px',
                                    'marginBottom': '10px'}),
                ],
                style={'marginTop': '20px', 'padding-left': '20px', 'border-left': '2px solid #ccc',
                       'height': 'calc(100vh - 140px)', 'overflow-y': 'auto', 'flex': '1'}
            )
        ]
        pass


if __name__ == '__main__':
    app.run_server(debug=True)
