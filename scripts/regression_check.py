import json
import os
from urllib import parse, request


BASE_URL = os.environ.get("REGRESSION_BASE_URL", "http://127.0.0.1:8000")


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

    if problems["data"]:
        get(f"/v1/problems/{problems['data'][0]['id']}", user_token)
    if notes["data"]:
        get(f"/v1/notes/{notes['data'][0]['id']}", user_token)

    admin_login = post(
        "/v1/admin/auth/login",
        {"username": "admin", "password": "admin123456"},
    )
    admin_token = admin_login["data"]["access_token"]

    get("/v1/admin/me", admin_token)
    get("/v1/admin/monitor/overview", admin_token)
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

    print("regression-check-ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
