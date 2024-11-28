import os
import openai
import logging
import json
from flask import Flask, request, jsonify, render_template_string
# 创建 Flask 实例
app = Flask(__name__)
key = os.getenv("OPENAI_API_KEY")
# 实例化一个 OpenAI 客户端
openai.api_key = key
# 读取 Fine-Tuned 模型的 ID
with open("fine_tuned_model.json", "r") as f:
    fine_tuned_data = json.load(f)
    FINE_TUNED_MODEL = fine_tuned_data.get("fine_tuned_model_id")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Using model ID: {FINE_TUNED_MODEL}")
logger.debug(f"API Key: {key}")
# 主页面路由
@app.route('/')
def index():
    return "Hello, this is the ChatGPT API integration demo!"

# 显示聊天页面
@app.route('/chat', methods=['GET'])
def chat_page():
    html_content = '''
    <!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChatGPT By Wong</title>
    <link rel="icon" href="https://hktest.ricepon.com/ricepon-service/favicon.ico" />
    <script src="https://cdn.jsdelivr.net/npm/vue@2"></script>
    <script src="https://unpkg.com/element-ui@2.15.14/lib/index.js"></script>
    <!-- 引入样式 -->
    <link rel="stylesheet" href="https://unpkg.com/element-ui@2.15.14/lib/theme-chalk/index.css">
</head>
<style>
    body {
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100vh;
        background-color: #F0F0F6;
    }

    body::-webkit-scrollbar {
        width: 6px;
    }

    body::-webkit-scrollbar-thumb {
        background-color: #ccc;
        border-radius: 10px;
    }

    body::-webkit-scrollbar-track {
        background-color: #f1f1f1;
    }

    #app {
        width: 100%;
        height: 100%;
    }

    .message-body {
        width: 100%;
        max-width: 800px;
        min-height: 100%;
        margin-left: 50%;
        transform: translateX(-50%);
    }

    .message-cell {
        display: flex;
        align-items: center;
        margin-top: 10px;
    }

    .message-cell .avatar {
        width: 30px;
        min-width: 30px;
        height: 30px;
        text-align: center;
        line-height: 30px;
        font-size: 12px;
        background-color: #FFF;
        border-radius: 4px;
        margin-bottom: auto;
    }

    .message-cell .message {
        margin-left: 10px;
        font-size: 16px;
    }

    .message-cell.gpt .message {
        background-color: #FFF;
        padding: 10px;
        border-radius: 8px;
        line-height: 28px;
    }

    .message-input {
        width: 100%;
        max-width: 800px;
        margin: 10px auto;
        box-shadow: 0 2px 6px #ccc;
        padding: 10px;
        border-radius: 8px;
        display: flex;
        background-color: #FFF;
        flex-direction: column;
        position: fixed;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
    }

    .message-input .el-button {
        margin-top: 10px;
        margin-left: auto;
    }

    .title {
        position: fixed;
        left: 10px;
        top: 10px;
        font-size: 40px;
        text-shadow: 0 4px 6px #f9abab;
    }
</style>

<body>
    <div id="app">
        <div class="title">ChatGPT By Wong</div>
        <div class="message-body">
            <div v-for="item,index in listInfo" :key="index" class="message-cell"
                :class="{you:item.type==0,gpt:item.type==1}">
                <div class="avatar" v-text="item.type == 0 ? 'YOU' : 'GPT'"></div>
                <div class="message" v-html="item.text"></div>
            </div>
        </div>
        <div class="message-input">
            <el-input v-model="message" type="textarea" rows="5" placeholder="Enter your message here..."></el-input>
            <el-button type="primary" round size="small" @click="sendMessage" :loading="loading">Send</el-button>
        </div>
    </div>

    <script>
        var app = new Vue({
            el: '#app',
            data: {
                message: '',
                listInfo: [],
                loading: false
            },
            created () {
                let listInfoStr = localStorage.getItem('gpt-list-info');
                if (listInfoStr) {
                    this.listInfo = JSON.parse(listInfoStr);
                }
            },
            methods: {
                sendMessage () {
                    let message = this.message;
                    if (!message) {
                        return this.$message.error('Please enter a message!');
                    }
                    this.loading = true;
                    this.message = "";
                    this.listInfo.push({
                        text: message,
                        type: 0
                    })
                    fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ message: message })
                    })
                        .then(response => response.json())
                        .then(data => {
                            let chatBox = document.getElementById("chatBox");
                            if (data.error) {
                                this.listInfo.push({
                                    text: `Server error: ${data.error}`,
                                    type: 1,
                                    status: 'error'
                                })
                            } else {
                                this.listInfo.push({
                                    text: data.response,
                                    type: 1,
                                    status: 'ok'
                                })
                            }
                            this.loading = false;
                            localStorage.setItem('gpt-list-info', JSON.stringify(this.listInfo));
                        })
                        .catch(error => {
                            this.loading = false;
                            console.error('Error:', error);
                        });
                }
            }
        })
    </script>
</body>

</html>
    '''
    return render_template_string(html_content)

# 接收用户消息并返回 ChatGPT 的响应
# 接收用户消息并返回ChatGPT的响应
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    try:
        response = openai.chat.completions.create(
            model=FINE_TUNED_MODEL,
            messages=[{"role": "user", "content": user_message}]
        )

        # 打印返回的完整 response 数据
        print(f"Response from OpenAI: {response}")

        # 获取聊天内容（正确的访问方式）
        chat_response = response.choices[0].message['content']

        return jsonify({"response": chat_response}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 运行 Flask 应用
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
