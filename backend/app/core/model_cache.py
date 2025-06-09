import logging
from transformers import pipeline
from app.config.settings import get_settings

logger = logging.getLogger(__name__)

def precache_models():
    """Pre-cache AI models at server startup."""
    settings = get_settings()
    logger.info("Pre-caching AI models...")

    # Summarization model
    try:
        pipeline("summarization", model=settings.AI_MODEL_NAME)
        logger.info(f"Cached summarization model: {settings.AI_MODEL_NAME}")
    except Exception as e:
        logger.error(f"Failed to cache summarization model: {e}")

    # Question Answering model
    try:
        pipeline("question-answering", model=settings.AI_QA_MODEL)
        logger.info(f"Cached QA model: {settings.AI_QA_MODEL}")
    except Exception as e:
        logger.error(f"Failed to cache QA model: {e}")

    # Keywords/Feature Extraction model
    try:
        pipeline("feature-extraction", model=settings.AI_KEYWORDS_MODEL)
        logger.info(f"Cached keywords model: {settings.AI_KEYWORDS_MODEL}")
    except Exception as e:
        logger.error(f"Failed to cache keywords model: {e}")

    logger.info("Model pre-caching completed.") 