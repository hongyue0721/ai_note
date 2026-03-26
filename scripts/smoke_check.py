import json
import os
from urllib import request


BASE_URL = os.environ.get("SMOKE_BASE_URL", "http://127.0.0.1:8000")


def post(path: str, payload: dict, token: str | None = None) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(f"{BASE_URL}{path}", data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get(path: str, token: str | None = None) -> dict:
    req = request.Request(f"{BASE_URL}{path}")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_text(path: str) -> tuple[int, str]:
    req = request.Request(f"{BASE_URL}{path}")
    with request.urlopen(req) as resp:
        return resp.status, resp.read().decode("utf-8")


def main() -> int:
    get("/healthz")
    login = post("/v1/auth/login", {"username": "demo_user", "password": "user123456"})
    token = login["data"]["access_token"]

    get("/v1/me", token)
    problems = get("/v1/problems", token)
    notes = get("/v1/notes", token)
    get("/v1/search?q=%E6%96%B9%E7%A8%8B", token)
    get("/v1/graph/overview", token)
    get("/v1/graph/weak-tags", token)

    if problems["data"]:
        get(f"/v1/problems/{problems['data'][0]['id']}", token)
    if notes["data"]:
        get(f"/v1/notes/{notes['data'][0]['id']}", token)

    solve = post(
        "/v1/solve",
        {
            "question_text": "解方程 x^2 - 5x + 6 = 0",
            "subject": "math",
            "allow_ai_fallback": True,
        },
        token,
    )
    if not solve["data"]["final_answer"]:
        raise RuntimeError("solve did not return final_answer")

    policy = post(
        "/v1/files/upload-policy",
        {
            "filename": "smoke-check.png",
            "mime_type": "image/png",
            "content_type": "problem",
            "file_kind": "image",
        },
        token,
    )
    confirm = post(
        "/v1/files/confirm",
        {
            "file_id": policy["data"]["file_id"],
            "object_key": policy["data"]["object_key"],
            "size_bytes": 321,
            "mime_type": "image/png",
            "sha256": "smoke-check-sha",
        },
        token,
    )
    if not confirm["data"]["file_url"].startswith("/uploads/"):
        raise RuntimeError("confirm did not return uploads file_url")

    local_object_key = policy["data"]["object_key"]
    local_root = os.environ.get("SMOKE_UPLOADS_ROOT", "data/uploads")
    local_file_path = os.path.join(local_root, *local_object_key.split("/"))
    os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
    with open(local_file_path, "w", encoding="utf-8") as fp:
        fp.write("smoke-static-ok")

    status, body = get_text(confirm["data"]["file_url"])
    if status != 200 or body != "smoke-static-ok":
        raise RuntimeError("uploads static file verification failed")

    print("smoke-check-ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
