# About Us
interLINGO was developed by researchers at 
[Appalachian State University (App State)](https://www.appstate.edu/). 
Funding for this project came from the 
[Research Institute for Environment, Energy, and Economics](https://rieee.appstate.edu/) 
at App State as well as the 
[Science and Technologies for Phosphorus Sustainability (STEPS) Center](https://steps-center.org/). 
interLINGO provides a collaborative space for teams to surface, discuss, 
and resolve differences in philosophies across disciplines by using language 
as a boundary object. 

If you are interested in using interLINGO, please contact 
[Dr. Mark Hills](https://cs.appstate.edu/hillsma/) (hillsma@appstate.edu) 
and Dr. Kim Bourne (bournekd@appstate.edu).

Contributors to this program include (in alphabetical order):
* Dr. Kimberly Bourne
* Christian Hart
* Dr. Christine Hendren
* Dr. Mark Hills
* Elle Russell
 
 # Getting Started
You will want to make sure you create a virtual environment. If you are not
sure how to do this, please ask. On a Mac, it is a command like the following:
```angular2html
python -m venv .venv
```

You will then enter the virtual environment (most IDEs will do this automatically,
so this is only needed from the command line). On a Mac, this is:
```
source .venv/bin/activate
```
while on Windows, it is:
```
.venv\Scripts\activate
```

Now, install any requirements using `pip`. This will just install the requirements
into the local directories:
```
pip install -r requirements.txt
```

# Running the Client

There are two ways to run the client. The first, meant for production
environments, is to use the `run.sh` script in the `bin` directory.
This is used by the Dockerized version of the app, but can also be
used directly. The alternative, and the easier method for debugging, is
to just run the application directly using `python app.py`. This will
cause the application to start in debug mode, making it easier for
development.

Note that an environment variable now also needs to be set. This
variable holds the location of the API server. On Windows, this
would be set as:
```
SET API_SERVER_URL=the-url-for-the-api-server
```
while on Mac or Linux this would be set as:
```
export API_SERVER_URL=the-url-for-the-api-server
```
This should be done before running the server. Note that, on Linux
or Mac, these can be combined into a single command:
```
API_SERVER_URL=the-url-for-the-api-server python app.py
```

# Bundling the Client

To create a Docker image for the client, you use the `Docker build`
command (note that `0.0.2` is just a sample version number, the
actual version number should be included):
```
docker build -t lingo-web-client:0.0.2
```
If you are on a Mac with Apple silicone then you need to include
a flag to build an image that runs on Intel and AMD processors:
```
docker build --platform linux/amd64 -t lingo-web-client:0.0.2
```
If you don't do this, you may get errors when you try to create
a running container, depending on the processor used on the
server.
