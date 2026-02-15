from flask import Flask, send_file, jsonify, abort
from flask_cors import CORS
from werkzeug.utils import secure_filename
from api.routes import api_bp
import os

TABLES_DIR = 'tables'
os.makedirs(TABLES_DIR, exist_ok=True)
RESULT_DIR = 'result'
os.makedirs(RESULT_DIR, exist_ok=True)

app = Flask(__name__, static_folder=None)
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = "application/json; charset=utf-8"
CORS(app)

# Register API blueprint
app.register_blueprint(api_bp, url_prefix='/api')


@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "Server is running",
        "available_endpoints": {
            "API endpoints": [
                "/api/database",         # Upload database
                "/api/generate",         # Generate results
                "/api/save",             # Save modified results
                "/api/vas/list",         # Get VA system list
                "/api/vas",              # Get/Create/Delete VA system
                "/api/"                  # Get CSV file
            ],
            "File download": "/<filename>"
        }
    })


@app.route('/<filename>', methods=['GET'])
def download_file(filename):
    safe_filename = secure_filename(filename)
    file_path = os.path.join(os.path.abspath(TABLES_DIR), safe_filename)
    # Check path
    if not os.path.commonpath([os.path.abspath(TABLES_DIR), file_path]) == os.path.abspath(TABLES_DIR):
        abort(403, description="Access denied")
    # Check file
    if not os.path.isfile(file_path):
        abort(404, description="File not found")
    try:
        return send_file(file_path)
    except Exception as e:
        app.logger.error(f"File delivery failed: {str(e)}")
        abort(500)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8888, debug=False)