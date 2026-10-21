from collections.abc import Generator
from typing import Optional, Union

import requests

from dify_plugin import OAICompatLargeLanguageModel
from dify_plugin.entities.model import AIModelEntity, ModelFeature
from dify_plugin.entities.model.llm import LLMMode, LLMResult
from dify_plugin.entities.model.message import PromptMessage, PromptMessageTool

AIAND_API_BASE = "https://api.aiand.com/v1"


class AiandLargeLanguageModel(OAICompatLargeLanguageModel):
    def _invoke(
        self,
        model: str,
        credentials: dict,
        prompt_messages: list[PromptMessage],
        model_parameters: dict,
        tools: Optional[list[PromptMessageTool]] = None,
        stop: Optional[list[str]] = None,
        stream: bool = True,
        user: Optional[str] = None,
    ) -> Union[LLMResult, Generator]:
        self._add_custom_parameters(credentials)
        self._add_function_call(model, credentials)
        if stream:
            model_parameters["stream_options"] = {"include_usage": True}
        return super()._invoke(model, credentials, prompt_messages, model_parameters, tools, stop, stream, user)

    def _handle_generate_response(
        self,
        model: str,
        credentials: dict,
        response: requests.Response,
        prompt_messages: list[PromptMessage],
    ) -> LLMResult:
        # A blocking tool-call reply has `content: null` (as on OpenAI). The SDK needs a string to count
        # tokens, and Dify's plugin daemon rejects a message without content, so normalise it first.
        body = response.json()
        for choice in body.get("choices", []):
            message = choice.get("message")
            if message is not None and message.get("content") is None:
                message["content"] = ""
        response.json = lambda **_: body
        return super()._handle_generate_response(model, credentials, response, prompt_messages)

    def validate_credentials(self, model: str, credentials: dict) -> None:
        self._add_custom_parameters(credentials)
        super().validate_credentials(model, credentials)

    def get_customizable_model_schema(self, model: str, credentials: dict) -> AIModelEntity:
        self._add_custom_parameters(credentials)
        return super().get_customizable_model_schema(model, credentials)

    def get_num_tokens(
        self,
        model: str,
        credentials: dict,
        prompt_messages: list[PromptMessage],
        tools: Optional[list[PromptMessageTool]] = None,
    ) -> int:
        self._add_custom_parameters(credentials)
        return super().get_num_tokens(model, credentials, prompt_messages, tools)

    @staticmethod
    def _add_custom_parameters(credentials: dict) -> None:
        credentials["endpoint_url"] = AIAND_API_BASE
        credentials["mode"] = LLMMode.CHAT.value

    def _add_function_call(self, model: str, credentials: dict) -> None:
        if "function_calling_type" in credentials:
            return
        model_schema = self.get_model_schema(model, credentials)
        features = (model_schema.features or []) if model_schema else []
        if ModelFeature.TOOL_CALL in features or ModelFeature.MULTI_TOOL_CALL in features:
            credentials["function_calling_type"] = "tool_call"
