"""Configuration for Vertex AI models and LangChain settings."""
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
class VertexAIConfig:
    """Configuration for Vertex AI models."""
    project_id: str
    location: str
    model_name: str
    temperature: float = 0.1
    max_tokens: int = 2048
    top_p: float = 0.95
    top_k: int = 40

class AegisConfig:
    """Main configuration class for the Aegis Orchestrator."""
    
    def __init__(self):
        self.project_id = os.getenv("PROJECT_ID", "")
        self.location = os.getenv("REGION", "us-central1")
        self.workspace_dir = os.getenv("WORKSPACE_DIR", "/workspace")
        
        # LangSmith configuration for tracing (optional)
        self.langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
        self.langsmith_project = os.getenv("LANGSMITH_PROJECT", "aegis-orchestrator")
        
        # Model configurations
        self.models = {
            ModelType.VULNERABILITY_SCANNER: VertexAIConfig(
                project_id=self.project_id,
                location=self.location,
                model_name="gemini-pro",
                temperature=0.1,
                max_tokens=2048
            ),
            ModelType.SECURITY_RESEARCHER: VertexAIConfig(
                project_id=self.project_id,
                location=self.location,
                model_name="gemini-pro",
                temperature=0.2,
                max_tokens=4096
            ),
            ModelType.CODE_FIXER: VertexAIConfig(
                project_id=self.project_id,
                location=self.location,
                model_name="gemini-pro",
                temperature=0.1,
                max_tokens=4096
            ),
            ModelType.CODE_REVIEWER: VertexAIConfig(
                project_id=self.project_id,
                location=self.location,
                model_name="gemini-pro",
                temperature=0.1,
                max_tokens=2048
            )
        }
    
    def get_model_config(self, model_type: ModelType) -> VertexAIConfig:
        """Get configuration for a specific model type."""
        return self.models[model_type]
    
    def validate(self) -> bool:
        """Validate that required configuration is present."""
        if not self.project_id:
            raise ValueError("PROJECT_ID environment variable is required")
        return True

# Global configuration instance
config = AegisConfig()