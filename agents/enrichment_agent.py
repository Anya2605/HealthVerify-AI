"""
Agent 2: Enrichment Agent
Enriches provider data using OCR and document extraction
"""
from typing import Dict, Any
from utils.file_processor import FileProcessor


class EnrichmentAgent:
    """Agent for data enrichment and OCR processing.

    External LLM-based services (Gemini) are imported lazily to avoid
    heavy dependencies at app startup. If Gemini/LLM services are not
    available or configured, enrichment will still attempt OCR-based
    extraction using the internal FileProcessor.
    """

    def __init__(self):
        # Lazy-initialize heavy services only when needed
        self._gemini = None

        self.file_processor = FileProcessor()

    def enrich_from_document(self, document_path: str, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich provider data from a document using OCR and optional LLM extraction."""
        try:
            # Use the FileProcessor to extract text (it will use remote OCR if configured)
            df, metadata = self.file_processor.process_file(document_path)

            # Prefer a text column if present
            text = None
            if 'ocr_text' in df.columns:
                text = df['ocr_text'].iloc[0]
            else:
                # Join textual columns as fallback
                text = '\n'.join(df.astype(str).apply(lambda row: ' | '.join(row.values), axis=1).tolist())

            extracted_data = {}

            # If Gemini is available, try to extract structured fields via LLM
            if not self._gemini:
                # Attempt to import and initialize Gemini lazily (only here)
                try:
                    from services.gemini_service import GeminiService
                    self._gemini = GeminiService()
                except Exception:
                    self._gemini = None

            if self._gemini:
                try:
                    extraction_result = self._gemini.extract_provider_info_from_document(text)
                    if extraction_result.get('success'):
                        extracted_data = extraction_result.get('extracted_data', {})
                except Exception:
                    # Fall back to no LLM extraction
                    extracted_data = {}

            enriched_data = {**provider_data, **extracted_data}
            return {
                'success': True,
                'enriched_data': enriched_data,
                'extracted_fields': list(extracted_data.keys())
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'enriched_data': provider_data
            }

