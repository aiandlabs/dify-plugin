from dify_plugin import ModelProvider
from dify_plugin.entities.model import ModelType


class AiandModelProvider(ModelProvider):
    def validate_provider_credentials(self, credentials: dict) -> None:
        # Any shipped model works for the SDK's 5-token ping, and the shipped list is regenerated from the
        # live catalog, so this never points at a retired model.
        llm = self.get_model_instance(ModelType.LLM)
        llm.validate_credentials(model=llm.predefined_models()[0].model, credentials=credentials)
