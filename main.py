from cases import cases
from scraper import Scraper
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape_case():
    data = request.get_json()

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

app.run(host="0.0.0.0", port=8000, debug=True)