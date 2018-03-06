from flask import Flask, send_from_directory


app = Flask(__name__)
from app import views
