from datetime import datetime, timezone

from flask import Flask, jsonify, request, url_for
from werkzeug.exceptions import HTTPException


app = Flask(__name__)
app.json.ensure_ascii = False

tasks = [
    {"id": 1, "title": "整理 API 文件", "description": "補上端點使用說明"},
    {"id": 2, "title": "檢查部署設定", "description": "確認正式環境參數"},
]
next_task_id = 3


def success_response(message, data, status_code=200):
    return jsonify({"status": "success", "message": message, "data": data}), status_code


def error_response(message, status_code):
    return jsonify({"status": "error", "message": message, "data": None}), status_code


@app.errorhandler(HTTPException)
def handle_http_exception(error):
    if error.code == 404:
        message = "找不到指定路徑"
    else:
        message = error.name
    return error_response(message, error.code)


@app.get("/api/health")
def health_check():
    data = {
        "server": "running",
        "time": datetime.now(timezone.utc).isoformat(),
    }
    return success_response("服務正常", data)


@app.get("/api/tasks")
def get_tasks():
    return success_response("取得任務清單成功", tasks)


@app.post("/api/tasks")
def create_task():
    global next_task_id

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return error_response("請提供合法的 JSON 物件", 400)

    title = payload.get("title")
    if not isinstance(title, str) or not title.strip():
        return error_response("缺少必填欄位 title", 400)

    task = {
        "id": next_task_id,
        "title": title,
        "description": payload.get("description", ""),
    }
    next_task_id += 1
    tasks.append(task)

    response, status_code = success_response("新增任務成功", task, 201)
    response.headers["Location"] = url_for("get_task", task_id=task["id"])
    return response, status_code


@app.get("/api/tasks/<int:task_id>")
def get_task(task_id):
    task = next((item for item in tasks if item["id"] == task_id), None)
    if task is None:
        return error_response("找不到指定任務", 404)
    return success_response("取得任務成功", task)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)