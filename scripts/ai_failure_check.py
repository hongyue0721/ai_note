import sys
from unittest.mock import patch


def main() -> int:
    if "/app" not in sys.path:
        sys.path.insert(0, "/app")

    from app.services.classifier import classify_content
    from app.services.llm_client import OpenAIClient
    from app.services.solver import solve_with_ai

    with patch.object(
        OpenAIClient,
        "chat_json",
        return_value=type(
            "Resp", (), {"content": "plain text, not json", "model": "fake-model"}
        )(),
    ):
        try:
            solve_with_ai(question_text="1+1=?", subject="math")
            print("solver_non_json:UNEXPECTED_SUCCESS")
        except Exception as exc:
            print(
                "solver_non_json:code={};message={}".format(
                    getattr(exc, "code", "NO_CODE"),
                    getattr(exc, "message", str(exc)),
                )
            )

        try:
            classify_content(
                text_content="示例文本",
                file_kind="image",
                content_category="problem",
            )
            print("classifier_non_json:UNEXPECTED_SUCCESS")
        except Exception as exc:
            print(
                "classifier_non_json:code={};message={}".format(
                    getattr(exc, "code", "NO_CODE"),
                    getattr(exc, "message", str(exc)),
                )
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
