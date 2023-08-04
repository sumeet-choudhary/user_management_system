from application.user.views import user_blueprint
from application.role.views import role_blueprint
from application import app

app.register_blueprint(user_blueprint)
app.register_blueprint(role_blueprint)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")

