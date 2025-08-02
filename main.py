from cases import cases
from scraper import Scraper
from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
import requests
from io import BytesIO

app = Flask(__name__)
CORS(app)  

@app.route('/scrape', methods=['POST'])
def scrape_case():
    data = request.get_json()
    print("Received ",data, flush=True)
    required_keys = {'case_type', 'case_number', 'case_year'}
    if not data or not required_keys.issubset(data.keys()):
        return jsonify({"error": "Missing required fields."}), 400

    scraper = Scraper()
    result = scraper.scrape(
        case_type=data['case_type'],
        case_number=data['case_number'],
        case_year=data['case_year']
    )

    if not result:
        return jsonify({"error": "Case not found or scraping failed."}), 404

    return jsonify(result), 200

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