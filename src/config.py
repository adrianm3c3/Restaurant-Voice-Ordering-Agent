import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def get_bool_env(name, default=False):
    value = os.getenv(name)

    if value is None:
        return default

    return value.lower() in {"1", "true", "yes", "y"}


CONFIG = {
    # =========================
    # API / models
    # =========================
    "api": {
        "base_url": os.getenv(
            "UTSA_BASE_URL",
            "http://149.165.173.247:8888/v1"
        ),

        "api_key": os.getenv(
            "UTSA_API_KEY",
            "EMPTY"
        ),
    },

    "model": {
        "agent": os.getenv(
            "UTSA_MODEL",
            "meta-llama/Llama-3.1-8B-Instruct"
        ),

        "parser": os.getenv(
            "PARSER_MODEL",
            "meta-llama/Llama-3.1-8B-Instruct"
        ),

        "embedding": os.getenv(
            "EMBED_MODEL",
            "all-MiniLM-L6-v2"
        ),
    },

    # =========================
    # Paths
    # =========================
    "paths": {
        "base_dir": str(BASE_DIR),

        "menu": os.getenv(
            "MENU_PATH",
            str(BASE_DIR / "data" / "menu" / "menu.json")
        ),

        "chroma_store": os.getenv(
            "CHROMA_STORE",
            str(BASE_DIR / "data" / "vector_store" / "chroma_db")
        ),

        "knowledge_chunks": os.getenv(
            "KNOWLEDGE_CHUNKS_PATH",
            str(BASE_DIR / "data" / "knowledge" / "knowledge_chunks.json")
        ),

        "logs": os.getenv(
            "LOG_DIR",
            str(BASE_DIR / "logs")
        ),
    },

    # =========================
    # Generation settings
    # =========================
    "generation": {
        "temperature": float(
            os.getenv("GEN_TEMPERATURE", "0.2")
        ),

        "max_tokens": int(
            os.getenv("GEN_MAX_TOKENS", "300")
        ),
    },

    "rag_generation": {
        "temperature": float(
            os.getenv("RAG_TEMP", "0.1")
        ),

        "max_tokens": int(
            os.getenv("RAG_MAX_TOKENS", "180")
        ),
    },

    "parser": {
        "temperature": float(
            os.getenv("PARSER_TEMPERATURE", "0.0")
        ),

        "max_tokens": int(
            os.getenv("PARSER_MAX_TOKENS", "250")
        ),
    },

    # =========================
    # Retrieval / embeddings
    # =========================
    "retrieval": {
        "top_k": int(
            os.getenv("RETRIEVAL_TOP_K", "8")
        ),

        "similarity_threshold": float(
            os.getenv("SIMILARITY_THRESHOLD", "0.30")
        ),

        "collection_name": os.getenv(
            "CHROMA_COLLECTION_NAME",
            "pizza_menu"
        ),

        "embedding_model": os.getenv(
            "EMBED_MODEL",
            "all-MiniLM-L6-v2"
        ),

        "chroma_distance_metric": os.getenv(
            "CHROMA_DISTANCE_METRIC",
            "cosine"
        ),

        "embedding_device": os.getenv(
            "EMBEDDING_DEVICE",
            "cpu"
        ),

        "normalize_embeddings": get_bool_env(
            "NORMALIZE_EMBEDDINGS",
            True
        ),
    },

    # =========================
    # Menu defaults
    # =========================
    "menu_defaults": {
        "default_crust": os.getenv(
            "DEFAULT_CRUST",
            "hand tossed"
        ),

        "default_pizza_size": os.getenv(
            "DEFAULT_PIZZA_SIZE",
            "medium"
        ),

        "default_pizza_base": os.getenv(
            "DEFAULT_PIZZA_BASE",
            "cheese"
        ),

        "pizza_sizes": [
            "small",
            "medium",
            "large",
        ],

        "default_wing_size": os.getenv(
            "DEFAULT_WING_SIZE",
            "6 piece"
        ),
    },

    # =========================
    # Tool settings
    # =========================
    "tools": {
        "enable_function_calling": get_bool_env(
            "ENABLE_FUNCTION_CALLING",
            True
        ),

        "strict_json": get_bool_env(
            "STRICT_JSON",
            True
        ),
    },

    # =========================
    # Pricing
    # =========================
    "pricing": {
        "tax_rate": float(
            os.getenv("TAX_RATE", "0.08")
        ),
    },

    # =========================
    # Restaurant metadata
    # =========================
    "restaurant": {
        "name": os.getenv(
            "RESTAURANT_NAME",
            "Paoli's Pizza Palace"
        ),
    },

    # =========================
    # Conversation settings
    # =========================
    "conversation": {
        "max_turns": int(
            os.getenv("MAX_TURNS", "20")
        ),

        "require_confirmation": get_bool_env(
            "REQUIRE_CONFIRMATION",
            True
        ),
    },

    # =========================
    # Voice settings
    # =========================
    "voice": {
        "sample_rate": int(
            os.getenv("VOICE_SAMPLE_RATE", "16000")
        ),

        "channels": int(
            os.getenv("VOICE_CHANNELS", "1")
        ),

        "tts_enabled": get_bool_env(
            "TTS_ENABLED",
            True
        ),

        "asr_enabled": get_bool_env(
            "ASR_ENABLED",
            True
        ),
    },

    # =========================
    # Logging
    # =========================
    "logging": {
        "level": os.getenv(
            "LOG_LEVEL",
            "INFO"
        ),

        "json_logs": get_bool_env(
            "JSON_LOGS",
            True
        ),

        "request_id": get_bool_env(
            "REQUEST_ID",
            True
        ),
    },

    # =========================
    # Runtime
    # =========================
    "runtime": {
        "environment": os.getenv(
            "ENV",
            "development"
        ),

        "debug": get_bool_env(
            "DEBUG",
            False
        ),
    },

    # =========================
    # Testing
    # =========================
    "testing": {
        "mock_llm": get_bool_env(
            "MOCK_LLM",
            False
        ),
    },

    # =========================
    # Debugging
    # =========================
    "debug": {
        "log_prompts": get_bool_env(
            "LOG_PROMPTS",
            False
        ),

        "log_responses": get_bool_env(
            "LOG_RESPONSES",
            False
        ),
    },
}