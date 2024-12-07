from flask import Blueprint
import logging
from flask import request
new_app1_bp = Blueprint('new_app1', __name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
@new_app1_bp.route('/receiveMsg', methods=['POST'])
def new_app1_route():
    try:
        # 获取请求中的 JSON 数据
        data = request.get_json()  # 解析 JSON 字符串

        # 记录接收到的 JSON 数据
        logger.debug(f"Received JSON: {data}")

        # 处理接收到的数据
        if data:
            # 假设你的 JSON 数据里有字段 'message'，你可以根据实际需要修改
            message = data.get('message', 'No message provided')

            # 返回处理后的响应
            return {"status": "success", "message": message}, 200
        else:
            # 如果没有 JSON 数据，返回错误信息
            return {"status": "error", "message": "No valid JSON data received"}, 400
    except Exception as e:
        # 如果解析 JSON 时发生错误
        logger.error(f"Error processing request: {e}")
        return {"status": "error", "message": "Error processing request"}, 500

def init_app(app):
    app.register_blueprint(new_app1_bp)
