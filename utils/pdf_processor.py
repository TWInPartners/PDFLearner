import pdfplumber
import io
import streamlit as st
import pytesseract
from PIL import Image
import cv2
import numpy as np
from pdf2image import convert_from_bytes
import re
import gc
import logging
from typing import List, Dict, Any
from .error_handler import ErrorHandler

class PDFProcessor:
    def __init__(self, enable_ocr=True, max_pages_for_ocr=20):
        self.enable_ocr = enable_ocr
        self.max_pages_for_ocr = max_pages_for_ocr  # Limit OCR pages for large files
        self.logger = logging.getLogger(__name__)
    
    def extract_text(self, uploaded_file):
        """
        Extract text from uploaded PDF file including OCR for images and figures
        Enhanced for large file handling with memory management
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            str: Extracted text from PDF including text from images
        """
        try:
            # Get file size for processing decisions
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
            
            # Show processing info for large files
            if file_size > 50:
                st.info(f"📄 Processing large PDF ({file_size:.1f} MB). This may take a few moments, but we'll optimize it for better performance.")
            
            # Create a BytesIO object from the uploaded file
            pdf_bytes = io.BytesIO(uploaded_file.getvalue())
            
            text_content = ""
            ocr_text = ""
            total_pages = 0
            
            # Use pdfplumber to extract regular text with memory optimization
            with pdfplumber.open(pdf_bytes) as pdf:
                total_pages = len(pdf.pages)
                
                # For very large files, process in batches
                batch_size = 10 if file_size > 100 else 20
                
                for i in range(0, total_pages, batch_size):
                    batch_end = min(i + batch_size, total_pages)
                    
                    # Update progress for large files
                    if file_size > 50:
                        progress = (i / total_pages) * 0.7  # Reserve 30% for OCR
                        st.progress(progress, f"Processing pages {i+1}-{batch_end} of {total_pages}")
                    
                    # Process batch
                    for page_num in range(i, batch_end):
                        try:
                            page = pdf.pages[page_num]
                            page_text = page.extract_text()
                            if page_text:
                                text_content += f"\n--- Page {page_num + 1} ---\n"
                                text_content += page_text
                                text_content += "\n"
                        except Exception as e:
                            self.logger.warning(f"Could not extract text from page {page_num + 1}: {str(e)}")
                            continue
                    
                    # Force garbage collection for large files
                    if file_size > 100:
                        gc.collect()
            
            # Clear progress bar for large files
            if file_size > 50:
                st.progress(1.0, "Text extraction complete!")
            
            # Extract text from images using OCR (if enabled)
            if self.enable_ocr:
                try:
                    # Reset BytesIO position for image extraction
                    pdf_bytes.seek(0)
                    
                    ocr_text = self.extract_text_from_images(pdf_bytes, file_size)
                    if ocr_text and ocr_text.strip():
                        text_content += "\n--- Text from Images and Figures ---\n"
                        text_content += ocr_text
                        st.success("✅ Successfully extracted text from images!")
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
    
    def extract_text_from_images(self, pdf_bytes, file_size_mb: float = 0):
        """
        Extract text from images and figures in PDF using OCR
        Enhanced for large file handling with intelligent limits
        
        Args:
            pdf_bytes: BytesIO object containing PDF data
            file_size_mb: File size in MB for processing decisions
            
        Returns:
            str: Extracted text from images
        """
        ocr_text = ""
        
        try:
            # Determine OCR page limit based on file size
            if file_size_mb > 150:
                max_pages = 5  # Very large files - minimal OCR
                dpi = 120
            elif file_size_mb > 100:
                max_pages = 10
                dpi = 150
            elif file_size_mb > 50:
                max_pages = 15
                dpi = 180
            else:
                max_pages = 20  # Default for smaller files
                dpi = 200
            
            st.info(f"🔍 **OCR Processing:** Scanning {max_pages} pages for images and figures...")
            
            # Convert PDF pages to images with intelligent limits
            images = convert_from_bytes(
                pdf_bytes.getvalue(), 
                dpi=dpi, 
                fmt='PNG', 
                first_page=1, 
                last_page=max_pages
            )
            
            for page_num, image in enumerate(images):
                try:
                    # Update OCR progress for large files
                    if file_size_mb > 50:
                        ocr_progress = 0.7 + (page_num / len(images)) * 0.3
                        st.progress(ocr_progress, f"OCR processing page {page_num + 1} of {len(images)}")
                    
                    # More aggressive resizing for large files
                    width, height = image.size
                    if file_size_mb > 100:
                        max_dimension = 1500
                    elif file_size_mb > 50:
                        max_dimension = 1800
                    else:
                        max_dimension = 2000
                    
                    if width > max_dimension or height > max_dimension:
                        ratio = min(max_dimension/width, max_dimension/height)
                        new_size = (int(width * ratio), int(height * ratio))
                        image = image.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # Convert PIL image to OpenCV format for preprocessing
                    open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                    
                    # Preprocess image for better OCR results
                    processed_image = self.preprocess_image_for_ocr(open_cv_image)
                    
                    # Extract text using Tesseract OCR with optimized config
                    page_ocr_text = pytesseract.image_to_string(
                        processed_image,
                        config='--psm 6 --oem 3'
                    )
                    
                    if page_ocr_text and page_ocr_text.strip():
                        ocr_text += f"\n--- OCR Page {page_num + 1} ---\n"
                        ocr_text += page_ocr_text.strip()
                        ocr_text += "\n"
                    
                    # Memory cleanup for large files
                    if file_size_mb > 100:
                        del open_cv_image, processed_image, image
                        gc.collect()
                        
                except Exception as e:
                    # Silently continue on individual page failures
                    self.logger.warning(f"OCR failed for page {page_num + 1}: {str(e)}")
                    continue
            
            # Clear progress for large files
            if file_size_mb > 50:
                st.progress(1.0, "OCR processing complete!")
                    
        except Exception as e:
            # Silently fail OCR without breaking the main process
            self.logger.warning(f"OCR processing failed: {str(e)}")
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
