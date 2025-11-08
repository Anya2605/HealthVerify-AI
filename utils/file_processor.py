"""
File processing utilities with remote OCR support using OCR.space API.

This module prefers using a configured OCR API key (OCR.space) so the
environment does not need local Tesseract/OCR installations. If no API key
is provided and local OCR libraries are missing, the processor will raise
an informative error.
"""
import os
import time
import json
import logging
from typing import Tuple, Dict

import pandas as pd
import requests

from config import Config


LOGGER = logging.getLogger(__name__)


class FileProcessor:
    """Enhanced file processor that supports remote OCR via OCR.space.

    Methods:
      - is_supported_format(filename)
      - process_file(file_path) -> (DataFrame, metadata)
    """

    SUPPORTED_FORMATS = {
        'csv': ['csv'],
        'excel': ['xlsx', 'xls'],
        'pdf': ['pdf'],
        'image': ['jpg', 'jpeg', 'png', 'tiff'],
        'json': ['json']
    }

    OCRSPACE_ENDPOINT = 'https://api.ocr.space/parse/image'

    def __init__(self):
        self.start_time = None

    @staticmethod
    def get_file_extension(filename: str) -> str:
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

    def is_supported_format(self, filename: str) -> bool:
        ext = self.get_file_extension(filename)
        return any(ext in exts for exts in self.SUPPORTED_FORMATS.values())

    def start_timer(self):
        self.start_time = time.time()

    def get_elapsed_time(self) -> float:
        if not self.start_time:
            return 0.0
        return time.time() - self.start_time

    def process_file(self, file_path: str) -> Tuple[pd.DataFrame, Dict]:
        """Detect file type, extract structured data and return DataFrame + metadata.

        For PDFs and images, prefers remote OCR (OCR.space) when
        `Config.OCRSPACE_API_KEY` is set. Otherwise, will attempt a local
        extraction if supported libraries are installed.
        """
        self.start_timer()

        ext = self.get_file_extension(file_path)
        df = pd.DataFrame()
        format_type = ext

        try:
            if ext in self.SUPPORTED_FORMATS['csv']:
                df = pd.read_csv(file_path, encoding='utf-8')
            elif ext in self.SUPPORTED_FORMATS['excel']:
                df = pd.read_excel(file_path)
            elif ext in self.SUPPORTED_FORMATS['json']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                df = pd.json_normalize(data)
            elif ext in self.SUPPORTED_FORMATS['pdf']:
                # Prefer remote OCR for PDFs
                if Config.OCRSPACE_API_KEY:
                    text = self._remote_ocr(file_path)
                    df = self._text_to_dataframe(text)
                else:
                    # Try extracting text directly from PDF (may work for born-digital PDFs)
                    try:
                        from PyPDF2 import PdfReader
                        reader = PdfReader(file_path)
                        text = "\n".join([p.extract_text() or '' for p in reader.pages])
                        if text.strip():
                            df = self._text_to_dataframe(text)
                        else:
                            raise RuntimeError('No text found in PDF and no OCR API key configured')
                    except Exception as e:
                        raise RuntimeError('PDF processing requires OCR API key or local PyPDF2/pdf2image installed') from e
            elif ext in self.SUPPORTED_FORMATS['image']:
                if Config.OCRSPACE_API_KEY:
                    text = self._remote_ocr(file_path)
                    df = self._text_to_dataframe(text)
                else:
                    raise RuntimeError('Image OCR requires OCR API key (no local OCR configured)')
            else:
                raise ValueError(f'Unsupported file format: {ext}')

            # Standardize columns where possible
            df = self._standardize_columns(df)

            processing_time = self.get_elapsed_time()
            metadata = {
                'format': format_type,
                'processing_time': processing_time,
                'rows_processed': len(df),
                'columns_found': list(df.columns),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }

            return df, metadata

        except Exception as e:
            LOGGER.exception('Error processing file')
            raise

    def _remote_ocr(self, file_path: str) -> str:
        """Send file to OCR.space API and return extracted text.

        Expects `Config.OCRSPACE_API_KEY` to be set.
        """
        api_key = Config.OCRSPACE_API_KEY
        if not api_key:
            raise RuntimeError('OCR API key not configured (OCRSPACE_API_KEY)')

        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'apikey': api_key,
                'language': 'eng',
                'isOverlayRequired': False
            }
            resp = requests.post(self.OCRSPACE_ENDPOINT, files=files, data=data, timeout=60)
            resp.raise_for_status()
            result = resp.json()

        # OCR.space returns ParsedResults list
        if 'ParsedResults' in result and result['ParsedResults']:
            texts = [p.get('ParsedText', '') for p in result['ParsedResults']]
            return '\n'.join(texts)

        # If API returns error
        error_message = result.get('ErrorMessage') or result.get('ErrorDetails') or 'Unknown OCR error'
        raise RuntimeError(f'OCR API error: {error_message}')

    def _text_to_dataframe(self, text: str) -> pd.DataFrame:
        """Try to parse simple key:value style text into a DataFrame.

        This is a best-effort conversion for semi-structured text extracted
        from OCR. The resulting DataFrame will have one row when parsing
        key:value pairs, or multiple rows if repetitive structures are found.
        """
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        data = {}
        current_key = None

        for line in lines:
            if ':' in line:
                key, val = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                val = val.strip()
                data.setdefault(key, []).append(val)
                current_key = key
            elif current_key:
                # Append additional text to last key
                data[current_key][-1] = data[current_key][-1] + ' ' + line

        # Normalize lengths: make each key have same number of rows
        max_len = max((len(v) for v in data.values()), default=0)
        for k, v in list(data.items()):
            if len(v) < max_len:
                data[k] = v + [''] * (max_len - len(v))

        if not data:
            # Fallback: return a single-row DataFrame with the raw text
            return pd.DataFrame({'ocr_text': [text]})

        return pd.DataFrame(data)

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        # Normalize column names and map common variants
        mapping = {
            'name': 'full_name',
            'provider_name': 'full_name',
            'doctor_name': 'full_name',
            'address': 'practice_address',
            'phone_number': 'phone',
            'telephone': 'phone',
            'zip': 'pin_code',
            'zipcode': 'pin_code',
            'postal_code': 'pin_code',
            'specialization': 'specialty',
            'doctor_id': 'provider_id',
            'id': 'provider_id'
        }

        df.columns = [str(c).lower().strip().replace(' ', '_') for c in df.columns]
        df = df.rename(columns=mapping)
        return df

