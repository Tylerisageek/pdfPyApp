# PDF Merger & Reader Desktop Application

A comprehensive Python desktop application for both merging multiple PDF files and reading/viewing PDF documents with an intuitive side-menu interface.

## Features

### PDF Merger
- **Easy file management**: Add multiple PDF files with a file picker
- **Reorder files**: Rearrange PDFs in the desired order using Move Up/Down buttons
- **File validation**: Automatically validates that files are readable PDFs
- **Visual feedback**: See the list of files and their order before merging
- **Clear all**: Reset the file list to start fresh

### PDF Reader
- **Continuous scroll view**: Scroll through entire PDF document without page breaks
- **High-quality rendering**: Uses PyMuPDF (fitz) for crisp, clear rendering
- **Flexible viewing modes**:
  - **Single column**: One page per row (default)
  - **2-Up view**: Two pages side-by-side
  - **Facing pages (book-style)**: Cover page on right, then left/right pairs for book-like reading
- **Advanced navigation**:
  - **Jump to page**: Enter a page number and press Enter
  - **Arrow keys**: Up/Down to scroll smoothly
  - **PageUp/PageDown**: Jump by full page with automatic alignment
  - **Home/End keys**: Jump to document start/end
  - **Mouse wheel**: Smooth scrolling support
- **Zoom controls**: Adjust zoom level from 40% to 300% (default 100%)
- **Text extraction**: Extract and copy text from entire PDF with word/character count

### Text Editor
- **Edit PDF text**: Modify text content on individual pages
- **WYSIWYG editing**: View and edit text with visual feedback
- **Apply changes**: Apply edits to PDF pages (text masking with white rectangles)
- **Save as new file**: Save edited PDFs with automatic naming

### General Features
- **Side menu navigation**: Easy switching between Merger, Reader, and Editor tools
- **Clean interface**: Modern GUI built with tkinter with intuitive controls
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Status bars**: Real-time feedback for all operations

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
   - **Scroll**: Use mouse wheel or arrow keys (Up/Down) for smooth scrolling
   - **Jump by page**: Press PageUp/PageDown to jump one full page at a time
   - **Jump to start/end**: Press Home/End keys
   - **Direct jump**: Enter a page number in the "Jump to page" field and press Enter
4. **Zoom**: Use the "-" and "+" buttons to adjust zoom level (40% to 300%)
5. **View modes**:
   - Click **"2-Up"** button to toggle two-page side-by-side view
   - Check **"Facing (cover right)"** checkbox for book-style reading (cover page on right, then left/right pairs)
6. **Extract text**: Click **"📋 Copy Text"** to view and copy all text from the PDF

### Using the Text Editor

1. Click "✏️ Text Editor" in the right-side menu
2. **Open PDF**: Click "Open PDF" to select a PDF file to edit
3. **Select page**: Use the page spinbox to navigate to different pages
4. **Edit text**: Modify the text in the editor window
5. **Apply changes**: Click "Apply Changes" to update the PDF (old text is covered with white)
6. **Save**: Click "Save PDF" to save the edited document as a new file

### Tips

- The side menu lets you quickly switch between Merger, Reader, and Editor tools
- All three tools can be used independently - merge files, read them, and edit them!
- The Reader maintains zoom level when navigating between pages
- In facing-page mode, the first page is displayed on the right as a cover, then subsequent pages are displayed as left/right spreads
- Keyboard navigation works in the Reader view for hands-free browsing
- At least 2 PDF files are required to merge
- PDF Reader and Editor require PyMuPDF and Pillow to be installed

## Keyboard Shortcuts

### PDF Reader Navigation
| Shortcut | Action |
|----------|--------|
| **Up Arrow** | Scroll up smoothly |
| **Down Arrow** | Scroll down smoothly |
| **Page Up** | Jump to previous page |
| **Page Down** | Jump to next page |
| **Home** | Jump to document start |
| **End** | Jump to document end |
| **Mouse Wheel** | Smooth scroll in any direction |
| **Enter** | In "Jump to page" field: go to that page number |

## Troubleshooting

**"PyMuPDF not available" message:**
- The PDF Reader and Editor require additional libraries. Install them with:
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

**Facing-page mode not working:**
- Make sure "2-Up" is enabled first (facing mode requires two-page view)
- If checked but not appearing, try toggling it off and back on

**Text editor changes not visible:**
- Changes are covered with white rectangles to hide old text
- This is normal behavior - the new text is inserted at the first text block location
- Save the PDF to preserve changes

**Text extraction returns no text:**
- Some PDFs have text embedded as images
- These cannot be extracted or edited; they appear as scanned content

## Technical Details

- **GUI Framework**: tkinter (included with Python)
- **PDF Merging**: pypdf library
- **PDF Rendering**: PyMuPDF (fitz) library
- **Image Processing**: Pillow (PIL) library
- **File Format**: Supports standard PDF files

## Architecture

The application uses a side-menu design pattern with three main views:
- **Merger View**: PDF merging and combining functionality
- **Reader View**: PDF viewing with continuous scroll, multiple layout modes, and text extraction
- **Editor View**: PDF text editing and modification functionality

Each view maintains its own state independently and can be used standalone or in combination. The Reader supports flexible rendering modes:
- Single-column for sequential reading
- Two-up (2-Up) for side-by-side viewing
- Facing-page book-style with automatic cover placement on the right

## Version History

- **v2.1**: Added facing-page book-style reading mode with cover on right
- **v2.0**: Added PDF Reader with continuous scroll, keyboard navigation, text extraction, and text editor with side-menu navigation
- **v1.0**: Initial release with PDF merging functionality

## License

This is a utility application provided as-is for personal use.
