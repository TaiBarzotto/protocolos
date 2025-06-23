def init_app(app):
    from .routes import bp_util
    app.register_blueprint(bp_util)