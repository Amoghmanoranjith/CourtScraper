from src.cases import cases
from src.scraper import Scraper
from flask import Flask, request, jsonify, send_file, abort, send_from_directory
from flask_cors import CORS
import requests
from io import BytesIO
from src.db import insert_log
app = Flask(__name__)
CORS(app)  

@app.route('/')
def serve_index():
    return send_from_directory('.', 'page/index.html')

@app.route('/scrape', methods=['POST'])
def scrape_case():
    data = request.get_json()
    print("Received ",data, flush=True)
    required_keys = {'case_type', 'case_number', 'case_year'}
    if not data or not required_keys.issubset(data.keys()):
        return jsonify({"error": "Missing required fields."})

    scraper = Scraper()
    result, raw = scraper.scrape(
        case_type=data['case_type'],
        case_number=data['case_number'],
        case_year=data['case_year']
    )
    if result['status'] == 200:
        success = insert_log(data['case_type'], data['case_number'],int(data['case_year']),raw)
        print("db logging status:",success)
    # store in a pgsql db time_stamp, case_type, case_number, case_year, data
    # run this process parallely
    return jsonify(result)

@app.route('/download', methods = ['GET'])
def proxy_download():
    pdf_url = "https://delhihighcourt.nic.in/app/showlogo/"+request.args.get('document_id')
    filename = request.args.get("filename", "document") + ".pdf"

    if not pdf_url:
        return abort(400, "Missing 'url' parameter.")

    try:
        resp = requests.get(pdf_url, stream=True, timeout=10)
        resp.raise_for_status()
        file_data = BytesIO(resp.content)

        return send_file(
            file_data,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return abort(500, f"Failed to fetch PDF: {str(e)}")
app.run(host="0.0.0.0", port=8000, debug=True)