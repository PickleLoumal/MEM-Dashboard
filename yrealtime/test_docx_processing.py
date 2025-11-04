#!/usr/bin/env python3
"""
Test script for docx2txt functionality
This script tests if docx2txt is properly installed and working
"""

import os
import sys

def test_docx_processing():
    """Test docx2txt processing functionality"""

    try:
        import docx2txt
        from docx import Document
        print("✅ Both packages imported successfully!")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please run: pip install docx2txt python-docx")
        return False

    # Test with the Contemporary Amperex document
    doc_path = './csi300_IS/IS - F2 Battery & energy storage technology  - Contemporary Amperex Technology Co Ltd - 300750.SZ.docx'

    if not os.path.exists(doc_path):
        print(f"❌ Document not found: {doc_path}")
        print("Available files in csi300_IS directory:")
        for f in os.listdir('csi300_IS')[:10]:  # Show first 10 files
            if f.endswith('.docx'):
                print(f"  {f}")
        return False

    print(f"✅ Document found: {doc_path}")

    try:
        # Process the document
        text = docx2txt.process(doc_path)
        print(f"✅ Document processed successfully!")
        print(f"   Text length: {len(text)} characters")

        # Show some content
        lines = text.split('\n')
        print("
First 5 lines:"        for i, line in enumerate(lines[:5]):
            if line.strip():
                print(f"  {i+1}: {line}")

        # Show document statistics
        print("
Document Statistics:"        print(f"  Total lines: {len(lines)}")
        print(f"  Non-empty lines: {len([l for l in lines if l.strip()])}")

        return True

    except Exception as e:
        print(f"❌ Error processing document: {e}")
        return False

if __name__ == "__main__":
    print("Testing docx2txt functionality...")
    print("=" * 50)

    success = test_docx_processing()

    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! docx2txt is working correctly.")
    else:
        print("💥 Some tests failed. Please check the error messages above.")
        sys.exit(1)

