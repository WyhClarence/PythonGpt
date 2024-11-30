import os
import openai
import logging
import json
from flask import Flask, request, jsonify, render_template_string
import sys
import io

# 设置默认编码为utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
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
            --theme-color: rgb(10, 137, 226);
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
            padding-bottom: 250px;
            background-color: #F0F0F6;
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

        .message-cell.you .avatar {
            background-color: #FFF;
        }

        .message-cell.gpt .avatar {
            background-color: var(--theme-color);
            color: #FFF;
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

        .message-input textarea {
            resize: none;
            border: 1px soid #efefef;
            border-radius: 4px;
            padding: 6px;
        }

        .message-input textarea:focus-visible {
            outline: none;
        }

        .message-input .btn-cell {
            margin-top: 10px;
            margin-left: auto;
        }

        .title {
            position: fixed;
            left: 10px;
            top: 10px;
            font-size: 40px;
            text-shadow: 0 4px 6px var(--theme-color);
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
                <textarea v-model="message" rows="7" @keyup.enter="enterMessage" placeholder="輸入你的問題,回車可發送"></textarea>
                <div class="btn-cell">
                    <el-button type="danger" round size="small" @click="clearMessage" :loading="loading">清除曆史</el-button>
                    <el-button type="primary" round size="small" color="var(--theme-color)" @click="sendMessage"
                        :loading="loading">發送</el-button>
                </div>
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
                    enterMessage () {
                        if (this.message.trim()) this.sendMessage();
                    },
                    clearMessage () {
                        localStorage.removeItem('gpt-list-info');
                        location.reload();
                    },
                    sendMessage () {
                        let message = this.message;
                        if (!message) {
                            return this.$message.error('請輸入你的問題!');
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
                                        text: `服務異常: ${data.error}`,
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


# 存储对话历史
conversation_history = []


# 接收用户消息并返回ChatGPT的响应
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    # 只保留最近的 10 条消息（或者你可以根据需要调整这个值）
    context = conversation_history[-10:]

    # 如果历史对话超过了限制，进行摘要
    if len(context) > 1:
        # 获取摘要
        summary = generate_summary(context)
        # 用摘要替换较早的历史记录
        context = [{"role": "system", "content": summary}]
    else:
        # 保留用户和助手的对话历史
        context = [{"role": msg["role"], "content": msg["content"]} for msg in context]

    # 构建消息体，确保在 context 中已经包括了历史对话（摘要或原文）
    # 这里只添加当前用户消息
    messages = context + [{"role": "user", "content": user_message}]  # 只在这里添加一次用户消息

    try:
        response = openai.chat.completions.create(
            model=FINE_TUNED_MODEL,
            messages=messages,
            temperature=0.2,  # 控制生成内容的保守性 0.0 到 0.3：模型的回答会更加确定和保守;如 0.7 到 1.0：模型的回答会更加随机、多样，适用于创意性或者不那么确定的回答场景。
            top_p=0.9,  # 如 0.1 到 0.3：限制生成的词汇范围，回答更加确定且集中在模型认为最合适的几个选项中。如 0.7 到 1.0：增加词汇范围，回答会更加多样化，适合创造性对话。
            max_tokens=150,  # 限制回答內容長度
            n=1,  # 用于指定生成多少个回答。默认情况下，n 的值为 1
        )

        # 提取回复内容
        choices = response.choices
        message = choices[0].message
        content = message.content

        # 将用户问题也添加到对话历史中
        conversation_history.append({"role": "user", "content": user_message})
        # 将助手的回复添加到对话历史中
        conversation_history.append({"role": "assistant", "content": content})
        # 返回时明确指定 utf-8 编码
        return jsonify({"response": content}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 生成对话摘要（可以使用GPT或简单规则）
def generate_summary(messages):
    # 将对话消息转换为字符串以便生成摘要
    summary_prompt = "请将以下对话总结为简短的几句话，保留关键信息，并且准确区分用户提问和助手回答：\n"

    for msg in messages:
        if msg["role"] == "user":
            summary_prompt += f"用户：{msg['content']}\n"
        else:
            summary_prompt += f"助手：{msg['content']}\n"
    logger.debug("內容：" + summary_prompt)
    try:
        # 调用 OpenAI API 生成摘要
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # 可以使用适合的模型，如微调模型
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0.5,
            max_tokens=100  # 控制摘要的长度
        )

        # 解析并返回摘要内容
        choices = response.choices
        logger.debug("摘要3：" + choices)
        message = choices[0].message
        logger.debug("摘要2：" + message)
        summary = message.content
        logger.debug("摘要：" + summary)
        return jsonify({"response": summary}), 200

    except Exception as e:
        print(f"Error generating summary: {e}")
        return ""


# 运行 Flask 应用
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
