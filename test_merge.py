#!/usr/bin/env python3
"""
Test script to demonstrate PDF merging functionality
This can be used to verify the core PDF merging logic works
"""

from pypdf import PdfReader, PdfWriter
from pathlib import Path


def create_sample_pdf(filename, content):
    """Create a simple test PDF using reportlab"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        c = canvas.Canvas(filename, pagesize=letter)
        c.drawString(100, 750, content)
        c.save()
        return True
    except ImportError:
        print("Note: reportlab not available, skipping sample PDF creation")
        return False


def merge_pdfs(pdf_files, output_file):
    """
    Merge multiple PDF files into one
    
    Args:
        pdf_files: List of PDF file paths to merge
        output_file: Path where merged PDF should be saved
    """
    writer = PdfWriter()
    total_pages = 0
    
    print(f"\nMerging {len(pdf_files)} PDFs...")
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"  [{i}/{len(pdf_files)}] Adding: {Path(pdf_file).name}")
        reader = PdfReader(pdf_file)
        pages_in_file = len(reader.pages)
        
        for page in reader.pages:
            writer.add_page(page)
            total_pages += 1
        
        print(f"      → Added {pages_in_file} page(s)")
    
    print(f"\nWriting merged PDF to: {output_file}")
    with open(output_file, "wb") as output:
        writer.write(output)
    
    print(f"✓ Success! Merged {len(pdf_files)} files ({total_pages} total pages)")
    return total_pages


def main():
    """Test the PDF merging functionality"""
    print("PDF Merger - Command Line Test\n" + "="*50)
    
    # Create sample PDFs if reportlab is available
    test_files = []
    if create_sample_pdf("test1.pdf", "This is test PDF #1"):
        test_files.append("test1.pdf")
    if create_sample_pdf("test2.pdf", "This is test PDF #2"):
        test_files.append("test2.pdf")
    if create_sample_pdf("test3.pdf", "This is test PDF #3"):
        test_files.append("test3.pdf")
    
    if test_files:
        # Test merging
        merge_pdfs(test_files, "merged_test.pdf")
        print("\n✓ Test completed successfully!")
        print(f"  Created merged_test.pdf from {len(test_files)} sample PDFs")
    else:
        print("\nDemo: How to use the merge function")
        print("-" * 50)
        print("from pypdf import PdfReader, PdfWriter\n")
        print("writer = PdfWriter()")
        print("for pdf_file in ['file1.pdf', 'file2.pdf', 'file3.pdf']:")
        print("    reader = PdfReader(pdf_file)")
        print("    for page in reader.pages:")
        print("        writer.add_page(page)\n")
        print("with open('merged.pdf', 'wb') as output:")
        print("    writer.write(output)")


if __name__ == "__main__":
    main()
