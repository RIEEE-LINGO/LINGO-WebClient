from os import environ

# Set the default for the API server endpiont
api_server_url = "http://localhost:8000"

# Get the endpoint out of the environment if set there
api_server_var = environ.get("API_SERVER_URL")
if api_server_var:
    api_server_var = api_server_var.strip()
    if len(api_server_var) > 0:
        api_server_url = api_server_var