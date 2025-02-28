from math import trunc

import dash
from dash import html, dcc, Input, Output, callback_context, State, ALL, ctx
import dash_bootstrap_components as dbc
import base64
import pandas as pd
from dash.exceptions import PreventUpdate
from firebase_authentication import FirebaseAuthentication
from urllib.parse import urlparse, parse_qs
from api import (fetch_words, fetch_meanings, fetch_reflections,
                 fetch_user_info, fetch_user_teams, fetch_team,
                 create_word, create_meaning, create_reflection,
                 update_user_with_current_team)

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        # "https://www.gstatic.com/firebasejs/ui/6.1.0/firebase-ui-auth.css"  # For Firebase Auth styling
    ],
    suppress_callback_exceptions=True
)



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
        dcc.Store(id='current-team-id', storage_type='session'),
        dcc.Store(id='current-team-name', storage_type='session'),
        dcc.Store(id='is-team-owner', storage_type='session'),
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

            # User display name at top of page
            dbc.Col([
                dbc.Card(
                    dbc.CardBody(
                        html.Div(
                            id='user_display_name',
                            style={'display': 'flex', 'justifyContent': 'flex-end', 'alignItems': 'center'}
                        )
                    ),
                    style={
                        'border': '1px solid #007bff',
                        'borderRadius': '8px',
                        'padding': '0px',
                        'margin': '0px',
                        'fontSize': '14px'
                    }
                )
            ], width=4, style={'display': 'flex', 'justifyContent': 'flex-end', 'alignItems': 'center'}),

            # Current Team Name display at top of page
            dbc.Col([
                dbc.Card(
                    dbc.CardBody(
                        html.Div(
                            id='user_current_team',
                            style={'display': 'flex', 'justifyContent': 'flex-end', 'alignItems': 'center'}
                        )
                    ),
                    id='user_team_card',
                    style={
                        'border': '1px solid #007bff',
                        'borderRadius': '8px',
                        'padding': '0px',
                        'margin': '0px',
                        'fontSize': '14px'
                    }
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
                dbc.Nav([], id='left-nav', vertical=True, pills=True,
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


def compute_left_nav(is_admin = False):
    dashboard_item = dbc.NavItem(
                        dbc.NavLink('Dashboard', href='/', id='dashboard-link', active='exact',
                                    style={'color': 'inherit', 'textDecoration': 'none', 'padding': '10px',
                                           'marginBottom': '5px'}))

    glossary_item = dbc.NavItem(
                        dbc.NavLink('Words', href='/glossary', id='glossary-link', active='exact',
                                    style={'color': 'inherit', 'textDecoration': 'none', 'padding': '10px',
                                           'marginBottom': '5px'}))

    meanings_item = dbc.NavItem(
                        dbc.NavLink('Meanings and Reflections', href='/reflections', id='reflections-link',
                                    active='exact',
                                    style={'color': 'inherit', 'textDecoration': 'none', 'padding': '10px',
                                           'marginBottom': '5px'}))

    teams_item = dbc.NavItem(dbc.NavLink('Teams', href='/teams', id='teams-link', active='exact',
                                            style={'color': 'inherit', 'textDecoration': 'none', 'padding': '10px',
                                                   'marginBottom': '5px'}))

    admin_item = dbc.NavItem(dbc.NavLink('Admin', href='/admin', id='admin-link', active='exact',
                                            style={'color': 'inherit', 'textDecoration': 'none', 'padding': '10px',
                                                   'marginBottom': '5px'}))

    nav_items = [ dashboard_item, glossary_item, meanings_item, teams_item ]
    # TODO: Put this back once we have an admin page
    # if is_admin:
    #     nav_items.append(admin_item)

    return nav_items


@app.callback(
    Output(component_id='left-nav', component_property='children'),
    Input(component_id='user-logged-in', component_property='data'),
    Input(component_id='current-team-id', component_property='data'),
    Input(component_id='firebase_auth', component_property='apiToken'),
)
def show_left_nav(display_name, team_id, api_token):
    if display_name is None or len(display_name.strip()) == 0:
        return []
    else:
        user_info = fetch_user_info(api_token)
        is_admin = False
        if user_info is not None:
            is_admin = user_info['is_admin']

        return compute_left_nav(is_admin)


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
    Output(component_id='firebase_auth', component_property='loginFlag'),
    Output(component_id='login_pane', component_property='hidden', allow_duplicate=True),
    Input(component_id='login-button', component_property='n_clicks'),
    prevent_initial_call=True
)
def login_perform_login(input_value):
    return True, False


@app.callback(
    Output(component_id='current-team-id', component_property='data', allow_duplicate=True),
    Output(component_id='current-team-name', component_property='data', allow_duplicate=True),
    Output(component_id='is-team-owner', component_property='data', allow_duplicate=True),
    Input(component_id='user-logged-in', component_property='data'),
    Input(component_id='firebase_auth', component_property='apiToken'),
    prevent_initial_call=True
)
def update_user_info(display_name, api_token):
    if display_name is None or len(display_name.strip()) == 0:
        # User logged out
        return -1, ""
    else:
        # User is logged in
        user_info = fetch_user_info(api_token)
        app.logger.debug(user_info)
        if user_info is not None:
            team_info = fetch_team(api_token, user_info['current_team_id'])
            if team_info is not None:
                # TODO: Get back info on team membership, change False to appropriate value
                return user_info['current_team_id'], team_info['team_name'], False
        return -1, "" # Just return the empty string for the team name
    # TODO: We should probably format the entire team widget here to make it disappear if there is no current team

@app.callback(
    Output(component_id='user_current_team', component_property='children'),
    Output('user_team_card', 'style'),
    Input(component_id='current-team-name', component_property='data')
)
def update_displayed_team(team_name):
    if team_name and team_name.strip():  # Check if not empty
        return (
            f"Current Team: {team_name}",
            {'border': '1px solid #007bff', 'borderRadius': '8px', 'padding': '0px',
             'margin': '0px', 'fontSize': '14px'}  # Keep card visible
        )
    return "What??", {'display': 'none'}  # Hide card when empty


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
    Input(component_id='current-team-id', component_property='data'),
    Input('lingo-words-updated', 'data'),
    State(component_id='firebase_auth', component_property='apiToken')
)
def update_words(pathname, team_id, words_updated_flag, api_token):
    if pathname == '/glossary':
        words_data = fetch_words(api_token,  team_id)
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
    Input('lingo-reflections-updated', 'data'),
    State(component_id='firebase_auth', component_property='apiToken')
)
def update_reflections(pathname, selected_word_id, reflections_updated_flag, api_token):
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
                    app.logger.error(f"Error processing reflection data into DataFrame: {e}")
                    return html.Div("Failed to process reflection data")
            else:
                return html.Div("No reflections found for the selected word")
        return html.Div("Select a word to see reflections")
    return html.Div("")


@app.callback(
    Output('team-member-content', 'children'),
    Input('url', 'pathname'),
    State(component_id='firebase_auth', component_property='apiToken'),
    State('is_team_owner', 'data')
)
def update_team_members(pathname, selected_word_id, reflections_updated_flag, api_token, is_team_owner):
    if pathname == '/teams' and is_team_owner:
        # TODO: Actually make an API call
        # if selected_word_id is not None:
        #     reflections_data = fetch_reflections(selected_word_id, api_token)
        #     if reflections_data:
        #         try:
        #             df = pd.DataFrame(reflections_data)
        #             df = df[['reflection', 'created_at']].rename(columns={
        #                 'reflection': 'Reflection',
        #                 'created_at': 'Created At'
        #             })
        #             table_content = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)
        #             return table_content
        #         except Exception as e:
        #             app.logger.error(f"Error processing reflection data into DataFrame: {e}")
        #             return html.Div("Failed to process reflection data")
        #     else:
        #         return html.Div("No reflections found for the selected word")
        return html.Div("Names of team members will be here")
    return html.Div("")

@app.callback(
    Output('meaning-content', 'children'),
    Input('url', 'pathname'),
    Input('word-dropdown', 'value'),
    Input('lingo-meanings-updated', 'data'),
    State(component_id='firebase_auth', component_property='apiToken')
)
def update_meanings(pathname, selected_word_id, meanings_updated_flag, api_token):
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
                    app.logger.error(f"Error processing meaning data into DataFrame: {e}")
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
    Input(component_id='current-team-id', component_property='data'),
    State(component_id='firebase_auth', component_property='apiToken'),
)
def update_word_options(pathname, search, team_id, api_token):
    if pathname == '/reflections':
        query_params = {}
        if len(search) > 1:
            query_params = parse_qs(search[1:])

        words_data = fetch_words(api_token, team_id)  # Endpoint that returns all words
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
    Output('alert-bar-div', 'children', allow_duplicate=True),
    Output('word-input', 'value'),
    Output('lingo-words-updated', 'data'),
    Input('submit-word', 'n_clicks'),
    State('word-input', 'value'),
    State('firebase_auth', 'apiToken'),
    State(component_id='current-team-id', component_property='data'),
    prevent_initial_call=True
)
def submit_word(n_clicks, word, api_token, current_team_id):
    if n_clicks:
        if word is not None:
            # TODO: Add team ID to call
            response = create_word(api_token, current_team_id, word)
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
            response = create_meaning(api_token, word_id, meaning)
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
            response = create_reflection(api_token, word_id, reflection)
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
    Output("current-team-id", 'data'),
    Output("current-team-name", 'data'),
    Output('is-team-owner', 'data'),
    Input({"type": "team-changer-button", "index": ALL}, "n_clicks"),
    State('firebase_auth', 'apiToken'),
    prevent_initial_call=True
)
def update_current_team(clicks, api_token):
    # Since this is called when the buttons are created, we need to check to see if anything
    # was actually clicked. If anything was, clicks, which is a list, should have a value in
    # it somewhere...
    real_clicks = [ c for c in clicks if c is not None ]
    if len(real_clicks) == 0:
        raise PreventUpdate

    app.logger.debug(f"Team update triggered for {ctx.triggered_id.index}")
    updated_team_id = ctx.triggered_id.index

    # Attempt to update our current team. Then we can just get info
    # back about our new current team.
    response = update_user_with_current_team(api_token, updated_team_id)
    if response is None:
        app.logger.error(f"Failed to update team for {updated_team_id}")
    else:
        team_info = fetch_team(api_token, updated_team_id)
        if response is None:
            app.logger.error(f"Failed to fetch team for {updated_team_id}")
        else:
            # TODO: Get back info on team membership, set False to appropriate value
            return updated_team_id, team_info['team_name'], False


@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    Input('url', 'search'),
    Input('firebase_auth', 'apiToken'),
    State('is-team-owner', 'data')
    # Input('lingo-words-updated', 'data'),
    # Input('lingo-meanings-updated', 'data'),
    # Input('lingo-reflections-updated', 'data')
)
def update_page_content(pathname, search, api_token, is_team_owner):
    if pathname == '/':
        return display_main_page()
    elif pathname == '/glossary':
        return display_glossary_page()
    elif pathname == '/reflections':
        return display_reflections_page(search)
    elif pathname == '/teams':
        return display_teams_page(api_token, is_team_owner)


def display_main_page():
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
                               style={'fontSize': '18px', 'margin-bottom': '10px'}),

                        # Team leader
                        html.P("Team Leader: John Doe",
                               style={'fontSize': '16px', 'font-weight': 'bold', 'margin-bottom': '10px'}),
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


def display_glossary_page():
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


def display_reflections_page(search):
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


def display_teams_page(api_token, is_team_owner):
    teams = fetch_user_teams(api_token, app.logger)
    # Initialize the row_count to 0. If we don't have any teams
    # come back (API call error, user not logged in), this will be
    # the default. A logged-in user should always have at least 1 team.
    row_count = 0
    if teams is not None:
        row_count = trunc(len(teams) / 3)
        if len(teams) % 3 != 0:
            row_count = row_count + 1
    # Each team is placed in a card, with rows of 3 cards used to
    # show the teams.
    rows = []
    for r in range(0, row_count):
        cols = []
        for c in range(0, 3):
            current_index = r * 3 + c
            if current_index >= len(teams):
                break
            current_team = teams[current_index]
            team_name = current_team['team_name']
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

    if is_team_owner:
        team_info_row = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Team Members"),
                    dbc.CardBody([
                        html.Div(id='team-member-content')
                    ])
                ])
            ], width=9)])
        rows.append(team_info_row)

    return html.Div(rows)


server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
