'''
Author: lbh
Date: 2024-11-29 09:43:56
LastEditors: lbh
LastEditTime: 2024-11-29 10:09:34
Description: file content
'''
from openai import OpenAI
import json
import sys
import io
# 设置默认编码为utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

key = "";
# 实例化一个 OpenAI 客户端
client = OpenAI(api_key=key)
# 读取 Fine-Tuned 模型的 ID
with open("fine_tuned_model.json", "r") as f:
    fine_tuned_data = json.load(f)
    FINE_TUNED_MODEL = fine_tuned_data.get("fine_tuned_model_id")
user_message = "介紹一下RicePOS";
# 使用显式实例化客户端调用 API
response = client.chat.completions.create(
  model=FINE_TUNED_MODEL,
  messages=[
      {"role": "user", "content": user_message},
      # {"role":"system", "content": "當你尋找不到答案時,需要結合網絡資訊回答問題"}
  ]
)


choices = response.choices
print("choices" , choices)

message = choices[0].message
print('message',message)
content = message.content
print('content',content)

# 提取回复内容
# chat_response = response['choices'][0]['message']['content']

# print(chat_response)