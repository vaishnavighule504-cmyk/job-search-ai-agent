import PyPDF2


def extract_text_from_pdf(pdf_file):
    """Extracts all text from an uploaded PDF file stream.

    Args:
        pdf_file: A file-like object representing the uploaded PDF.

    Returns:
        str: The full text extracted from the PDF, or an error message if it fails.
    """
    text = ""
    try:
        # Initialize a PDF Reader object using the uploaded PDF file stream.
        # This parses the PDF structure and makes pages accessible.
        reader = PyPDF2.PdfReader(pdf_file)

        # Loop through each page in the document (0-indexed)
        for page in reader.pages:
            # Extract plain text from the current page
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    except Exception as e:
        return f"Error reading PDF: {e}"

    return text.strip()
