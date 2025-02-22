from config import api_server_url
import requests


def configure_headers(api_token):
    headers = {"Authorization": f"Bearer {api_token}"}
    return headers


def configure_headers_with_body(api_token):
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    return headers


# TODO: Add the current team ID as an input
def fetch_words(api_token, team_id):
    headers = configure_headers(api_token)
    # TODO: Use the /teams/{team_id}/words endpoint instead to just get the words for the team
    full_endpoint = f"{api_server_url}/api/teams/{team_id}/words"
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

def fetch_reflections(word_id, api_token):
    headers = configure_headers(api_token)
    full_endpoint = f"{api_server_url}/api/words/{word_id}/reflections"
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
    full_endpoint = f"{api_server_url}/api/words/{word_id}/meanings"
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


def fetch_user_teams(api_token, logger):
    headers = configure_headers(api_token)
    full_endpoint = f"{api_server_url}/api/my/teams"
    response = requests.get(full_endpoint, headers=headers)

    # print("Status Code:", response.status_code)  # Debugging line to check the status code
    # print("Response Text:", response.text)  # Debugging line to check the raw response text

    if response.status_code == 200:
        try:
            user_team_list = response.json()
            return user_team_list
        except Exception as e:
            logger.error("Error processing user teams data:", e)
            return None
    else:
        logger.debug(f"Failed to fetch user team data, Status Code: {response.status_code}")
        return None


def fetch_user_info(api_token):
    headers = configure_headers(api_token)
    full_endpoint = f"{api_server_url}/api/my/userinfo"
    response = requests.get(full_endpoint, headers=headers)

    # print("Status Code:", response.status_code)  # Debugging line to check the status code
    # print("Response Text:", response.text)  # Debugging line to check the raw response text

    if response.status_code == 200:
        try:
            data = response.json()
            return data
        except Exception as e:
            print("Error processing data:", e)  # Print any error during data processing
            return None
    else:
        return None


def fetch_team(api_token, team_id):
    headers = configure_headers(api_token)
    full_endpoint = f"{api_server_url}/api/teams/{team_id}"
    response = requests.get(full_endpoint, headers=headers)

    # print("Status Code:", response.status_code)  # Debugging line to check the status code
    # print("Response Text:", response.text)  # Debugging line to check the raw response text

    if response.status_code == 200:
        try:
            data = response.json()
            return data
        except Exception as e:
            print("Error processing data:", e)  # Print any error during data processing
            return None
    else:
        return None


def create_word(api_token, team_id, word):
    headers = configure_headers_with_body(api_token)
    data = {
        "team_id": team_id,
        "word": word,
    }
    response = requests.post(f"{api_server_url}/api/words", json=data, headers=headers)
    return response


def create_meaning(api_token, word_id, meaning):
    headers = configure_headers_with_body(api_token)
    data = {
        "meaning": meaning,
    }
    response = requests.post(f"{api_server_url}/api/words/{word_id}/meanings", json=data, headers=headers)
    return response


def create_reflection(api_token, word_id, reflection):
    headers = configure_headers_with_body(api_token)
    data = {
        "reflection": reflection,
    }
    response = requests.post(f"{api_server_url}/api/words/{word_id}/reflections", json=data, headers=headers)
    return response

def update_user_with_current_team(api_token, new_team_id):
    headers = configure_headers_with_body(api_token)
    data = {
        "current_team_id": new_team_id,
    }
    response = requests.post(f"{api_server_url}/api/my/teams", json=data, headers=headers)
    return response