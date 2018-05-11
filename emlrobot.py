from emapp import app, emrdb
from emapp.models import User


@app.shell_context_processor
def make_shell_context():
    return {'db': emrdb, 'User': User}
