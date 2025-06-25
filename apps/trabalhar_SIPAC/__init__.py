def init_app(app):
    from .routes import bp_protocolos
    app.register_blueprint(bp_protocolos)
