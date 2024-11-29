import openai
import json
import os
import time

# 从环境变量中获取 OpenAI API Key，或者手动设置
openai.api_key = os.getenv("OPENAI_API_KEY")
if openai.api_key is None:
    openai.api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 上传训练数据
def upload_training_data(file_path):
    try:
        with open(file_path, "rb") as f:
            response = openai.files.create(
                file=f,
                purpose='fine-tune'
            )
        # 由于新版 API 返回的是一个对象，而不是字典类型，使用 model_dump() 来提取信息
        response_dict = response.model_dump()
        print(f"Training data uploaded successfully. File ID: {response_dict['id']}")
        return response_dict['id']
    except Exception as e:
        print(f"Error uploading training data: {e}")
        return None


# 读取 Fine-Tuned 模型的 ID
with open("fine_tuned_model.json", "r") as f:
    fine_tuned_data = json.load(f)
    FINE_TUNED_MODEL = fine_tuned_data.get("fine_tuned_model_id")

# 启动 Fine-Tuning 任务
def start_fine_tuning(training_file_id, model=FINE_TUNED_MODEL):
    try:
        response = openai.fine_tuning.jobs.create(
            training_file=training_file_id,
            model=model
        )
        response_dict = response.model_dump()
        print(f"Fine-Tuning job started successfully. Job ID: {response_dict['id']}")
        return response_dict['id']
    except Exception as e:
        print(f"Error starting Fine-Tuning job: {e}")
        return None

# 查询 Fine-Tuning 任务状态并打印详细的失败信息
def check_fine_tune_status(job_id):
    try:
        status_response = openai.fine_tuning.jobs.retrieve(job_id)
        status_dict = status_response.model_dump()
        print(f"Fine-Tune Job Status: {status_dict['status']}")

        if status_dict['status'] == 'failed':
            # 打印详细的错误信息
            print("Fine-Tune Job Failed Details:")
            if 'error' in status_dict:
                print(status_dict['error'])

        return status_dict
    except Exception as e:
        print(f"Error checking Fine-Tune status: {e}")
        return None


# 将 Fine-Tuned 模型 ID 保存到文件
def save_fine_tuned_model_id(job_id, output_file="fine_tuned_model.json"):
    status_response = check_fine_tune_status(job_id)
    if status_response and status_response['status'] == 'succeeded':
        fine_tuned_model_id = status_response['fine_tuned_model']
        with open(output_file, "w") as file:
            json.dump({"fine_tuned_model_id": fine_tuned_model_id}, file)
        print(f"Fine-Tuned model ID saved to {output_file}: {fine_tuned_model_id}")
    else:
        print("Fine-Tuning job has not completed successfully. Unable to save model ID.")

# 主逻辑
if __name__ == "__main__":
    # Step 1: 上传训练数据
    training_file_path = "training_data.jsonl"  # 训练数据的文件路径
    training_file_id = upload_training_data(training_file_path)

    if training_file_id:
        # Step 2: 启动 Fine-Tuning 任务
        fine_tune_job_id = start_fine_tuning(training_file_id)

        # Step 3: 等待任务完成并检查状态
        if fine_tune_job_id:
            while True:
                status_response = check_fine_tune_status(fine_tune_job_id)
                if status_response and status_response['status'] in ['succeeded', 'failed']:
                    break
                time.sleep(30)  # 每隔 30 秒检查一次状态

            # Step 4: 保存 Fine-Tuned 模型 ID
            save_fine_tuned_model_id(fine_tune_job_id)
