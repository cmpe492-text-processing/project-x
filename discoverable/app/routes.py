from flask import render_template, request, redirect, url_for, flash


def init_routes(app):
    @app.route('/')
    def home():
        return render_template('home.html')

