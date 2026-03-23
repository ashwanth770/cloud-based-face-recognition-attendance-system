from flask import Flask, request, render_template, jsonify, send_file
import boto3, os, io, pandas as pd
from werkzeug.utils import secure_filename
from utils import compare_and_log_attendance, fetch_attendance_logs
from datetime import datetime

app = Flask(__name__)
BUCKET = os.getenv('S3_BUCKET')

s3 = boto3.client('s3')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        file = request.files['file']
        filename = secure_filename(f"{user_id}.jpg")
        key = f"registered_faces/{filename}"
        s3.upload_fileobj(file, BUCKET, key)
        return f"Registered {user_id}"
    return render_template('register.html')

@app.route('/upload', methods=['POST'])
def upload_attendance():
    file = request.files['file']
    fname = secure_filename(file.filename)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    key = f"attendance_photos/{timestamp}_{fname}"
    s3.upload_fileobj(file, BUCKET, key)
    user_id = compare_and_log_attendance(BUCKET, key)
    if user_id:
        return jsonify({"status":"success","user_id":user_id})
    else:
        return jsonify({"status":"failed","message":"No match found"}),404

@app.route('/admin')
def admin():
    logs = fetch_attendance_logs()
    return render_template('admin.html', logs=logs)

@app.route('/export')
def export_csv():
    logs = fetch_attendance_logs()
    if not logs:
        return "No logs", 404
    df = pd.DataFrame(logs)
    csv_io = io.StringIO()
    df.to_csv(csv_io, index=False)
    csv_io.seek(0)
    return send_file(io.BytesIO(csv_io.getvalue().encode()), mimetype='text/csv', download_name='attendance_logs.csv', as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)