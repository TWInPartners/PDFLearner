import pdfplumber
import io
import streamlit as st
import pytesseract
from PIL import Image
import cv2
import numpy as np
from pdf2image import convert_from_bytes
import re

class PDFProcessor:
    def __init__(self, enable_ocr=True):
        self.enable_ocr = enable_ocr
    
    def extract_text(self, uploaded_file):
        """
        Extract text from uploaded PDF file including OCR for images and figures
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            str: Extracted text from PDF including text from images
        """
        try:
            # Create a BytesIO object from the uploaded file
            pdf_bytes = io.BytesIO(uploaded_file.getvalue())
            
            text_content = ""
            ocr_text = ""
            
            # Use pdfplumber to extract regular text
            with pdfplumber.open(pdf_bytes) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += f"\n--- Page {page_num + 1} ---\n"
                            text_content += page_text
                            text_content += "\n"
                    except Exception as e:
                        st.warning(f"Could not extract text from page {page_num + 1}: {str(e)}")
                        continue
            
            # Reset BytesIO position for image extraction
            pdf_bytes.seek(0)
            
            # Extract text from images using OCR (if enabled)
            if self.enable_ocr:
                try:
                    with st.spinner("🔍 Scanning images for text..."):
                        ocr_text = self.extract_text_from_images(pdf_bytes)
                        if ocr_text and ocr_text.strip():
                            text_content += "\n--- Text from Images and Figures ---\n"
                            text_content += ocr_text
                            st.success("✓ Successfully extracted text from images!")
                        else:
                            st.info("ℹ️ No readable text found in images")
                except Exception as e:
                    st.warning(f"OCR processing skipped: {str(e)}")
                    # Continue without OCR rather than crashing
            
            if not text_content.strip():
                raise ValueError("No text could be extracted from the PDF")
            
            return self.clean_text(text_content)
            
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    
    def clean_text(self, text):
        """
        Clean and preprocess extracted text
        
        Args:
            text (str): Raw extracted text
            
        Returns:
            str: Cleaned text
        """
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip empty lines and page markers
            line = line.strip()
            if line and not line.startswith('--- Page'):
                cleaned_lines.append(line)
        
        # Join lines and normalize spacing
        cleaned_text = ' '.join(cleaned_lines)
        
        # Remove extra spaces
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        return cleaned_text.strip()
    
    def extract_text_from_images(self, pdf_bytes):
        """
        Extract text from images and figures in PDF using OCR
        
        Args:
            pdf_bytes: BytesIO object containing PDF data
            
        Returns:
            str: Extracted text from images
        """
        ocr_text = ""
        
        try:
            # Convert PDF pages to images (limit to first 5 pages for performance)
            images = convert_from_bytes(pdf_bytes.getvalue(), dpi=200, fmt='PNG', first_page=1, last_page=5)
            
            for page_num, image in enumerate(images):
                try:
                    # Resize image if too large (for performance)
                    width, height = image.size
                    if width > 2000 or height > 2000:
                        image = image.resize((min(2000, width), min(2000, height)), Image.Resampling.LANCZOS)
                    
                    # Convert PIL image to OpenCV format for preprocessing
                    open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                    
                    # Preprocess image for better OCR results
                    processed_image = self.preprocess_image_for_ocr(open_cv_image)
                    
                    # Extract text using Tesseract OCR with simplified config
                    page_ocr_text = pytesseract.image_to_string(
                        processed_image,
                        config='--psm 6'
                    )
                    
                    if page_ocr_text and page_ocr_text.strip():
                        ocr_text += f"\n--- OCR Page {page_num + 1} ---\n"
                        ocr_text += page_ocr_text.strip()
                        ocr_text += "\n"
                        
                except Exception as e:
                    # Silently continue on individual page failures
                    continue
                    
        except Exception as e:
            # Silently fail OCR without breaking the main process
            pass
            
        return ocr_text
    
    def preprocess_image_for_ocr(self, image):
        """
        Preprocess image to improve OCR accuracy
        
        Args:
            image: OpenCV image array
            
        Returns:
            Preprocessed image for OCR
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Apply adaptive thresholding for better text contrast
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Apply morphological operations to clean up the image
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        processed = cv2.morphologyEx(processed, cv2.MORPH_OPEN, kernel)
        
        return processed
    
    def get_text_stats(self, text):
        """
        Get basic statistics about the extracted text
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Text statistics
        """
        words = text.split()
        sentences = text.split('.')
        
        return {
            'character_count': len(text),
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'average_words_per_sentence': len(words) / max(len([s for s in sentences if s.strip()]), 1)
        }
