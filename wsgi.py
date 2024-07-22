from app import server as app

# This is the production entry point for our app.
if __name__ == "__main__":
    app.run(debug=False)