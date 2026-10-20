import logging

from dify_plugin import ModelProvider
from dify_plugin.entities.model import ModelType
from dify_plugin.errors.model import CredentialsValidateFailedError

logger = logging.getLogger(__name__)

# Answers without reasoning by default, so validation is fast and cheap.
VALIDATION_MODEL = "google/gemma-4-31b-it"


class AiandModelProvider(ModelProvider):
    def validate_provider_credentials(self, credentials: dict) -> None:
        try:
            model_instance = self.get_model_instance(ModelType.LLM)
            model_instance.validate_credentials(model=VALIDATION_MODEL, credentials=credentials)
        except CredentialsValidateFailedError:
            raise
        except Exception:
            logger.exception("ai& credentials validation failed")
            raise
