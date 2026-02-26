from app import app

if __name__ == "__main__":
    print("Starting Flask app on port 5000...")
    app.run(debug=True, port=5000)
