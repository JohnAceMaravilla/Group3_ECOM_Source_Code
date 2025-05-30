from __init__ import create_app

app = create_app()

if __name__ == '__main__':
    # Make the Flask app accessible from mobile devices
    app.run(debug=True, host='0.0.0.0', port=5000)     