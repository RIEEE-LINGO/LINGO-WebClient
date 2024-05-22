import dash
from dash import html, dcc, Input, Output, callback_context, State
import dash_bootstrap_components as dbc
import base64, requests
import requests
import pandas as pd
from firebase_authentication import FirebaseAuthentication
from urllib.parse import urlparse, parse_qs

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://www.gstatic.com/firebasejs/ui/6.1.0/firebase-ui-auth.css"  # For Firebase Auth styling
    ],
    suppress_callback_exceptions=True
)


def configure_headers(api_token):
    headers = {"Authorization": f"Bearer {api_token}"}
    return headers


def configure_headers_with_body(api_token):
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    return headers


def fetch_words(api_token):
    headers = configure_headers(api_token)
    full_endpoint = f"{endpoint}/api/words"
    response = requests.get(full_endpoint, headers=headers)

    print("Status Code:", response.status_code)  # Debugging line to check the status code
    print("Response Text:", response.text)  # Debugging line to check the raw response text

    if response.status_code == 200:
        try:
            ids = []
            words = []

            data = response.json()
            return data
            # print("Data received:", data)
            #
            # for w in data:
            #     ids.append(w["id"])
            #     words.append(w["word"])
            #
            # df = pd.DataFrame({
            #     "Id": ids,
            #     "Word": words
            # })
            #
            # print("DataFrame:", df)  # Debugging line to see the DataFrame structure
            # return df
        except Exception as e:
            print("Error processing data:", e)  # Print any error during data processing
            return None
    else:
        return None


def fetch_reflections(word_id, api_token):
    headers = configure_headers(api_token)
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
        print("Failed to fetch reflections data, please try refreshing your browser.")
        return None


def fetch_meanings(word_id, api_token):
    headers = configure_headers(api_token)
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
        print("Failed to fetch meanings data, please try refreshing your browser.")
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
        dcc.Store(id='lingo-reflections-updated'),
        dcc.Store(id='lingo-meanings-updated'),
        dcc.Store(id='user-logged-in', storage_type='session'),
        html.Div(
            id='alert-bar-div'
        ),
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
                        dbc.NavLink('Words', href='/glossary', id='glossary-link', active='exact',
                                    style={'color': 'inherit', 'textDecoration': 'none', 'padding': '10px',
                                           'marginBottom': '5px'})),
                    dbc.NavItem(
                        dbc.NavLink('Meanings and Reflections', href='/reflections', id='reflections-link',
                                    active='exact',
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
def show_user_email(user_email):
    return f"Email: {user_email}"


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
def show_profile_image(photo_url):
    if photo_url is not None and len(photo_url.strip()) > 0:
        return [html.Img(src=photo_url, height=100, width=100)]
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
    Input('url', 'pathname'),
    Input('word-dropdown', 'value'),
    Input(component_id='firebase_auth', component_property='apiToken'),
    Input('lingo-reflections-updated', 'data')
)
def update_reflections(pathname, selected_word_id, api_token, reflections_updated_flag):
    if pathname == '/reflections':
        if selected_word_id is not None:
            reflections_data = fetch_reflections(selected_word_id, api_token)
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
    return html.Div("")


@app.callback(
    Output('meaning-content', 'children'),
    Input('url', 'pathname'),
    Input('word-dropdown', 'value'),
    Input(component_id='firebase_auth', component_property='apiToken'),
    Input('lingo-meanings-updated', 'data')
)
def update_meanings(pathname, selected_word_id, api_token, meanings_updated_flag):
    if pathname == '/reflections':
        if selected_word_id is not None:
            meanings_data = fetch_meanings(selected_word_id, api_token)
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
    return html.Div("")


@app.callback(
    Output('word-dropdown', 'options'),
    Output('word-dropdown', 'value'),
    Input('url', 'pathname'),
    Input('url', 'search'),
    Input(component_id='firebase_auth', component_property='apiToken'),
)
def update_word_options(pathname, search, api_token):
    if pathname == '/reflections':
        query_params = {}
        if len(search) > 1:
            query_params = parse_qs(search[1:])

        words_data = fetch_words(api_token)  # Endpoint that returns all words
        if words_data is not None:
            word_options = [{'label': word['word'], 'value': word['id']} for word in words_data]
            if 'word' in query_params and query_params['word'] is not None:
                query_word = query_params['word']
                if type(query_word) is list and len(query_word) > 0:
                    query_word = int(query_word[0])
                else:
                    query_word = int(query_word)
                return word_options, query_word
            else:
                return word_options, 0
        else:
            return [], 0
    return [], 0


@app.callback(
    Output('submit-word-message', 'children'),
    Output('lingo-words-updated', 'data'),
    Input('submit-word', 'n_clicks'),
    State('word-input', 'value'),
    State('firebase_auth', 'apiToken'),
    prevent_initial_call=True
)
def submit_word(n_clicks, word, api_token):
    if word is not None:
        endpoint = 'https://lingo-api-server-xwzwrv5rxa-ue.a.run.app'
        headers = configure_headers_with_body(api_token)
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
    Output('alert-bar-div', 'children'),
    Output('meaning-input', 'value'),
    Output('lingo-meanings-updated', 'data'),
    Input('submit-meaning', 'n_clicks'),
    State('word-dropdown', 'value'),
    State('meaning-input', 'value'),
    State('firebase_auth', 'apiToken'),
    prevent_initial_call=True
)
def submit_meaning(n_clicks, word_id, meaning, api_token):
    if n_clicks:
        if word_id is not None and meaning is not None:
            headers = configure_headers_with_body(api_token)
            data = {
                "meaning": meaning
            }
            response = requests.post(f"{endpoint}/api/words/{word_id}/meanings", json=data, headers=headers)
            if response.status_code == 200 or response.status_code == 201:
                return (dbc.Alert("Meaning submitted successfully!",
                                  is_open=True,
                                  dismissable=True,
                                  color="success",
                                  duration=4000),
                        '',
                        n_clicks)
            else:
                return (dbc.Alert(f"Failed to submit meaning. Error: {response.text}",
                                  is_open=True,
                                  dismissable=True,
                                  color="danger"),
                        meaning,
                        n_clicks)
        else:
            return (
                dbc.Alert("Please select a word and enter a meaning before submitting.",
                          is_open=True,
                          dismissable=True,
                          color="warning",
                          duration=4000),
                meaning,
                n_clicks)
    return html.Div(), meaning, n_clicks


@app.callback(
    Output('submit-reflection-message', 'children'),
    Output('reflection-input', 'value'),
    Output('lingo-reflections-updated', 'data'),
    Input('submit-reflection', 'n_clicks'),
    State('word-dropdown', 'value'),
    State('reflection-input', 'value'),
    State('firebase_auth', 'apiToken'),
    prevent_initial_call=True
)
def submit_reflection(n_clicks, word_id, reflection, api_token):
    if n_clicks:
        if word_id is not None and reflection is not None:
            headers = configure_headers_with_body(api_token)
            data = {
                "reflection": reflection
            }
            response = requests.post(f"{endpoint}/api/words/{word_id}/reflections", json=data, headers=headers)
            if response.status_code == 200 or response.status_code == 201:
                return html.Div("Reflection submitted successfully!", style={'color': 'green'}), '', n_clicks
            else:
                return (html.Div(f"Failed to submit reflection. Error: {response.text}", style={'color': 'red'}),
                        reflection,
                        n_clicks)
        else:
            return (html.Div("Please select a word and enter a reflection before submitting.", style={'color': 'red'}),
                    reflection,
                    n_clicks)
    return html.Div(), reflection, n_clicks


@app.callback(
    Output('submit-meaning', 'disabled'),
    Input('word-dropdown', 'value'),
    Input('meaning-input', 'value')
)
def update_submit_meaning_button(word_value, meaning_input):
    return word_value is None or word_value == 0 or meaning_input is None or len(meaning_input.strip()) == 0


@app.callback(
    Output('submit-reflection', 'disabled'),
    Input('word-dropdown', 'value'),
    Input('reflection-input', 'value')
)
def update_submit_reflection_button(word_value, reflection_input):
    return word_value is None or word_value == 0 or reflection_input is None or len(reflection_input.strip()) == 0


@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    Input('url', 'search'),
    Input('firebase_auth', 'apiToken'),
    # Input('lingo-words-updated', 'data'),
    # Input('lingo-meanings-updated', 'data'),
    # Input('lingo-reflections-updated', 'data')
)
def update_page_content(pathname, search, apiToken):
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
        data = fetch_words(apiToken)
        word_contents = html.Div("Failed to retrieve data, please try refreshing your browser.")
        if data is not None:
            table_header = [
                # html.Thead(html.Tr([html.Th("Word")]))
            ]
            rows = []
            for word in data:
                rows.append(
                    html.Tr([html.Td(dcc.Link(href=f'/reflections?word={word["id"]}', children=[word["word"]]))]))
            table_body = [html.Tbody(rows)]
            table_content = dbc.Table(table_header + table_body, striped=True, bordered=True, hover=True)
            # table_content = dbc.Table.from_dataframe(data, striped=True, bordered=True, hover=True)
            word_contents = html.Div([table_content])
        return html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Words"),
                        dbc.CardBody([
                            word_contents
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("New Word"),
                        dbc.CardBody([
                            dcc.Input(id='word-input', type='text', placeholder='Enter word...',
                                      style={'width': '80%', 'marginTop': '10px'})
                        ]),
                        dbc.CardBody([
                            html.Button('Submit', id='submit-word', n_clicks=0, className='btn btn-success',
                                        style={'marginTop': '-20px'})
                        ]),
                        dbc.CardBody([
                            html.Div(id='submit-word-message')
                        ])
                    ])
                ], width=6)
            ])
        ])
    elif pathname == '/reflections':
        query_params = {}
        if len(search) > 1:
            query_params = parse_qs(search[1:])
        return html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Meanings and Reflections"),
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
                        dbc.CardHeader("New Meaning"),
                        dbc.CardBody([
                            dcc.Textarea(id='meaning-input', placeholder='Enter meaning...',
                                         style={'width': '80%', 'marginTop': '10px'})
                        ]),
                        dbc.CardBody([
                            html.Button('Submit',
                                        id='submit-meaning',
                                        disabled=True,
                                        className='btn btn-success',
                                        style={'marginTop': '-20px'})
                        ]),
                        dbc.CardBody([
                            html.Div(id='submit-meaning-message')
                        ])
                    ]),
                    dbc.Card([
                        dbc.CardHeader("New Reflection"),
                        dbc.CardBody([
                            dcc.Textarea(id='reflection-input', placeholder='Enter reflection...',
                                         style={'width': '80%', 'marginTop': '10px'})
                        ]),
                        dbc.CardBody([
                            html.Button('Submit',
                                        id='submit-reflection',
                                        disabled=True,
                                        className='btn btn-success',
                                        style={'marginTop': '-20px'})
                        ]),
                        dbc.CardBody([
                            html.Div(id='submit-reflection-message')
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
