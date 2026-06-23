from app import create_app

# Create our Flask application
app = create_app()

if __name__ == "__main__":
    # debug=True means:
    # - Auto-reload when you save a file
    # - Show detailed error messages
    # - NEVER use debug=True in production!
    app.run(host="0.0.0.0", port=5001, debug=True)