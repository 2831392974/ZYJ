from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import tempfile
import os
from datetime import datetime

app = Flask(__name__)

# 临时存储配置
UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 模拟用户数据库（实际使用时建议用数据库）
users = {
    "admin": {"password": "admin123", "photos": []}
}

# ------------ 核心路由 ------------
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username in users and users[username]['password'] == password:
        return jsonify({"status": "success", "token": "demo_token"})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/upload', methods=['POST'])
def upload():
    # 验证 token（简易版）
    if request.headers.get('Authorization') != 'Bearer demo_token':
        return jsonify({"error": "Unauthorized"}), 403
    
    if 'photo' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['photo']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
    
    # 保存到临时文件（实际使用需替换为云存储）
    filename = secure_filename(f"{datetime.now().timestamp()}.jpg")
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(temp_path)
    
    # 模拟存储记录（实际需用数据库）
    users["admin"]["photos"].append(filename)
    
    return jsonify({
        "status": "success",
        "message": "File will be auto-deleted in 1 hour",
        "filename": filename
    })

# ------------ Vercel 适配器 ------------
def vercel_handler(event, context):
    from werkzeug.wrappers import Request
    from werkzeug.datastructures import Headers
    from io import BytesIO
    
    # 转换 Vercel 事件为 Flask 请求
    body = event.get('body', '')
    headers = Headers(event.get('headers', {}))
    
    with Request({
        'REQUEST_METHOD': event['httpMethod'],
        'PATH_INFO': event['path'],
        'QUERY_STRING': event.get('queryStringParameters', ''),
        'wsgi.input': BytesIO(body.encode()),
        'CONTENT_TYPE': headers.get('Content-Type', ''),
        'HTTP_AUTHORIZATION': headers.get('Authorization', '')
    }) as req:
        with app.request_context(req.environ) as ctx:
            app.preprocess_request()
            try:
                resp = app.full_dispatch_request()
            except Exception as e:
                resp = app.handle_exception(e)
            return {
                'statusCode': resp.status_code,
                'headers': dict(resp.headers),
                'body': resp.get_data(as_text=True)
            }

# 本地调试模式
if __name__ == '__main__':
    app.run(port=3000, debug=True)
