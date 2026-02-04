import os
import random
from typing import Optional, List
from google.api_core import exceptions as gexc
from app.core.logging import setup_logging

logger = setup_logging()

class GoogleAPIChecker:
  @staticmethod
  def extract_status_code(error: Exception) -> Optional[int]:
    """
    Extract HTTP-like status code from Google API exception.
    """
    if isinstance(error, gexc.ResourceExhausted):
      return 429
    if isinstance(error, gexc.PermissionDenied):
      return 403
    if isinstance(error, gexc.Unauthorized):
      return 401
    if isinstance(error, gexc.InvalidArgument):
      return 400
    if isinstance(error, gexc.NotFound):
      return 404
    if isinstance(error, gexc.InternalServerError):
      return 500
    if isinstance(error, gexc.ServiceUnavailable):
      return 503
    if isinstance(error, gexc.DeadlineExceeded):
      return 504
    return None

  @staticmethod
  def should_rotate_key(status_code: int) -> bool:
    """
    Only rotate key if the error relates to key exhaustion or quota exhaustion.
    """
    return status_code in {403, 429}

class KeyManager:
  def __init__(self, settings, explicit_keys: List[str] = None):
    if explicit_keys:
      self.keys = explicit_keys
    else:
      self.keys = self._load_keys(settings)
    self.current_index = 0
    if not self.keys:
      logger.warning("No GOOGLE_API_KEYS found. Embedding service may fail.")
    else:
      logger.info(f"Loaded {len(self.keys)} Google API keys.")

  def _load_keys(self, settings) -> List[str]:
    """
    Load keys from settings. 
    Checks for settings.GOOGLE_API_KEYS (list) first, 
    then fallbacks to environment variables pattern GOOGLE_API_KEY_1, _2...
    and finally the single settings.GOOGLE_API_KEY.
    """
    keys = []
    
    # 1. Try explicit list in settings if it existed (it doesn't yet, but good for future)
    if hasattr(settings, 'GOOGLE_API_KEYS') and settings.GOOGLE_API_KEYS:
      if isinstance(settings.GOOGLE_API_KEYS, list):
        return settings.GOOGLE_API_KEYS
      elif isinstance(settings.GOOGLE_API_KEYS, str):
        return [k.strip() for k in settings.GOOGLE_API_KEYS.split(',') if k.strip()]

    # 2. Try pattern matching from environment
    import os
    for key, value in os.environ.items():
      if key.startswith("GOOGLE_API_KEY_") and key[15:].isdigit():
        if value:
          keys.append(value)
    
    # 3. Fallback to the single main key
    if settings.GOOGLE_API_KEY and settings.GOOGLE_API_KEY not in keys:
      keys.insert(0, settings.GOOGLE_API_KEY)

    return keys

  def get_current_key(self) -> Optional[str]:
    if not self.keys:
      return None
    return self.keys[self.current_index]

  def rotate_key(self) -> Optional[str]:
    if not self.keys or len(self.keys) <= 1:
      logger.warning("Key rotation requested but no other keys available.")
      return self.get_current_key()
    
    self.current_index = (self.current_index + 1) % len(self.keys)
    logger.info(f"Rotated to API Key index {self.current_index}")
    return self.get_current_key()
