import dash

app = dash.Dash(__name__)
server = app.server

app.config.suppress_callback_exceptions = True


""" import dash_auth
VALID_USERNAME_PASSWORD_PAIRS = [
    ['fouad', 'zabaneh']
]

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)
 """
