import pdfplumber
import io
import streamlit as st

class PDFProcessor:
    def __init__(self):
        pass
    
    def extract_text(self, uploaded_file):
        """
        Extract text from uploaded PDF file
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            str: Extracted text from PDF
        """
        try:
            # Create a BytesIO object from the uploaded file
            pdf_bytes = io.BytesIO(uploaded_file.getvalue())
            
            text_content = ""
            
            # Use pdfplumber to extract text
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
        import re
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        return cleaned_text.strip()
    
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
