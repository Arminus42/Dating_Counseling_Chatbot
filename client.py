import os
import json
import requests

BASE_URL = "http://localhost:8000/chat"
SESSION_FILE = "session_id.txt"

def load_session_id():
    if os.path.exists(SESSION_FILE):
        sid = open(SESSION_FILE, "r", encoding="utf-8").read().strip()
        return sid if sid else None
    return None

def save_session_id(sid: str):
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        f.write(sid)

def reset_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

def is_json_like(s: str) -> bool:
    s = s.strip()
    return s.startswith("{")

def read_multiline_json(first_line: str) -> str:
    lines = [first_line]
    while True:
        joined = "\n".join(lines).strip()
        if joined.endswith("}"):
            return joined
        nxt = input("... ")
        lines.append(nxt)

def build_payload_from_input(user_input: str):
    user_input = user_input.strip()

    if is_json_like(user_input):
        raw = read_multiline_json(user_input)
        try:
            payload = json.loads(raw)
            if not isinstance(payload, dict):
                raise ValueError("JSON must be an object (dictionary).")
            return payload
        except Exception as e:
            raise ValueError(
                "JSON parsing failed. Check commas/quotes.\n"
                f"Reason: {e}"
            )

    return {
        "user_gender": "남",
        "character": "유재석",
        "message": user_input
    }

def send(payload: dict):
    if "message" not in payload or not str(payload["message"]).strip():
        raise ValueError("payload must include non-empty 'message'.")

    if "user_gender" not in payload:
        raise ValueError("payload must include 'user_gender' (e.g., '남' or '여').")

    if "character" not in payload:
        raise ValueError("payload must include 'character' (e.g., '박명수').")

    sid = load_session_id()
    if "session_id" not in payload and sid:
        payload["session_id"] = sid

    res = requests.post(BASE_URL, json=payload)
    if not res.ok:
        try:
            err = res.json()
        except:
            err = res.text
        raise RuntimeError(f"HTTP {res.status_code}: {err}")

    data = res.json()

    if "session_id" in data and data["session_id"]:
        save_session_id(data["session_id"])

    return data

def main():
    print("=== JSON Chat Client (auto session_id) ===")
    print("✅ Paste JSON object each time (multi-line ok).")
    print("Commands: exit / reset")
    print("Tip: JSON needs double quotes \" \" and commas.")
    print("")

    while True:
        user_input = input("YOU: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "exit":
            break

        if user_input.lower() == "reset":
            reset_session()
            print("✅ Session cleared. Next request starts a new session.")
            continue

        try:
            payload = build_payload_from_input(user_input)
            resp = send(payload)

            bot_text = resp.get("response", "")
            sid = resp.get("session_id", "")
            print(f"BOT: {bot_text}")
            print(f"(session_id saved: {sid})")
        except Exception as e:
            print("❌ Error:", e)

if __name__ == "__main__":
    main()
