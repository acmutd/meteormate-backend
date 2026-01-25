# # Created by Ryan Polasky | 9/23/25
# # ACM MeteorMate | All Rights Reserved
#
# import os
# import logging
# from google import genai
#
# logger = logging.getLogger(__name__)
#
#
# class GeminiClient:
#     """A generic client to interact with the Google Gemini API."""
#
#     def __init__(self):
#         """
#         Initializes the Gemini client. Loads the API key and model name from environment variables.
#         """
#         self.api_key = os.getenv("GEMINI_API_KEY")
#         self.model_name = os.getenv("GEMINI_MODEL")
#
#         if not self.api_key:
#             logger.critical("GEMINI_API_KEY environment variable not found.")
#             raise ValueError("API key for Gemini is not configured.")
#
#         try:
#             self.client = genai.Client()
#             logger.info(f"GeminiClient initialized successfully, model set to '{self.model_name}'.")
#         except Exception as e:
#             logger.critical(f"Failed to initialize the GoogleGenerativeAI model: {e}")
#             raise
#
#     def generate_response(self, prompt: str) -> str:
#         """
#         Sends a prompt to the Gemini API and returns the text response.
#         :param prompt: The prompt to be sent to the LLM as a string.
#         :return: A string containing the response text.
#         """
#         if not prompt or not isinstance(prompt, str):
#             logger.warning("generate_response called with an invalid or empty prompt.")
#             return ""
#
#         try:
#             logger.debug("Invoking Gemini model.")
#             response = self.client.models.generate_content(
#                 model=self.model_name,
#                 contents=prompt,
#                 # don't need API key passed in, just needs to be the env var
#             )
#             return str(response.text) if hasattr(response, 'text') else str(response)
#         except Exception as e:
#             logger.error(f"An error occurred while communicating with the Gemini API: {e}")
#             raise
