"""
Service modules for external API integrations.

Note: avoid importing heavy third-party libraries at package import time.
Submodules should be imported lazily by the code that needs them to
prevent import-time side effects during app startup.
"""

__all__ = [
    'NPIService',
    'LocationService',
    'PhoneService',
    'GeminiService',
    'HuggingFaceService',
    'WebScraper',
    'MLModels'
]

