from flask import Flask, request, jsonify
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import os

app = Flask(__name__)


# Vercel Serverless 适配器
def vercel_handler(event, context):
    from flask import Response
    from werkzeug.wrappers import Request
    from werkzeug.datastructures import Headers

    req = Request(event)
    res = Response()

    with app.app_context():
        app.dispatch_request(req)(res)

    return {
        'statusCode': res.status_code,
        'headers': dict(res.headers),
        'body': res.data.decode('utf-8')
    }


# 示例路由（需补充你的业务逻辑）
@app.route('/api/upload', methods=['POST'])
def upload():
    return jsonify({"status": "success"})


# 本地调试模式
if __name__ == '__main__':
    app.run(debug=True)