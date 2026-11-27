"""Nối model — chỗ DUY NHẤT trong bản chạy thử gọi model AI. NHÓM VIẾT phần gọi model thật.

Hợp đồng (giữ nguyên để khung đo được token):
    call_model(system: str, user: str) -> dict với 4 khoá
        "text":       str   chữ model trả về
        "model":      str   tên model đã gọi (để tra giá ở bảng giá model)
        "tokens_in":  int   số token vào, lấy từ trường usage trong phản hồi API — KHÔNG ước lượng
        "tokens_out": int   số token ra, gồm cả token suy luận / suy nghĩ nếu API tính riêng
    @model_call (từ tracing.py) tự ghi mỗi lần gọi vào trace; agent.py gọi call_model bao nhiêu lần
    cũng được, khung tự cộng token.
    Lỗi gọi model (hết lượt, sai key, mất mạng): cứ để exception bay ra — khung ghi lỗi vào cột error.

Chế độ giả (mặc định khi .env chưa có MODEL_PROVIDER, hoặc MODEL_PROVIDER=fake):
    trả một câu giả cố định, model "fake", token 0 — để luồng chạy hết từ trước CP2 (guide bước 3.2).
    Lượt `run.py eval` / `run.py simulate` chạy bằng model giả KHÔNG được tính.

Nối model thật: điền .env (chép từ .env.example). Hỗ trợ OpenRouter, OpenAI, Anthropic và Ollama.
Không dán API key vào file này.
"""
import os
import json
from urllib import request

from tracing import model_call

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_env(path=os.path.join(ROOT, ".env")):
    """Đọc file .env (KEY=VALUE mỗi dòng) vào biến môi trường, không ghi đè biến đã có. Khung — không cần sửa."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()
MODEL_PROVIDER = (os.environ.get("MODEL_PROVIDER") or "fake").strip().lower()
MODEL_NAME = (os.environ.get("MODEL_NAME") or "").strip()
API_KEY = (os.environ.get("API_KEY") or "").strip()


def _post_json(url, headers, payload, timeout=60):
    req = request.Request(url, data=json.dumps(payload).encode("utf-8"),
                          headers={"Content-Type": "application/json", **headers}, method="POST")
    with request.urlopen(req, timeout=timeout) as response:
        return json.load(response)


@model_call
def call_model(system: str, user: str) -> dict:
    if MODEL_PROVIDER == "fake":
        last = (user.strip().splitlines() or [""])[-1]
        return {"text": "[câu trả lời giả — chưa nối model] " + last[:60], "model": "fake", "tokens_in": 0, "tokens_out": 0}
    if not MODEL_NAME or (MODEL_PROVIDER in ("openai", "anthropic", "openrouter") and not API_KEY):
        raise RuntimeError("Thiếu MODEL_NAME hoặc API_KEY trong cấu hình model.")
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
    if MODEL_PROVIDER == "openrouter":
        data = _post_json("https://openrouter.ai/api/v1/chat/completions",
                          {"Authorization": "Bearer " + API_KEY, "X-Title": "K5-D2-Lion"},
                          {"model": MODEL_NAME, "messages": messages, "temperature": 0}, timeout=90)
        text = data["choices"][0]["message"]["content"]
        tokens_in, tokens_out = data["usage"]["prompt_tokens"], data["usage"]["completion_tokens"]
    elif MODEL_PROVIDER == "openai":
        data = _post_json("https://api.openai.com/v1/chat/completions", {"Authorization": "Bearer " + API_KEY},
                          {"model": MODEL_NAME, "messages": messages})
        text = data["choices"][0]["message"]["content"]
        tokens_in, tokens_out = data["usage"]["prompt_tokens"], data["usage"]["completion_tokens"]
    elif MODEL_PROVIDER == "anthropic":
        data = _post_json("https://api.anthropic.com/v1/messages", {"x-api-key": API_KEY, "anthropic-version": "2023-06-01"},
                          {"model": MODEL_NAME, "max_tokens": 4096, "system": system or "",
                           "messages": [{"role": "user", "content": user}]})
        text = "".join(block.get("text", "") for block in data["content"] if block.get("type") == "text")
        tokens_in, tokens_out = data["usage"]["input_tokens"], data["usage"]["output_tokens"]
    elif MODEL_PROVIDER == "ollama":
        data = _post_json("http://localhost:11434/api/chat", {},
                          {"model": MODEL_NAME, "messages": messages, "stream": False}, timeout=300)
        text = data["message"]["content"]
        tokens_in, tokens_out = data["prompt_eval_count"], data["eval_count"]
    else:
        raise RuntimeError("MODEL_PROVIDER chưa được hỗ trợ: %s" % MODEL_PROVIDER)
    if not isinstance(text, str):
        raise ValueError("Model không trả văn bản.")
    return {"text": text, "model": MODEL_NAME, "tokens_in": int(tokens_in), "tokens_out": int(tokens_out)}
