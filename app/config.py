"""
Application configuration using Pydantic Settings.
Loads environment variables for MongoDB connection, security, and app settings.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "MongoDB News API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_HOST: str = "localhost"
    MONGODB_PORT: int = 27017
    MONGODB_USERNAME: str = ""
    MONGODB_PASSWORD: str = ""
    MONGODB_DB_NAME: str = "novoxpert"
    MONGODB_COLLECTION_NAME: str = "news"
    MONGODB_MIN_POOL_SIZE: int = 10
    MONGODB_MAX_POOL_SIZE: int = 50
    MONGODB_AUTH_SOURCE: str = "admin"  # Authentication database
    
    # Security
    API_KEYS: str = ""  # Comma-separated list of API keys
    
    # Pagination
    DEFAULT_PAGE_LIMIT: int = 100
    MAX_PAGE_LIMIT: int = 1000
    MIN_PAGE_LIMIT: int = 10
    
    # CORS
    CORS_ORIGINS: str = "*"  # Comma-separated list of allowed origins
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "GET,POST,PUT,DELETE,OPTIONS"
    CORS_ALLOW_HEADERS: str = "*"
    
    # Rate Limiting (requests per hour)
    RATE_LIMIT_PER_HOUR: int = 1000
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    def get_api_keys(self) -> List[str]:
        """Parse API keys from comma-separated string."""
        if not self.API_KEYS:
            return []
        return [key.strip() for key in self.API_KEYS.split(",") if key.strip()]
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    def get_mongodb_uri(self) -> str:
        """
        Build MongoDB connection URI with authentication if credentials are provided.
        
        Returns:
            str: Complete MongoDB URI
        """
        # If MONGODB_URI is already a complete URI (starts with mongodb://), use it as-is
        if self.MONGODB_URI.startswith("mongodb://") or self.MONGODB_URI.startswith("mongodb+srv://"):
            # Check if it already contains credentials
            if "@" in self.MONGODB_URI:
                return self.MONGODB_URI
            
            # If username and password provided, inject them
            if self.MONGODB_USERNAME and self.MONGODB_PASSWORD:
                from urllib.parse import quote_plus
                username = quote_plus(self.MONGODB_USERNAME)
                password = quote_plus(self.MONGODB_PASSWORD)
                
                # Insert credentials after mongodb://
                protocol = "mongodb://"
                if self.MONGODB_URI.startswith("mongodb+srv://"):
                    protocol = "mongodb+srv://"
                
                uri_without_protocol = self.MONGODB_URI.replace(protocol, "")
                return f"{protocol}{username}:{password}@{uri_without_protocol}"
            
            return self.MONGODB_URI
        
        # Build URI from components
        if self.MONGODB_USERNAME and self.MONGODB_PASSWORD:
            from urllib.parse import quote_plus
            username = quote_plus(self.MONGODB_USERNAME)
            password = quote_plus(self.MONGODB_PASSWORD)
            return f"mongodb://{username}:{password}@{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DB_NAME}?authSource={self.MONGODB_AUTH_SOURCE}"
        else:
            return f"mongodb://{self.MONGODB_HOST}:{self.MONGODB_PORT}"


# Global settings instance
settings = Settings()
