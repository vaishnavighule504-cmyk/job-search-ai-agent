import PyPDF2
import streamlit as st

def extract_text_from_pdf(pdf_file):
    """
    Extracts all text from an uploaded PDF file stream.
    Validates that the PDF is not empty, corrupted, or unreadable.

    Args:
        pdf_file: A file-like object representing the uploaded PDF.

    Returns:
        str: The full text extracted from the PDF, or a clean user-facing error message.
    """
    text = ""
    try:
        # Validate that the file is not completely empty
        pdf_file.seek(0, 2)  # Seek to end
        file_size = pdf_file.tell()
        pdf_file.seek(0)  # Reset pointer
        
        if file_size == 0:
            return "Error: The uploaded PDF is empty. Please upload a valid PDF resume."

        # Initialize reader
        reader = PyPDF2.PdfReader(pdf_file)
        
        # Check if the PDF has pages
        if len(reader.pages) == 0:
            return "Error: The PDF has no pages. Please upload a valid PDF resume."

        # Extract text page by page
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            except Exception as page_err:
                # Log page read error gracefully, continue to other pages
                pass
                
        cleaned_text = text.strip()
        if not cleaned_text:
            return "Error: No text could be extracted from this PDF. It might be scanned or image-only. Please upload a valid text-based PDF resume."
            
        return cleaned_text

    except PyPDF2.errors.PdfReadError:
        return "Error: The file is not a valid PDF or is corrupted. Please upload a valid PDF resume."
    except Exception as e:
        return f"Error: An unexpected error occurred while reading the PDF: {str(e)}. Please upload a valid PDF resume."
