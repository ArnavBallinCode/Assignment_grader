from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pptx import Presentation
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/grade', methods=['POST'])
def grade_ppt():
    if 'ppt' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    ppt_file = request.files['ppt']
    presentation = Presentation(ppt_file)

    scores = {
        'Completeness': 0,
        'Clarity of Ideas': 0,
        'Justification of Skills': 0
    }

    # Implement grading logic based on the criteria
    for slide in presentation.slides:
        # Analyze each slide and update scores based on criteria
        pass

    return jsonify({'scores': scores})

if __name__ == '__main__':
