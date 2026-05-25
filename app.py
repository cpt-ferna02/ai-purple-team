import os
import uuid
from flask import Flask, render_template, request, jsonify, send_file
from red_team import generate_red_team
from blue_team import generate_blue_team
from report_builder import build_purple_report
import traceback

app = Flask(__name__)
os.makedirs("exports", exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    technique_id = data.get("technique_id", "").strip()
    technique_name = data.get("technique_name", "").strip()
    description = data.get("description", "").strip()

    if not technique_id or not technique_name:
        return jsonify({"error": "Please provide a technique ID and name."}), 400

    try:
        # Generate red team data
        red_data = generate_red_team(technique_id, technique_name, description)

        # Generate blue team data using red team context
        blue_data = generate_blue_team(technique_id, technique_name, red_data)

        return jsonify({
            "red_team": red_data,
            "blue_team": blue_data
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/export-pdf", methods=["POST"])
def export_pdf():
    data = request.get_json()
    red_data = data.get("red_team")
    blue_data = data.get("blue_team")

    if not red_data or not blue_data:
        return jsonify({"error": "No report data provided."}), 400

    try:
        filename = f"purple_report_{red_data.get('technique_id', 'unknown')}_{uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join("exports", filename)
        build_purple_report(red_data, blue_data, output_path)
        return send_file(output_path, as_attachment=True, download_name=filename)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)