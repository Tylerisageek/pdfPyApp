# PDF Merger Desktop Application

A simple and intuitive Python desktop application for merging multiple PDF files into a single document.

## Features

- **Easy file management**: Add multiple PDF files with a file picker
- **Drag and reorder**: Rearrange PDFs in the desired order before merging
- **File validation**: Automatically validates that files are readable PDFs
- **Visual feedback**: See the list of files and their order before merging
- **Simple interface**: Clean, user-friendly GUI built with tkinter
- **Cross-platform**: Works on Windows, macOS, and Linux

## Requirements

- Python 3.6 or higher
- pypdf library (will be installed automatically if missing)

## Installation

1. Make sure you have Python installed. You can check by running:
   ```bash
   python --version
   ```
   or
   ```bash
   python3 --version
   ```

2. Download the `pdf_merger.py` file to your computer

3. The application will automatically install the required `pypdf` library when first run

## Usage

### Running the Application

**On Windows:**
```bash
python pdf_merger.py
```

**On macOS/Linux:**
```bash
python3 pdf_merger.py
```

Or make it executable:
```bash
chmod +x pdf_merger.py
./pdf_merger.py
```

### Using the Application

1. **Add PDF Files**: Click "Add PDF Files" to select one or more PDF files
2. **Arrange Order**: Use the "↑ Move Up" and "↓ Move Down" buttons to reorder files
3. **Remove Files**: Select a file and click "Remove Selected" to remove it
4. **Clear All**: Click "Clear All" to start over
5. **Merge**: Click "Merge PDFs" to combine the files
6. **Save**: Choose where to save the merged PDF file

### Tips

- You can add files multiple times to build your list
- The application validates each PDF before adding it
- At least 2 PDF files are required to merge
- The final PDF will contain all pages from all files in the order shown

## Troubleshooting

**"pypdf not found" error:**
- The application should auto-install pypdf, but you can manually install it:
  ```bash
  pip install pypdf
  ```
  or on some systems:
  ```bash
  pip3 install pypdf --break-system-packages
  ```

**"Not a valid PDF" warning:**
- The file may be corrupted or not actually a PDF
- Try opening it in a PDF reader to verify it works

**Application won't start:**
- Make sure Python 3.6+ is installed
- Try running from the command line to see error messages

## Technical Details

- **GUI Framework**: tkinter (included with Python)
- **PDF Processing**: pypdf library
- **File Format**: Supports standard PDF files

## License

This is a simple utility application provided as-is for personal use.
