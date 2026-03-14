import base64
from dataclasses import dataclass
import json

from openai import OpenAI  # pyright: ignore[reportMissingImports]

from app.core.config import get_settings
from app.core.exceptions import AppException


@dataclass
class LlmResponse:
    content: str
    model: str


class OpenAIClient:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise AppException(
                code=5001,
                message="OPENAI_API_KEY is not configured",
                status_code=500,
            )

        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            timeout=settings.openai_timeout_seconds,
        )

    def chat_json(
        self, *, model: str, system_prompt: str, user_prompt: str
    ) -> LlmResponse:
        try:
            response = self.client.chat.completions.create(
                model=model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except Exception as exc:
            raise AppException(
                code=5002,
                message=f"openai request failed: {exc}",
                status_code=502,
            ) from exc

        message = response.choices[0].message.content if response.choices else None
        if not message:
            raise AppException(code=5003, message="empty llm response", status_code=502)

        try:
            json.loads(message)
        except Exception as exc:
            raise AppException(
                code=5004,
                message=f"llm returned invalid json: {exc}",
                status_code=502,
            ) from exc

        return LlmResponse(content=message, model=response.model)

    def chat_json_with_image_url(
        self,
        *,
        model: str,
        system_prompt: str,
        user_prompt: str,
        image_url: str,
        image_detail: str = "auto",
    ) -> LlmResponse:
        """Chat Completions JSON-mode with multimodal user content.

        Minimal pattern for image+text classification using the existing
        chat.completions.create style and response_format json_object.

        NOTE: Chat Completions vision input uses content parts with:
          - {"type": "text", "text": ...}
          - {"type": "image_url", "image_url": {"url": ..., "detail": ...}}
        """

        try:
            response = self.client.chat.completions.create(
                model=model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url, "detail": image_detail},
                            },
                        ],
                    },
                ],
            )
        except Exception as exc:
            raise AppException(
                code=5002,
                message=f"openai request failed: {exc}",
                status_code=502,
            ) from exc

        message = response.choices[0].message.content if response.choices else None
        if not message:
            raise AppException(code=5003, message="empty llm response", status_code=502)

        try:
            json.loads(message)
        except Exception as exc:
            raise AppException(
                code=5004,
                message=f"llm returned invalid json: {exc}",
                status_code=502,
            ) from exc

        return LlmResponse(content=message, model=response.model)

    def chat_json_with_image(
        self,
        *,
        model: str,
        system_prompt: str,
        user_prompt: str,
        image_bytes: bytes,
        image_mime_type: str,
    ) -> LlmResponse:
        image_b64 = base64.b64encode(image_bytes).decode("ascii")
        image_url = f"data:{image_mime_type};base64,{image_b64}"

        try:
            response = self.client.chat.completions.create(
                model=model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    },
                ],
            )
        except Exception as exc:
            raise AppException(
                code=5002,
                message=f"openai request failed: {exc}",
                status_code=502,
            ) from exc

        message = response.choices[0].message.content if response.choices else None
        if not message:
            raise AppException(code=5003, message="empty llm response", status_code=502)

        try:
            json.loads(message)
        except Exception as exc:
            raise AppException(
                code=5004,
                message=f"llm returned invalid json: {exc}",
                status_code=502,
            ) from exc

        return LlmResponse(content=message, model=response.model)
