from datetime import datetime, timezone
import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from sqlalchemy import text
from werkzeug.exceptions import HTTPException

from extensions import db


def success_response(message, data, status_code=200):
    return jsonify({"code": status_code, "message": message, "data": data}), status_code


def error_response(message, status_code):
    return jsonify({"code": status_code, "message": message, "data": None}), status_code


def create_app(test_config=None):
    load_dotenv()

    app = Flask(__name__)
    app.json.ensure_ascii = False

    database_url = None
    if test_config and "DATABASE_URL" in test_config:
        database_url = test_config["DATABASE_URL"]
    else:
        database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("未設定 DATABASE_URL 環境變數，請在 .env 或系統環境變數中設定 PostgreSQL 連線字串。")

    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        if error.code == 404:
            message = "找不到這一筆"
        else:
            message = error.name
        return error_response(message, error.code)

    @app.get("/api/health")
    def health_check():
        data = {
            "status": "ok",
            "time": datetime.now(timezone.utc).isoformat(),
        }
        return success_response("伺服器運作正常，測試正常可以進行其他任務。", data, 200)

    @app.get("/api/health/db")
    def health_check_db():
        try:
            db.session.execute(text("SELECT 1"))
            return success_response("資料庫連線正常", {"status": "ok"}, 200)
        except Exception as e:
            db.session.rollback()
            app.logger.error("資料庫連線檢查失敗: %s", e, exc_info=True)
            return error_response("資料庫暫時連不上", 500)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)