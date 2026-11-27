"""Khung chạy bản chạy thử tối thiểu (dòng lệnh): gõ đầu vào → answer() trong agent.py → in kết quả.

Chạy bằng: python run.py   (macOS/Linux có thể là python3, Windows có thể là py)
Nhóm thay bằng giao diện của mình (web, bot…) nhưng giữ `python run.py` là lệnh duy nhất
để chạy bản chạy thử (sửa hàm run_app() trong run.py nếu cần).
"""
import os
import sys

for _stream in (sys.stdout, sys.stderr, sys.stdin):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _where(e):
    """File (trong codebase/) gây lỗi khi nạp: SyntaxError có e.filename, lỗi khác lấy khung cuối của traceback."""
    import traceback
    path = getattr(e, "filename", None) or (traceback.extract_tb(e.__traceback__)[-1].filename if e.__traceback__ else "")
    if not path:
        return "codebase/"
    p = os.path.abspath(path)
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.relpath(p, base).replace(os.sep, "/") if p.startswith(base) else path

HELP = ("Dán đoạn chat nhóm (tên một dòng, tin nhắn dòng dưới), kết thúc bằng một dòng trống.\n"
        "Sau đó nhắn tiếp như chat. Lệnh: /xacnhan (xác nhận hồ sơ) · /chot (chốt giỏ) · /moi (phiên mới) · /thoat.")


def read_message(lines):
    """Gom các dòng tới dòng trống thành một tin (bỏ dòng trống ở đầu). Hết input thì None."""
    collected = []
    for line in lines:
        line = line.rstrip("\r\n")
        if not line.strip():
            if collected:
                break
            continue
        collected.append(line)
    return "\n".join(collected) if collected else None


def _stdin_lines():
    while True:
        try:
            yield input("> ")
        except (EOFError, KeyboardInterrupt):
            return


def main() -> int:
    try:
        import tracing
        import core
        from llm_steps import AIUnavailable
    except Exception as e:  # lỗi cú pháp, thiếu thư viện… trong codebase/
        print("Không nạp được codebase/ — lỗi ở %s: %s: %s" % (_where(e), type(e).__name__, e))
        print("Sửa lỗi rồi chạy lại. Cách nối model: docs/connect-model.md")
        return 1
    print(HELP)
    lines = _stdin_lines()
    session = None
    while True:
        text = read_message(lines)
        if text is None or text.strip() == "/thoat":
            print()
            return 0
        command = text.strip()
        if command == "/moi":
            session = None
            print("Đã bắt đầu phiên mới. Dán đoạn chat nhóm.")
            continue
        tracing.begin("app")
        try:
            if session is None:
                session = core.start(text)
            elif command == "/xacnhan":
                session = core.confirm(session)
            elif command == "/chot":
                session = core.finalize(session)
            else:
                session = core.send(session, text)
            output = core.render(session)
        except AIUnavailable:
            output = "Hệ thống AI tạm thời không phản hồi, vui lòng thử lại."
        except NotImplementedError as e:
            tracing.end()
            print("Chưa nối model: %s" % e)
            return 1
        except Exception as e:  # lỗi gọi model: báo rồi cho nhắn tiếp
            tracing.end()
            print("[lỗi] %s: %s" % (type(e).__name__, e))
            continue
        s, _ = tracing.end()
        print(output)
        print("   (model: %s · gọi model %d lần · công cụ %d lần · token vào %d / ra %d)"
              % (", ".join(s["models"]) or "—", s["model_calls"], s["tool_calls"], s["tokens_in"], s["tokens_out"]))


if __name__ == "__main__":
    sys.exit(main())
