import json
import os
import os
import uuid
from urllib import parse, request


BASE_URL = os.environ.get("REGRESSION_BASE_URL", "http://127.0.0.1:8000")


def request_json(
    method: str,
    path: str,
    payload: dict | None = None,
    token: str | None = None,
) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = request.Request(f"{BASE_URL}{path}", data=data, method=method)
    if payload is not None:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def post(path: str, payload: dict, token: str | None = None) -> dict:
    return request_json("POST", path, payload, token)


def put(path: str, payload: dict, token: str | None = None) -> dict:
    return request_json("PUT", path, payload, token)


def delete(path: str, token: str | None = None) -> dict:
    return request_json("DELETE", path, None, token)


def get(path: str, token: str | None = None) -> dict:
    req = request.Request(f"{BASE_URL}{path}")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def post_multipart(
    path: str,
    fields: dict[str, str],
    files: dict[str, tuple[str, bytes, str]],
    token: str | None = None,
) -> dict:
    boundary = f"----regression-{uuid.uuid4().hex}"
    body = bytearray()

    for name, value in fields.items():
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8")
        )
        body.extend(str(value).encode("utf-8"))
        body.extend(b"\r\n")

    for name, (filename, content, mime_type) in files.items():
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(
            (
                f'Content-Disposition: form-data; name="{name}"; '
                f'filename="{filename}"\r\n'
            ).encode("utf-8")
        )
        body.extend(f"Content-Type: {mime_type}\r\n\r\n".encode("utf-8"))
        body.extend(content)
        body.extend(b"\r\n")

    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    req = request.Request(f"{BASE_URL}{path}", data=bytes(body), method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    user_login = post(
        "/v1/auth/login", {"username": "demo_user", "password": "user123456"}
    )
    user_token = user_login["data"]["access_token"]

    get("/v1/me", user_token)
    get("/v1/dashboard", user_token)
    problems = get("/v1/problems", user_token)
    notes = get("/v1/notes", user_token)
    get(f"/v1/search?{parse.urlencode({'q': '方程'})}", user_token)
    get("/v1/graph/overview", user_token)
    get("/v1/graph/weak-tags", user_token)
    preview = post(
        "/v1/preview/upload-tags",
        {
            "filename": "regression-preview.txt",
            "mime_type": "text/plain",
            "file_kind": "document",
            "content_type": "note",
            "subject": "math",
            "text_content": "解方程 x^2 - 5x + 6 = 0，总结知识点与关键步骤。",
        },
        user_token,
    )
    if preview["data"]["subject"] != "math":
        raise RuntimeError("preview did not preserve subject")
    if not preview["data"]["normalized_text"]:
        raise RuntimeError("preview missing normalized_text")
    if "knowledge_candidates" not in preview["data"]:
        raise RuntimeError("preview missing knowledge_candidates")

    upload_policy = post(
        "/v1/files/upload-policy",
        {
            "filename": "regression-upload.txt",
            "mime_type": "text/plain",
            "content_type": "note",
            "file_kind": "document",
        },
        user_token,
    )
    upload_local = post_multipart(
        "/v1/files/upload-local",
        {
            "file_id": str(upload_policy["data"]["file_id"]),
            "object_key": upload_policy["data"]["object_key"],
        },
        {
            "upload_file": (
                "regression-upload.txt",
                "regression upload body".encode("utf-8"),
                "text/plain",
            )
        },
        user_token,
    )
    if upload_local["data"]["bytes_written"] <= 0:
        raise RuntimeError("upload-local did not write bytes")

    confirm_upload = post(
        "/v1/files/confirm",
        {
            "file_id": upload_policy["data"]["file_id"],
            "object_key": upload_policy["data"]["object_key"],
            "size_bytes": upload_local["data"]["bytes_written"],
            "mime_type": "text/plain",
            "sha256": "regression-upload-sha",
        },
        user_token,
    )
    if not confirm_upload["data"]["file_url"].startswith("/uploads/"):
        raise RuntimeError("confirm after upload-local missing uploads file_url")

    confirmed_note = post(
        "/v1/notes/confirm",
        {
            "file_id": upload_policy["data"]["file_id"],
            "source_type": "upload",
            "entity_type": preview["data"]["entity_type"],
            "content_category": preview["data"]["content_category"],
            "subject": preview["data"]["subject"],
            "title": f"Regression note {uuid.uuid4().hex[:8]}",
            "summary": preview["data"].get("summary", ""),
            "normalized_text": preview["data"]["normalized_text"],
            "knowledge_candidates": preview["data"]["knowledge_candidates"],
            "confidence": preview["data"]["confidence"],
            "needs_review": preview["data"].get("needs_review", False),
            "review_reason": preview["data"].get("review_reason", ""),
        },
        user_token,
    )
    confirmed_note_id = confirmed_note["data"]["id"]
    if confirmed_note["data"]["file_id"] != upload_policy["data"]["file_id"]:
        raise RuntimeError("notes confirm did not preserve file_id")

    ingestion_skipped = post(
        "/v1/ingestions",
        {
            "entity_type": "note",
            "file_id": upload_policy["data"]["file_id"],
            "text_content": "ingestion skipped regression body",
            "subject": "math",
            "source_type": "upload",
            "content_category": "note",
            "auto_parse": False,
        },
        user_token,
    )
    if ingestion_skipped["data"]["parse_job_id"] is not None:
        raise RuntimeError("ingestion auto_parse=false should not create parse_job")
    if ingestion_skipped["data"]["parse_status"] != "skipped":
        raise RuntimeError("ingestion auto_parse=false should return skipped status")

    ingestion_pending = post(
        "/v1/ingestions",
        {
            "entity_type": "problem",
            "text_content": "已知 x^2 - 1 = 0，求 x。",
            "subject": "math",
            "source_type": "manual",
            "content_category": "problem",
            "auto_parse": True,
        },
        user_token,
    )
    if ingestion_pending["data"]["parse_job_id"] is None:
        raise RuntimeError("ingestion auto_parse=true should create parse_job")
    if ingestion_pending["data"]["parse_status"] != "pending":
        raise RuntimeError("ingestion auto_parse=true should return pending status")

    solve = post(
        "/v1/solve",
        {
            "question_text": "解方程 x^2 - 5x + 6 = 0",
            "subject": "math",
            "allow_ai_fallback": True,
        },
        user_token,
    )
    if not solve["data"]["final_answer"]:
        raise RuntimeError("user flow solve missing final_answer")

    delete_note_result = delete(f"/v1/notes/{confirmed_note_id}", user_token)
    if delete_note_result["data"]["status"] != "deleted":
        raise RuntimeError("note delete did not return deleted status")

    if problems["data"]:
        get(f"/v1/problems/{problems['data'][0]['id']}", user_token)
    if notes["data"]:
        get(f"/v1/notes/{notes['data'][0]['id']}", user_token)

    admin_password = os.environ.get("REGRESSION_ADMIN_PASSWORD")
    if not admin_password:
        raise RuntimeError("REGRESSION_ADMIN_PASSWORD is required")

    admin_login = post(
        "/v1/admin/auth/login",
        {"username": "admin", "password": admin_password},
    )
    admin_token = admin_login["data"]["access_token"]

    get("/v1/admin/me", admin_token)
    get("/v1/admin/monitor/overview", admin_token)
    runtime_before = get("/v1/admin/runtime-config/models", admin_token)
    runtime_payload = {
        "solve": {
            "vendor": "openai-compatible",
            "base_url": "http://runtime-regression-solve",
            "api_key": f"regression-solve-{uuid.uuid4().hex[:8]}",
            "model_name": f"regression-solve-{uuid.uuid4().hex[:8]}",
        },
        "classify": {
            "vendor": "openai-compatible",
            "base_url": "http://runtime-regression-classify",
            "api_key": f"regression-classify-{uuid.uuid4().hex[:8]}",
            "model_name": f"regression-classify-{uuid.uuid4().hex[:8]}",
        },
    }
    runtime_after = put(
        "/v1/admin/runtime-config/models",
        runtime_payload,
        admin_token,
    )
    if (
        runtime_after["data"]["solve"]["model_name"]
        != runtime_payload["solve"]["model_name"]
    ):
        raise RuntimeError(
            "runtime-config solve update did not persist in PUT response"
        )
    if (
        runtime_after["data"]["classify"]["model_name"]
        != runtime_payload["classify"]["model_name"]
    ):
        raise RuntimeError(
            "runtime-config classify update did not persist in PUT response"
        )

    runtime_roundtrip = get("/v1/admin/runtime-config/models", admin_token)
    if (
        runtime_roundtrip["data"]["solve"]["model_name"]
        != runtime_payload["solve"]["model_name"]
    ):
        raise RuntimeError("runtime-config solve roundtrip mismatch")
    if (
        runtime_roundtrip["data"]["classify"]["model_name"]
        != runtime_payload["classify"]["model_name"]
    ):
        raise RuntimeError("runtime-config classify roundtrip mismatch")

    parse_jobs = get("/v1/admin/parse-jobs", admin_token)
    review_tasks = get("/v1/review/tasks?status=pending", admin_token)

    if parse_jobs["data"]:
        failed_job = next(
            (job for job in parse_jobs["data"] if job["status"] == "failed"), None
        )
        if failed_job:
            retry = post(f"/v1/parse-jobs/{failed_job['id']}/retry", {}, admin_token)
            if retry["data"]["status"] != "pending":
                raise RuntimeError("admin retry did not return pending status")

    if review_tasks["data"]:
        review_id = review_tasks["data"][0]["id"]
        decision = post(
            f"/v1/review/tasks/{review_id}/decision",
            {"action": "approve", "edited_tags": []},
            admin_token,
        )
        if decision["data"]["status"] != "approved":
            raise RuntimeError("review decision did not return approved status")

    put("/v1/admin/runtime-config/models", runtime_before["data"], admin_token)

    print("regression-check-ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
