import unittest
from unittest.mock import MagicMock, patch
import logging
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from app.utils.google_api_helper import GoogleAPIChecker, KeyManager
from app.services.embedding_service import EmbeddingService
from google.api_core import exceptions as gexc
from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)

class TestRotation(unittest.TestCase):
  def test_status_extraction(self):
    self.assertEqual(GoogleAPIChecker.extract_status_code(gexc.ResourceExhausted("Quota")), 429)
    self.assertEqual(GoogleAPIChecker.extract_status_code(ValueError("Error")), None)

  def test_should_rotate(self):
    self.assertTrue(GoogleAPIChecker.should_rotate_key(429))
    self.assertTrue(GoogleAPIChecker.should_rotate_key(403))
    self.assertFalse(GoogleAPIChecker.should_rotate_key(500))

  def test_key_manager_load(self):
    with patch.dict('os.environ', {'GOOGLE_API_KEY_1': 'key1', 'GOOGLE_API_KEY_2': 'key2'}):
      km = KeyManager(settings)
      self.assertIsNotNone(km.get_current_key())

  def test_key_rotation(self):
    km = KeyManager(settings)
    km.keys = ['key_A', 'key_B'] # Force keys
    km.current_index = 0
    
    self.assertEqual(km.get_current_key(), 'key_A')
    km.rotate_key()
    self.assertEqual(km.get_current_key(), 'key_B')
    km.rotate_key()
    self.assertEqual(km.get_current_key(), 'key_A')

  @patch('google.genai.Client')
  def test_embedding_rotation_trigger(self, mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    
    mock_client.models.embed_content.side_effect = [
      gexc.ResourceExhausted("Quota exceeded"), # Call 1
      MagicMock(embeddings=[MagicMock(values=[0.1, 0.2])]) # Call 2 (Success after rotation hopefully)
    ]
    
    service = EmbeddingService()
    service.key_manager.keys = ['k1', 'k2']
    service.key_manager.current_index = 0
    
    result = service.embed_query("test")
    
    self.assertEqual(result, [0.1, 0.2])
    self.assertEqual(service.key_manager.current_index, 1)

if __name__ == '__main__':
  unittest.main()
