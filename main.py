import threading

# import "packages" from flask
from flask import render_template  # import render_template from "public" flask libraries

from __init__ import app

# setup APIs
from api.snake import snake_api # Blueprint import api definition
from api.score import score_api # Blueprint import api definition
from api.admin import admin_api # Blueprint import api definition

# register URIs
app.register_blueprint(snake_api) # register app pages
app.register_blueprint(score_api) # register app pages
app.register_blueprint(admin_api) # register app pages

# this runs the application on the development server
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="8343")
