"""
config.py — Central configuration for Labour Law AI Platform
============================================================
Powered by Anthropic Claude APIs.

Loads settings from .env (or environment variables).
Import this module anywhere in the project:

    from config import settings, PATHS

All paths use pathlib.Path so they work on Windows, Linux, and macOS.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

# ── Load .env before anything else ──────────────────────────────────────────
load_dotenv()


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  1. ROOT PATH — everything is relative to this                          ║
# ╚══════════════════════════════════════════════════════════════════════════╝

ROOT_DIR: Path = Path(__file__).resolve().parent


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  2. FOLDER PATHS                                                        ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class Paths:
    """All project directories as pathlib.Path objects.

    Usage:
        from config import PATHS
        pdf_dir = PATHS.acts
    """
    root       : Path = ROOT_DIR
    acts       : Path = ROOT_DIR / "acts"
    rules      : Path = ROOT_DIR / "rules"
    judgments  : Path = ROOT_DIR / "judgments"
    circulars  : Path = ROOT_DIR / "circulars"
    forms      : Path = ROOT_DIR / "forms"
    database   : Path = ROOT_DIR / "database"
    embeddings : Path = ROOT_DIR / "embeddings"
    summaries  : Path = ROOT_DIR / "summaries"
    quiz       : Path = ROOT_DIR / "quiz"
    faq        : Path = ROOT_DIR / "faq"
    logs       : Path = ROOT_DIR / "logs"

    def create_all(self) -> None:
        """Create every directory if it doesn't exist."""
        for attr, value in self.__class__.__dict__.items():
            if isinstance(value, Path):
                value.mkdir(parents=True, exist_ok=True)

PATHS = Paths()


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  3. SETTINGS MODEL (reads from .env automatically)                      ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class Settings(BaseSettings):
    """
    All settings come from environment variables or .env file.
    Pydantic validates types and raises clear errors on bad values.
    """

    # ── App metadata ────────────────────────────────────────────────────
    app_name   : str  = Field("Labour Law AI", env="APP_NAME")
    app_version: str  = Field("1.0.0",         env="APP_VERSION")
    debug      : bool = Field(False,            env="DEBUG")

    # ── Anthropic API ────────────────────────────────────────────────────
    # Get your key at: https://console.anthropic.com
    anthropic_api_key : str = Field("", env="ANTHROPIC_API_KEY")

    # ── Claude model selection ───────────────────────────────────────────
    # Available models (as of 2025):
    #   claude-haiku-4-5-20251001      ← fastest, cheapest — good for quiz MCQ gen
    #   claude-sonnet-4-6              ← balanced speed/quality — recommended default
    #   claude-opus-4-6                ← most capable — use for complex legal reasoning
    claude_model      : str   = Field("claude-sonnet-4-6", env="CLAUDE_MODEL")
    claude_temperature: float = Field(0.2,                  env="CLAUDE_TEMPERATURE")
    claude_max_tokens : int   = Field(2048,                 env="CLAUDE_MAX_TOKENS")

    # Model aliases for different tasks — override in .env if needed
    # Using Haiku for fast bulk tasks (quiz generation, summarisation)
    # and Sonnet/Opus for legal Q&A where accuracy matters most
    claude_model_fast  : str = Field("claude-haiku-4-5-20251001", env="CLAUDE_MODEL_FAST")
    claude_model_smart : str = Field("claude-opus-4-6",            env="CLAUDE_MODEL_SMART")

    # ── Embedding settings ──────────────────────────────────────────────
    # Anthropic does not offer an embeddings API.
    # sentence-transformers is the recommended offline pairing for RAG.
    embedding_model : str = Field(
        "all-MiniLM-L6-v2",  # ~80 MB, runs fully offline, no API key needed
        env="EMBEDDING_MODEL"
    )
    chunk_size      : int = Field(500, env="CHUNK_SIZE")
    chunk_overlap   : int = Field(50,  env="CHUNK_OVERLAP")
    top_k_results   : int = Field(5,   env="TOP_K_RESULTS")

    # ── OCR settings ────────────────────────────────────────────────────
    tesseract_cmd : str = Field(
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        env="TESSERACT_CMD"
    )
    ocr_language  : str = Field("eng", env="OCR_LANGUAGE")  # e.g. "eng+hin"
    ocr_dpi       : int = Field(300,   env="OCR_DPI")

    # Claude Vision fallback — send page image to Claude when Tesseract fails
    use_claude_vision_ocr : bool = Field(False, env="USE_CLAUDE_VISION_OCR")
    # When True, pages that Tesseract can't parse are sent to claude-haiku-4-5-20251001
    # as base64 images. Costs API tokens but handles complex layouts well.

    # ── Database ─────────────────────────────────────────────────────────
    db_path : str = Field(
        str(ROOT_DIR / "database" / "labour_law.db"),
        env="DB_PATH"
    )

    @property
    def db_url(self) -> str:
        """SQLAlchemy connection string."""
        return f"sqlite:///{self.db_path}"

    # ── FastAPI server ────────────────────────────────────────────────────
    api_host : str = Field("127.0.0.1", env="API_HOST")
    api_port : int = Field(8000,        env="API_PORT")

    # ── Streamlit ─────────────────────────────────────────────────────────
    streamlit_port : int = Field(8501, env="STREAMLIT_PORT")

    # ── Logging ──────────────────────────────────────────────────────────
    log_level : str = Field("INFO", env="LOG_LEVEL")
    log_file  : str = Field(
        str(ROOT_DIR / "logs" / "app.log"),
        env="LOG_FILE"
    )

    # ── Validators ───────────────────────────────────────────────────────
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v = v.upper()
        if v not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v

    @field_validator("claude_temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("claude_temperature must be between 0.0 and 1.0")
        return v

    @field_validator("claude_model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        known = {
            "claude-haiku-4-5-20251001",
            "claude-sonnet-4-6",
            "claude-opus-4-6",
        }
        if v not in known:
            # Allow unknown model strings (future models) — just warn, don't crash
            import warnings
            warnings.warn(
                f"CLAUDE_MODEL='{v}' is not in the known model list. "
                f"Known: {known}. Proceeding anyway.",
                UserWarning,
                stacklevel=2,
            )
        return v

    class Config:
        env_file          = ".env"
        env_file_encoding = "utf-8"
        case_sensitive    = False  # ANTHROPIC_API_KEY and anthropic_api_key both work


# Singleton — import this everywhere
settings = Settings()


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  4. ANTHROPIC CLIENT FACTORY                                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def get_anthropic_client():
    """
    Return a configured Anthropic client.
    Use this instead of constructing anthropic.Anthropic() manually.

    Usage:
        from config import get_anthropic_client
        client = get_anthropic_client()
        response = client.messages.create(
            model=settings.claude_model,
            max_tokens=settings.claude_max_tokens,
            messages=[{"role": "user", "content": "Explain Section 25 of the ID Act"}]
        )
        print(response.content[0].text)
    """
    import anthropic

    if not settings.anthropic_api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY is not set. "
            "Add it to your .env file or set it as an environment variable. "
            "Get a key at: https://console.anthropic.com"
        )

    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def get_langchain_llm(model: str | None = None, temperature: float | None = None):
    """
    Return a LangChain-compatible ChatAnthropic object.
    Drop-in for use in LangChain chains, agents, and retrievers.

    Usage:
        from config import get_langchain_llm
        llm = get_langchain_llm()
        # or use a faster model for bulk tasks:
        llm_fast = get_langchain_llm(model=settings.claude_model_fast)
    """
    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(
        model=model or settings.claude_model,
        temperature=temperature if temperature is not None else settings.claude_temperature,
        max_tokens=settings.claude_max_tokens,
        anthropic_api_key=settings.anthropic_api_key,
    )


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  5. LOGGING SETUP                                                       ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def setup_logging() -> None:
    """
    Configure loguru to write to both terminal and a rotating log file.
    Call once at application startup (e.g. in main.py or app.py).
    """
    try:
        from loguru import logger

        logger.remove()

        logger.add(
            sys.stderr,
            level=settings.log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{line}</cyan> — "
                   "<level>{message}</level>",
            colorize=True,
        )

        PATHS.logs.mkdir(parents=True, exist_ok=True)
        logger.add(
            settings.log_file,
            level=settings.log_level,
            rotation="10 MB",
            retention=7,
            compression="zip",
            encoding="utf-8",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{line} — {message}",
        )

        logger.info(f"{settings.app_name} v{settings.app_version} — logging ready")
        logger.info(f"Claude model: {settings.claude_model}")

    except ImportError:
        logging.basicConfig(
            level=getattr(logging, settings.log_level, logging.INFO),
            format="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d — %(message)s",
        )


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  6. FOLDER BOOTSTRAP                                                    ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def bootstrap_folders() -> None:
    """Create all required directories on first run (safe to call every time)."""
    folders = [
        PATHS.acts, PATHS.rules, PATHS.judgments, PATHS.circulars,
        PATHS.forms, PATHS.database, PATHS.embeddings, PATHS.summaries,
        PATHS.quiz, PATHS.faq, PATHS.logs,
    ]
    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)


bootstrap_folders()
