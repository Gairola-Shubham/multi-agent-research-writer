import os
import tempfile
from backend.core.config import settings
from backend.core.logger import logger


def run_startup_checks():
    logger.info("Initializing startup checks...")
    
    # 1. Configuration loaded log
    logger.info(
        f"Configuration loaded - Host: {settings.BACKEND_HOST}, Port: {settings.BACKEND_PORT}, "
        f"Model: {settings.LLM_MODEL}, Chroma DB Path: {settings.CHROMA_DB_PATH}"
    )
    
    # 2. Check ChromaDB directory existence & writability
    try:
        os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
        # Test write permission by writing a temp file
        temp_file = os.path.join(settings.CHROMA_DB_PATH, ".startup_write_test")
        with open(temp_file, "w") as f:
            f.write("test")
        os.remove(temp_file)
        logger.info(f"ChromaDB status - directory '{settings.CHROMA_DB_PATH}' is verified and writable.")
    except Exception as e:
        logger.critical(f"ChromaDB status - directory '{settings.CHROMA_DB_PATH}' is NOT writable: {e}")
        # Stop application if critical ChromaDB path is unusable
        raise RuntimeError(f"Critical ChromaDB path is not writable: {e}")

    # 3. Verify writable export directory (system temp directory)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            test_file = os.path.join(tmp, "test.txt")
            with open(test_file, "w") as f:
                f.write("test")
        logger.info("Export status - System temporary directory is verified and writable.")
    except Exception as e:
        logger.critical(f"Export status - System temporary directory is NOT writable: {e}")
        raise RuntimeError(f"System temp directory is not writable: {e}")

    # 4. Check Ollama status
    from backend.services.ai_service import ai_service
    logger.info("Checking Ollama status...")
    try:
        is_connected = ai_service.client.check_connection()
        if is_connected:
            logger.info("Ollama status - connected successfully.")
            model_exists = ai_service.client.has_model(settings.LLM_MODEL)
            if model_exists:
                logger.info(f"Ollama status - configured model '{settings.LLM_MODEL}' exists and is ready.")
            else:
                logger.warning(f"Ollama status - configured model '{settings.LLM_MODEL}' was not found on the Ollama server.")
        else:
            logger.warning(f"Ollama status - server at {settings.OLLAMA_BASE_URL} is unreachable.")
    except Exception as e:
        logger.warning(f"Ollama status - check encountered an error: {e}")

    logger.info("Startup checks completed.")
