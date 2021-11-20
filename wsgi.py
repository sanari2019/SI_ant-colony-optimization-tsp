"""WSGI entry point for Vercel deployment."""
from app import app, socketio

# Vercel needs the app object to be named 'app'
# For SocketIO support in production
application = app

if __name__ == "__main__":
    socketio.run(app, debug=False)
