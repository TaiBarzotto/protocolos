def init_app(app):
    from .routes import bp_ccrs
    app.register_blueprint(bp_ccrs)
