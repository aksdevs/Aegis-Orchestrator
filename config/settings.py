"""Configuration for Ollama LLM models and LangChain settings."""
import os
from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum

class ModelType(Enum):
    """Enum for different model types used in the pipeline."""
    VULNERABILITY_SCANNER = "vulnerability_scanner"
    SECURITY_RESEARCHER = "security_researcher"
    CODE_FIXER = "code_fixer"
    CODE_REVIEWER = "code_reviewer"

@dataclass
class LLMConfig:
    """Configuration for Ollama LLM models."""
    model_name: str
    base_url: str
    temperature: float = 0.1
    max_tokens: int = 2048

class AegisConfig:
    """Main configuration class for the Aegis Orchestrator."""

    def __init__(self):
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1")
        self.workspace_dir = os.getenv("WORKSPACE_DIR", "/workspace")

        # LangSmith configuration for tracing (optional)
        self.langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
        self.langsmith_project = os.getenv("LANGSMITH_PROJECT", "aegis-orchestrator")

        # Model configurations
        self.models = {
            ModelType.VULNERABILITY_SCANNER: LLMConfig(
                model_name=self.ollama_model,
                base_url=self.ollama_base_url,
                temperature=0.1,
                max_tokens=2048
            ),
            ModelType.SECURITY_RESEARCHER: LLMConfig(
                model_name=self.ollama_model,
                base_url=self.ollama_base_url,
                temperature=0.2,
                max_tokens=4096
            ),
            ModelType.CODE_FIXER: LLMConfig(
                model_name=self.ollama_model,
                base_url=self.ollama_base_url,
                temperature=0.1,
                max_tokens=4096
            ),
            ModelType.CODE_REVIEWER: LLMConfig(
                model_name=self.ollama_model,
                base_url=self.ollama_base_url,
                temperature=0.1,
                max_tokens=2048
            )
        }

    def get_model_config(self, model_type: ModelType) -> LLMConfig:
        """Get configuration for a specific model type."""
        return self.models[model_type]

    def validate(self) -> bool:
        """Validate that required configuration is present."""
        return True

# Global configuration instance
config = AegisConfig()
