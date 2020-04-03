from flask import Flask, render_template

app = Flask(__name__)

from . import pages
app.register_blueprint(pages.bp)
