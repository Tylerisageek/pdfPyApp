# PDF Merger & Reader Desktop Application

A comprehensive Python desktop application for both merging multiple PDF files and reading/viewing PDF documents with an intuitive side-menu interface.

## Features

### PDF Merger
- **Easy file management**: Add multiple PDF files with a file picker
- **Drag and reorder**: Rearrange PDFs in the desired order before merging
- **File validation**: Automatically validates that files are readable PDFs
- **Visual feedback**: See the list of files and their order before merging

### PDF Reader (New!)
- **View PDF files**: Open and read any PDF document
- **Page navigation**: Move between pages with Previous/Next buttons
- **Direct page access**: Jump to any page by entering the page number
- **Zoom controls**: Zoom in/out to adjust viewing size (40% - 300%)
- **Scrollable canvas**: Scroll through large pages with built-in scrollbars
- **High-quality rendering**: Uses PyMuPDF for crisp, clear PDF rendering

### General Features
- **Side menu navigation**: Easy switching between Merger and Reader tools
- **Clean interface**: Modern GUI built with tkinter
- **Cross-platform**: Works on Windows, macOS, and Linux

## Requirements

- Python 3.6 or higher
- pypdf library (for merging)
- PyMuPDF library (for PDF rendering)
- Pillow library (for image processing)

## Installation

1. Make sure you have Python installed. You can check by running:
   ```bash
   python --version
   ```
   or
   ```bash
   python3 --version
   ```

2. Install required libraries:
   ```bash
   pip install pypdf PyMuPDF Pillow
   ```
   
   or on some systems:
   ```bash
   pip3 install pypdf PyMuPDF Pillow --break-system-packages
   ```

3. Download the `pdf_merger_enhanced.py` file to your computer

## Usage

### Running the Application

**On Windows:**
```bash
python pdf_merger_enhanced.py
```

**On macOS/Linux:**
```bash
python3 pdf_merger_enhanced.py
```

Or make it executable:
```bash
chmod +x pdf_merger_enhanced.py
./pdf_merger_enhanced.py
```

### Using the PDF Merger

1. Click "📄 PDF Merger" in the right-side menu (default view)
2. **Add PDF Files**: Click "Add PDF Files" to select one or more PDF files
3. **Arrange Order**: Use the "↑ Move Up" and "↓ Move Down" buttons to reorder files
4. **Remove Files**: Select a file and click "Remove Selected" to remove it
5. **Clear All**: Click "Clear All" to start over
6. **Merge**: Click "Merge PDFs" to combine the files
7. **Save**: Choose where to save the merged PDF file

### Using the PDF Reader

1. Click "📖 PDF Reader" in the right-side menu
2. **Open PDF**: Click "Open PDF" to select a PDF file to view
3. **Navigate Pages**: 
   - Use "← Previous" and "Next →" buttons to move between pages
   - Enter a page number and press Enter to jump directly to that page
4. **Zoom**: Use the "-" and "+" buttons to adjust the zoom level (40% to 300%)
5. **Scroll**: Use scrollbars to view different parts of large pages

### Tips

- The side menu lets you quickly switch between Merger and Reader tools
- Both tools can be used independently - merge files, then read the result!
- The Reader maintains zoom level when navigating between pages
- At least 2 PDF files are required to merge
- PDF Reader requires PyMuPDF and Pillow to be installed

## Keyboard Shortcuts

- **PDF Reader**: Press Enter after typing a page number to jump to that page
- Standard scrolling with mouse wheel or trackpad gestures

## Troubleshooting

**"PyMuPDF not available" message:**
- The PDF Reader requires additional libraries. Install them with:
  ```bash
  pip install PyMuPDF Pillow
  ```

**"Not a valid PDF" warning:**
- The file may be corrupted or not actually a PDF
- Try opening it in a PDF reader to verify it works

**PDF displays blurry:**
- Try increasing the zoom level using the "+" button
- Some PDFs with complex graphics may render differently than in other viewers

**Application won't start:**
- Make sure Python 3.6+ is installed
- Install all required packages: `pip install -r requirements_enhanced.txt`
- Try running from the command line to see error messages

**Zoom too high or too low:**
- Use the zoom controls to adjust between 40% and 300%
- Default zoom is 100%

## Technical Details

- **GUI Framework**: tkinter (included with Python)
- **PDF Merging**: pypdf library
- **PDF Rendering**: PyMuPDF (fitz) library
- **Image Processing**: Pillow (PIL) library
- **File Format**: Supports standard PDF files

## Architecture

The application uses a side-menu design pattern with two main views:
- **Merger View**: Original PDF merging functionality
- **Reader View**: New PDF viewing and navigation functionality

The views are switched using a simple frame management system, and each maintains its own state independently.

## Version History

- **v2.0**: Added PDF Reader with side-menu navigation
- **v1.0**: Initial release with PDF merging functionality

## License

This is a utility application provided as-is for personal use.
