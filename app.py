from math import trunc

import dash
from dash import html, dcc, Input, Output, callback_context, State, ALL, ctx
import dash_bootstrap_components as dbc
import base64, requests
import requests
import pandas as pd
from firebase_authentication import FirebaseAuthentication
from urllib.parse import urlparse, parse_qs
from config import api_server_url

# The location of the API server
endpoint = api_server_url

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        # "https://www.gstatic.com/firebasejs/ui/6.1.0/firebase-ui-auth.css"  # For Firebase Auth styling
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

    # print("Status Code:", response.status_code)  # Debugging line to check the status code
    # print("Response Text:", response.text)  # Debugging line to check the raw response text

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


def fetch_team_words(api_token, team_id):
    headers = configure_headers(api_token)
    full_endpoint = f"{endpoint}/api/teams/{team_id}/words"
    response = requests.get(full_endpoint, headers=headers)

    # print("Status Code:", response.status_code)  # Debugging line to check the status code
    # print("Response Text:", response.text)  # Debugging line to check the raw response text

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
            print("Error processing team words:", e)  # Print any error during data processing
            return None
    else:
        return None


def fetch_reflections(word_id, api_token):
    headers = configure_headers(api_token)
    full_endpoint = f"{endpoint}/api/words/{word_id}/reflections"
    response = requests.get(full_endpoint, headers=headers)

    # print("Status Code:", response.status_code)  # Debugging line to check the status code
    # print("Response Text:", response.text)  # Debugging line to check the raw response text

    if response.status_code == 200:
        try:
            reflections_data = response.json()
            # print("Reflections Data Received:", reflections_data)  # Debugging line to check what data is received
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

    # print("Status Code:", response.status_code)  # Debugging line to check the status code
    # print("Response Text:", response.text)  # Debugging line to check the raw response text

    if response.status_code == 200:
        try:
            meanings_data = response.json()
            # print("Meanings Data Received:", meanings_data)  # Debugging line to check what data is received
            return meanings_data
        except Exception as e:
            print("Error processing meanings data:", e)  # Print any error during data processing
            return None
    else:
        print("Failed to fetch meanings data, please try refreshing your browser.")
        return None


def fetch_user_teams(api_token):
    # Eventually remove hard code
    # return [
    #     {"id": 25, "name": "Team A", "img": "None"},
    #     {"id": 31, "name": "Team B", "img": "None"},
    #     {"id": 4, "name": "Team C", "img": "None"},
    #     {"id": 172, "name": "Team D", "img": "None"},
    # ]

    headers = configure_headers(api_token)
    full_endpoint = f"{endpoint}/api/my/teams"
    response = requests.get(full_endpoint, headers=headers)

    # print("Status Code:", response.status_code)  # Debugging line to check the status code
    # print("Response Text:", response.text)  # Debugging line to check the raw response text

    if response.status_code == 200:
        try:
            user_team_list = response.json()
            return user_team_list
        except Exception as e:
            print("Error processing teams data:", e)  # Print any error during data processing
            return None
    else:
        print("Failed to fetch user team data, please try refreshing your browser.")
        print(f"Status Code: {response.status_code}") # Error with teams list starts here; status code is 404
        return None


def fetch_team(api_token, team_id):
    headers = configure_headers(api_token)
    full_endpoint = f"{endpoint}/api/teams/{team_id}"
    response = requests.get(full_endpoint, headers=headers)

    # print("Status Code:", response.status_code)  # Debugging line to check the status code
    # print("Response Text:", response.text)  # Debugging line to check the raw response text

    if response.status_code == 200:
        try:
            team = response.json()
            return team
        except Exception as e:
            print("Error processing team data:", e)  # Print any error during data processing
            return None
    else:
        print("Failed to fetch team data, please try refreshing your browser.")
        return None


def generate_team_card(team):
    """Generate a single team card."""
    return html.Div(
        children=[
            html.Div(team['name'], className='team',
                     style={'position': 'absolute', 'top': '50%', 'left': '50%',
                            'transform': 'translate(-50%, -50%)'}),
            html.Div([html.Img(src=team['img'], style={'width': '60px', 'height': '60px'})],
                     style={'position': 'relative', 'margin': '20px auto'}),

        ],
        className='rectangle-1',
        style={'background': '#ecffda', 'borderRadius': '15px', 'width': '180px',
               'height': '220px', 'position': 'relative',
               'box-shadow': '0px 4px 4px 0px rgba(0, 0, 0, 0.25)', 'margin': '20px 10px',
               'text-align': 'center'}
    )


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
        dcc.Store(id='current-team', storage_type='session'),
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
            dbc.Col([
                dbc.Card(
                    dbc.CardBody(
                        html.Div(
                            id='user_current_team',
                            style={
                                'padding': '10px',
                                'textAlign': 'center',
                                'fontSize': '16px'  # Adjust font size as needed
                            }
                        )
                    ),
                    style={'border': '2px solid #007bff', 'borderRadius': '15px', 'padding': '10px'}
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


'''
    Does not work currently!
'''
@app.callback(
    Output(component_id='user_current_team', component_property='children'),
    Input(component_id='current-team', component_property='data'),
)
def show_current_team(currentTeamName):
    return f"Current Team: {currentTeamName}"


@app.callback(
    Output('user-logged-in', 'data', allow_duplicate=True),
    Input(component_id='firebase_auth', component_property='userDisplayName'),
    prevent_initial_call=True
)
def store_display_name(userDisplayName):
    return userDisplayName


'''
    Not sure if the below function has the correct output and inputs????
'''
@app.callback(
    Output(component_id='current-team', component_property='data', allow_duplicate=True),
    Input(component_id='team-changer-button', component_property='id'),
    prevent_initial_call=True
)
def store_current_team(current_team):
    return current_team


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
    Output(component_id='firebase_auth', component_property='loginFlag'),
    Output(component_id='login_pane', component_property='hidden', allow_duplicate=True),
    Input(component_id='login-button', component_property='n_clicks'),
    prevent_initial_call=True
)
def login_perform_login(input_value):
    return True, False


def create_alert(alert_text, color="success", duration=4000):
    return dbc.Alert(alert_text,
                     is_open=True,
                     dismissable=True,
                     color=color,
                     duration=duration)


def create_success_alert(alert_text):
    return create_alert(alert_text)


def create_danger_alert(alert_text):
    return create_alert(alert_text, color="danger")


def create_warning_alert(alert_text):
    return create_alert(alert_text, color="warning")


@app.callback(
    Output('word-content', 'children'),
    Input('url', 'pathname'),
    Input(component_id='firebase_auth', component_property='apiToken'),
    Input('lingo-words-updated', 'data')
)
def update_words(pathname, api_token, words_updated_flag):
    if pathname == '/glossary':
        words_data = fetch_words(api_token)
        if words_data is not None:
            table_header = [
                # html.Thead(html.Tr([html.Th("Word")]))
            ]
            rows = []
            for word in words_data:
                rows.append(
                    html.Tr([html.Td(dcc.Link(href=f'/reflections?word={word["id"]}', children=[word["word"]]))]))
            table_body = [html.Tbody(rows)]
            table_content = dbc.Table(table_header + table_body, striped=True, bordered=True, hover=True)
            return table_content
        else:
            return html.Div("No words found")
    return html.Div("Failed to load words, please refresh your browser.")


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


# '''
#     Not sure if the function below is even needed???
# '''
# @app.callback(
#     Output(),
#     Input('url', 'pathname'),
#     Input(component_id='firebase_auth', component_property='apiToken'),
# )
# def update_teams(pathname, api_token, words_updated_flag):
#     if pathname == '/teams':
#         team_list = fetch_teams(api_token)
#         if team_list is not None:
#             table_header = [
#                 # html.Thead(html.Tr([html.Th("Word")]))
#             ]
#             rows = []
#             for team in team_list:
#                 rows.append(
#                     html.Tr([html.Td(dcc.Link(href=f'/{team["id"]}', children=[team["name"]]))])) # NOT SURE ABOUT THE HREF ON THIS LINE
#             table_body = [html.Tbody(rows)]
#             table_content = dbc.Table(table_header + table_body, striped=True, bordered=True, hover=True)
#             return table_content
#         else:
#             return html.Div("No teams found")
#     return html.Div("Failed to load teams, please refresh your browser.")


@app.callback(
    Output('alert-bar-div', 'children', allow_duplicate=True),
    Output('word-input', 'value'),
    Output('lingo-words-updated', 'data'),
    Input('submit-word', 'n_clicks'),
    State('word-input', 'value'),
    State('firebase_auth', 'apiToken'),
    prevent_initial_call=True
)
def submit_word(n_clicks, word, api_token):
    if n_clicks:
        if word is not None:
            headers = configure_headers_with_body(api_token)
            data = {
                "word": word,
                "project": 1
            }
            response = requests.post(f"{endpoint}/api/words", json=data, headers=headers)
            if response.status_code == 200 or response.status_code == 201:
                return (create_success_alert("Word submitted successfully!"),
                        '',
                        n_clicks)
            else:
                return (create_danger_alert(f"Failed to submit word. Error: {response.text}"),
                        word,
                        n_clicks)
        else:
            return (
                create_warning_alert("Please enter a word before submitting."),
                word,
                n_clicks)
    return html.Div(), word, n_clicks


@app.callback(
    Output('alert-bar-div', 'children', allow_duplicate=True),
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
                return (create_success_alert("Meaning submitted successfully!"),
                        '',
                        n_clicks)
            else:
                return (create_danger_alert(f"Failed to submit meaning. Error: {response.text}"),
                        meaning,
                        n_clicks)
        else:
            return (
                create_warning_alert("Please select a word and enter a meaning before submitting."),
                meaning,
                n_clicks)
    return html.Div(), meaning, n_clicks


@app.callback(
    Output('alert-bar-div', 'children', allow_duplicate=True),
    Output('reflection-input', 'value'),
    Output('lingo-reflections-updated', 'data'),
    Input('submit-reflection', 'n_clicks'),
    State('word-dropdown', 'value'),
    State('reflection-input', 'value'),
    State('firebase_auth', 'apiToken'),
    prevent_initial_call=True,
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
                return create_success_alert("Reflection submitted successfully!"), '', n_clicks
            else:
                return (create_danger_alert(f"Failed to submit reflection. Error: {response.text}"),
                        reflection,
                        n_clicks)
        else:
            return (create_warning_alert("Please select a word and enter a reflection before submitting."),
                    reflection,
                    n_clicks)
    return html.Div(), reflection, n_clicks


@app.callback(
    Output('submit-word', 'disabled'),
    Input('word-input', 'value')
)
def update_submit_word_button(meaning_input):
    return meaning_input is None or len(meaning_input.strip()) == 0


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
    Output("current-team", 'data'),
    Input({"type": "team-changer-button", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def update_current_team(clicks):
    print(ctx.triggered_id.index)


@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    Input('url', 'search'),
    Input('firebase_auth', 'apiToken'),
    # Input('lingo-words-updated', 'data'),
    # Input('lingo-meanings-updated', 'data'),
    # Input('lingo-reflections-updated', 'data')
)
def update_page_content(pathname, search, api_token):
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
            html.Div(
                children=[
                    # Team title
                    html.H2("Current Team: Team 0", style={'text-align': 'center'}),

                    # Team description and details
                    html.Div(
                        children=[
                            # Team description
                            html.P("Team 0 is a dynamic team focused on innovation and collaboration.",
                                   style={'font-size': '18px', 'margin-bottom': '10px'}),

                            # Team leader
                            html.P("Team Leader: John Doe",
                                   style={'font-size': '16px', 'font-weight': 'bold', 'margin-bottom': '10px'}),
                        ],
                        style={'padding': '20px', 'border': '1px solid #ddd', 'border-radius': '8px',
                               'background-color': '#f9f9f9', 'width': '60%', 'margin': '20px auto',
                               'text-align': 'center'}
                    ),
                ],
                style={'width': '70%', 'margin': '20px auto 0'}
            ),
            html.Div(
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Words"),
                            dbc.CardBody([
                                html.Div(id='word-content'),
                            ])
                        ])
                    ], width=6),
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
                ])
            ),
            html.Div(
                children=[],
                style={'marginTop': '20px', 'padding-left': '20px', 'border-left': '2px solid #ccc',
                       'height': 'calc(100vh - 140px)', 'overflow-y': 'auto', 'flex': '1'}
            )
        ]

    elif pathname == '/glossary':
        return html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Words"),
                        dbc.CardBody([
                            html.Div(id='word-content'),
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
                            html.Button('Submit',
                                        id='submit-word',
                                        disabled=True,
                                        className='btn btn-success',
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
        teams = fetch_user_teams(api_token)
        row_count = trunc(len(teams) / 3)
        if len(teams) % 3 != 0:
            row_count = row_count + 1
        rows = []
        for r in range(0, row_count):
            cols = []
            for c in range(0, 3):
                current_index = r*3+c
                if current_index >= len(teams):
                    break
                current_team = teams[current_index]
                team_name = current_team['name']
                current_card = dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(team_name),
                        dbc.CardBody([
                            html.Button('Select',
                                        id={"type": "team-changer-button", "index": current_team['id']},
                                        className='btn btn-success',
                                        style={'marginTop': '20px'})
                        ])
                    ])
                ], width=3)
                cols.append(current_card)
            rows.append(dbc.Row(cols))
        return html.Div(rows)


server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
