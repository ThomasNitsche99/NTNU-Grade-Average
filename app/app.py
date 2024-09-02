from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from grade_average import GradeCalculator # Adjust import based on your class name

app = Flask(__name__)
app.config.from_pyfile('settings.py')    
CORS(app)

#Setup cors to only allow requests from authorized website
#TODO: 

#Intersection function for checking authorization
def require_api_key(func):
    def wrapper(*args, **kwargs):
        key = request.headers.get('x-api-key')
        print(key)
        if key and key == app.config.get('SECRET_KEY'):
            return func(*args, **kwargs)
        else:
            return jsonify({"error": "Unauthorized"}), 401
    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/' , methods=['GET'])
@require_api_key
def hello_world():
    return jsonify("Greetings!")

@app.route('/process-pdf', methods=['POST'])
@require_api_key
def process_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.pdf'):
        # file_path = os.path.join('/tmp', file.filename)
        # file.save(file_path)
        
        # Assuming YourClass is the main class doing the work in your script
        processor = GradeCalculator(file, False)
        result = processor.calculate()  # Modify according to your method name

        return jsonify({"result": result}), 200

    return jsonify({"error": "Invalid file type"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
