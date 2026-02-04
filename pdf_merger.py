#!/usr/bin/env python3
"""
PDF Merger & Reader - A desktop application for merging and reading PDF files
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import sys
import io

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("Error: pypdf library not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf", "--break-system-packages"])
    from pypdf import PdfReader, PdfWriter

try:
    from PIL import Image, ImageTk
    import fitz  # PyMuPDF for better PDF rendering
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("Note: PyMuPDF not available. PDF reader will have limited functionality.")
    print("Install with: pip install PyMuPDF Pillow")


class PDFMergerReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Merger & Reader")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Shared state variables
        self.pdf_files = []  # For merger
        self.pdf_document = None  # Current PDF document
        self.current_pdf = None  # Current PDF path
        self.total_pages = 0
        self.current_page = 0
        self.zoom_level = 1.0
        self.is_editing = False
        self.page_images = []  # Keep references for tkinter
        self.two_up = False  # two-page side-by-side mode
        # Facing-pages (book-style) option: cover on the right
        self.facing_cover_right = tk.BooleanVar(value=False)
        
        # UI Setup
        self.setup_main_ui()
        
    def setup_main_ui(self):
        """Create the main UI with sidebar and content areas"""
        # Main container with horizontal layout
        main_container = ttk.Frame(self.root)
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(0, weight=1)
        
        # Content area
        self.content_frame = ttk.Frame(main_container)
        self.content_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)
        
        # Setup the three main views
        self.setup_merger_view()
        self.setup_reader_view()
        self.setup_editor_view()
        
        # Create side menu
        self.setup_side_menu(main_container)
        
        # Show merger view by default
        self.show_view('merger')
        
    def setup_side_menu(self, parent):
        """Create the vertical side menu"""
        menu_frame = ttk.Frame(parent, relief=tk.RAISED, borderwidth=2)
        menu_frame.grid(row=0, column=1, sticky=(tk.N, tk.S), padx=(10, 0))
        
        # Menu title
        menu_title = ttk.Label(menu_frame, text="Tools", 
                              font=("Helvetica", 11, "bold"))
        menu_title.pack(pady=(10, 5))
        
        ttk.Separator(menu_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5, pady=5)
        
        # Merger button
        self.merger_btn = ttk.Button(menu_frame, text="📄 PDF Merger", 
                                    command=lambda: self.show_view('merger'),
                                    width=15)
        self.merger_btn.pack(pady=5, padx=10)
        
        # Reader button
        self.reader_btn = ttk.Button(menu_frame, text="📖 PDF Reader", 
                                    command=lambda: self.show_view('reader'),
                                    width=15)
        self.reader_btn.pack(pady=5, padx=10)
        
        # Editor button
        self.editor_btn = ttk.Button(menu_frame, text="✏️ Text Editor", 
                                    command=lambda: self.show_view('editor'),
                                    width=15)
        self.editor_btn.pack(pady=5, padx=10)
        
        ttk.Separator(menu_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5, pady=10)
        
        # About button
        about_btn = ttk.Button(menu_frame, text="ℹ About", 
                              command=self.show_about,
                              width=15)
        about_btn.pack(pady=5, padx=10, side=tk.BOTTOM)
        
    def setup_merger_view(self):
        """Create the PDF merger interface"""
        self.merger_frame = ttk.Frame(self.content_frame, padding="10")
        
        # Configure grid weights for resizing
        self.merger_frame.columnconfigure(0, weight=1)
        self.merger_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(self.merger_frame, text="PDF Merger", 
                               font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Instructions
        instructions = ttk.Label(self.merger_frame, 
                                text="Add PDF files below, arrange them in order, then merge",
                                font=("Helvetica", 10))
        instructions.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(self.merger_frame)
        list_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.file_listbox = tk.Listbox(list_frame, 
                                       yscrollcommand=scrollbar.set,
                                       height=12,
                                       selectmode=tk.SINGLE)
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.config(command=self.file_listbox.yview)
        
        # File count label
        self.file_count_label = ttk.Label(self.merger_frame, text="No files added")
        self.file_count_label.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        # Buttons frame
        button_frame = ttk.Frame(self.merger_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(0, 10))
        
        # Buttons
        self.add_button = ttk.Button(button_frame, text="Add PDF Files", 
                                     command=self.add_files)
        self.add_button.grid(row=0, column=0, padx=5)
        
        self.remove_button = ttk.Button(button_frame, text="Remove Selected", 
                                        command=self.remove_selected, state=tk.DISABLED)
        self.remove_button.grid(row=0, column=1, padx=5)
        
        self.move_up_button = ttk.Button(button_frame, text="↑ Move Up", 
                                         command=self.move_up, state=tk.DISABLED)
        self.move_up_button.grid(row=0, column=2, padx=5)
        
        self.move_down_button = ttk.Button(button_frame, text="↓ Move Down", 
                                           command=self.move_down, state=tk.DISABLED)
        self.move_down_button.grid(row=0, column=3, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="Clear All", 
                                       command=self.clear_all, state=tk.DISABLED)
        self.clear_button.grid(row=0, column=4, padx=5)
        
        # Merge button
        self.merge_button = ttk.Button(self.merger_frame, text="Merge PDFs", 
                                       command=self.merge_pdfs, state=tk.DISABLED)
        self.merge_button.grid(row=5, column=0, columnspan=2, pady=10, ipadx=20, ipady=5)
        
        # Status bar
        self.merger_status_label = ttk.Label(self.merger_frame, text="Ready", 
                                            relief=tk.SUNKEN, anchor=tk.W)
        self.merger_status_label.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Bind listbox selection event
        self.file_listbox.bind('<<ListboxSelect>>', self.on_select)
        
    def setup_reader_view(self):
        """Create the PDF reader interface"""
        self.reader_frame = ttk.Frame(self.content_frame, padding="10")
        
        # Configure grid weights
        self.reader_frame.columnconfigure(0, weight=1)
        self.reader_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(self.reader_frame, text="PDF Reader", 
                               font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Toolbar
        toolbar = ttk.Frame(self.reader_frame)
        toolbar.grid(row=1, column=0, columnspan=3, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Open PDF button
        open_btn = ttk.Button(toolbar, text="Open PDF", command=self.open_pdf)
        open_btn.pack(side=tk.LEFT, padx=5)
        
        # Extract text button
        text_btn = ttk.Button(toolbar, text="📋 Copy Text", command=self.extract_page_text)
        text_btn.pack(side=tk.LEFT, padx=5)
        
        # Zoom controls
        ttk.Label(toolbar, text="Zoom:").pack(side=tk.LEFT, padx=(20, 5))
        zoom_out_btn = ttk.Button(toolbar, text="-", command=self.zoom_out, width=3)
        zoom_out_btn.pack(side=tk.LEFT, padx=2)
        
        self.zoom_label = ttk.Label(toolbar, text="100%", width=6)
        self.zoom_label.pack(side=tk.LEFT, padx=2)
        
        zoom_in_btn = ttk.Button(toolbar, text="+", command=self.zoom_in, width=3)
        zoom_in_btn.pack(side=tk.LEFT, padx=2)

        # Two-page side-by-side toggle
        self.two_up_btn = ttk.Button(toolbar, text="2-Up", command=self.toggle_two_up)
        self.two_up_btn.pack(side=tk.LEFT, padx=(10, 2))
        # Facing pages (cover on right) checkbox
        self.facing_chk = ttk.Checkbutton(toolbar, text="Facing (cover right)",
                          variable=self.facing_cover_right,
                          command=self.toggle_facing_mode)
        self.facing_chk.pack(side=tk.LEFT, padx=(5, 2))
        
        # Page info
        self.page_info_label = ttk.Label(toolbar, text="No PDF loaded")
        self.page_info_label.pack(side=tk.RIGHT, padx=10)
        
        # PDF display area with scrollbars
        display_frame = ttk.Frame(self.reader_frame)
        display_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        
        # Create canvas with scrollbars
        v_scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        h_scrollbar = ttk.Scrollbar(display_frame, orient=tk.HORIZONTAL)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.pdf_canvas = tk.Canvas(display_frame, 
                                    bg='gray85',
                                    xscrollcommand=h_scrollbar.set,
                                    yscrollcommand=v_scrollbar.set)
        self.pdf_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        v_scrollbar.config(command=self.pdf_canvas.yview)
        h_scrollbar.config(command=self.pdf_canvas.xview)
        
        # Bind mouse wheel for scrolling
        self.pdf_canvas.bind("<MouseWheel>", self._on_mousewheel)
        # Bind arrow keys for scrolling the reader (Up/Down)
        # Use bind_all so keys work even if canvas doesn't have explicit focus
        self.root.bind_all("<Up>", self._on_key_up)
        self.root.bind_all("<Down>", self._on_key_down)
        # PageUp/PageDown and Home/End bindings
        self.root.bind_all("<Prior>", self._on_page_up)
        self.root.bind_all("<Next>", self._on_page_down)
        self.root.bind_all("<Home>", self._on_home)
        self.root.bind_all("<End>", self._on_end)
        
        # Navigation controls
        nav_frame = ttk.Frame(self.reader_frame)
        nav_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        self.goto_page_label = ttk.Label(nav_frame, text="Jump to page:")
        self.goto_page_label.pack(side=tk.LEFT, padx=5)
        
        self.goto_page_entry = ttk.Entry(nav_frame, width=8, justify=tk.CENTER)
        self.goto_page_entry.pack(side=tk.LEFT, padx=5)
        self.goto_page_entry.bind('<Return>', self.jump_to_page)
        
        self.goto_page_btn = ttk.Button(nav_frame, text="Go", command=self.jump_to_page)
        self.goto_page_btn.pack(side=tk.LEFT, padx=2)
        
        page_info = ttk.Label(nav_frame, text="(Scroll to navigate)", font=("Helvetica", 9), foreground="gray")
        page_info.pack(side=tk.LEFT, padx=10)
        
        # Reader status bar
        self.reader_status_label = ttk.Label(self.reader_frame, text="Open a PDF to begin", 
                                            relief=tk.SUNKEN, anchor=tk.W)
        self.reader_status_label.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E))
    
    def setup_editor_view(self):
        """Create the PDF text editor interface"""
        self.editor_frame = ttk.Frame(self.content_frame, padding="10")
        
        # Configure grid weights
        self.editor_frame.columnconfigure(0, weight=1)
        self.editor_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(self.editor_frame, text="PDF Text Editor", 
                               font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Toolbar
        toolbar = ttk.Frame(self.editor_frame)
        toolbar.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Open PDF button
        open_btn = ttk.Button(toolbar, text="Open PDF", command=self.editor_open_pdf)
        open_btn.pack(side=tk.LEFT, padx=5)
        
        # Page navigation
        ttk.Label(toolbar, text="Page:").pack(side=tk.LEFT, padx=(20, 5))
        self.editor_page_spinbox = ttk.Spinbox(toolbar, from_=1, to=1, width=5, 
                                               command=self.editor_load_page)
        self.editor_page_spinbox.pack(side=tk.LEFT, padx=5)
        self.editor_page_label = ttk.Label(toolbar, text="of 0")
        self.editor_page_label.pack(side=tk.LEFT, padx=5)
        
        # Page info
        self.editor_status_label = ttk.Label(toolbar, text="No PDF loaded")
        self.editor_status_label.pack(side=tk.RIGHT, padx=10)
        
        # Text editor area
        text_frame = ttk.LabelFrame(self.editor_frame, text="Edit Text on Current Page", padding="5")
        text_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        # Create text widget with scrollbar
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.editor_text = tk.Text(text_frame, 
                                   yscrollcommand=scrollbar.set,
                                   wrap=tk.WORD,
                                   font=("Courier", 10),
                                   height=15)
        self.editor_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.config(command=self.editor_text.yview)
        
        # Control buttons
        button_frame = ttk.Frame(self.editor_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.editor_reload_btn = ttk.Button(button_frame, text="Reload Page Text", 
                                           command=self.editor_load_page, state=tk.DISABLED)
        self.editor_reload_btn.pack(side=tk.LEFT, padx=5)
        
        self.editor_apply_btn = ttk.Button(button_frame, text="Apply Changes", 
                                          command=self.editor_apply_changes, state=tk.DISABLED)
        self.editor_apply_btn.pack(side=tk.LEFT, padx=5)
        
        self.editor_save_btn = ttk.Button(button_frame, text="Save PDF", 
                                         command=self.editor_save_pdf, state=tk.DISABLED)
        self.editor_save_btn.pack(side=tk.LEFT, padx=5)
        
        # Editor status bar
        self.editor_info_label = ttk.Label(self.editor_frame, text="Open a PDF to begin editing", 
                                          relief=tk.SUNKEN, anchor=tk.W)
        self.editor_info_label.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
    def show_view(self, view_name):
        """Switch between merger, reader, and editor views"""
        # Hide all views
        self.merger_frame.grid_forget()
        self.reader_frame.grid_forget()
        self.editor_frame.grid_forget()
        
        # Show requested view
        if view_name == 'merger':
            self.merger_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            self.current_view = 'merger'
            self.merger_btn.state(['pressed'])
            self.reader_btn.state(['!pressed'])
            self.editor_btn.state(['!pressed'])
        elif view_name == 'reader':
            self.reader_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            self.current_view = 'reader'
            self.reader_btn.state(['pressed'])
            self.merger_btn.state(['!pressed'])
            self.editor_btn.state(['!pressed'])
        elif view_name == 'editor':
            self.editor_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            self.current_view = 'editor'
            self.editor_btn.state(['pressed'])
            self.merger_btn.state(['!pressed'])
            self.reader_btn.state(['!pressed'])
    
    # ========== MERGER FUNCTIONS ==========
    
    def add_files(self):
        """Open file dialog to add PDF files"""
        files = filedialog.askopenfilenames(
            title="Select PDF files",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if files:
            added_count = 0
            for file_path in files:
                if self.validate_pdf(file_path):
                    self.pdf_files.append(file_path)
                    filename = Path(file_path).name
                    self.file_listbox.insert(tk.END, filename)
                    added_count += 1
                else:
                    messagebox.showwarning("Invalid File", 
                                          f"Skipped: {Path(file_path).name}\n(Not a valid PDF)")
            
            self.update_merger_ui_state()
            if added_count > 0:
                self.merger_status_label.config(text=f"Added {added_count} file(s)")
    
    def validate_pdf(self, file_path):
        """Validate that the file is a readable PDF"""
        try:
            reader = PdfReader(file_path)
            return len(reader.pages) > 0
        except Exception:
            return False
    
    def remove_selected(self):
        """Remove the selected file from the list"""
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            self.file_listbox.delete(index)
            del self.pdf_files[index]
            self.update_merger_ui_state()
            self.merger_status_label.config(text="File removed")
    
    def move_up(self):
        """Move selected file up in the list"""
        selection = self.file_listbox.curselection()
        if selection and selection[0] > 0:
            index = selection[0]
            self.pdf_files[index], self.pdf_files[index-1] = \
                self.pdf_files[index-1], self.pdf_files[index]
            item = self.file_listbox.get(index)
            self.file_listbox.delete(index)
            self.file_listbox.insert(index-1, item)
            self.file_listbox.selection_set(index-1)
            self.merger_status_label.config(text="File moved up")
    
    def move_down(self):
        """Move selected file down in the list"""
        selection = self.file_listbox.curselection()
        if selection and selection[0] < len(self.pdf_files) - 1:
            index = selection[0]
            self.pdf_files[index], self.pdf_files[index+1] = \
                self.pdf_files[index+1], self.pdf_files[index]
            item = self.file_listbox.get(index)
            self.file_listbox.delete(index)
            self.file_listbox.insert(index+1, item)
            self.file_listbox.selection_set(index+1)
            self.merger_status_label.config(text="File moved down")
    
    def clear_all(self):
        """Clear all files from the list"""
        if messagebox.askyesno("Clear All", "Remove all files from the list?"):
            self.file_listbox.delete(0, tk.END)
            self.pdf_files.clear()
            self.update_merger_ui_state()
            self.merger_status_label.config(text="All files removed")
    
    def on_select(self, event):
        """Handle listbox selection change"""
        self.update_merger_ui_state()
    
    def update_merger_ui_state(self):
        """Update button states and file count based on current state"""
        num_files = len(self.pdf_files)
        selection = self.file_listbox.curselection()
        
        if num_files == 0:
            self.file_count_label.config(text="No files added")
        elif num_files == 1:
            self.file_count_label.config(text="1 file added")
        else:
            self.file_count_label.config(text=f"{num_files} files added")
        
        self.merge_button.config(state=tk.NORMAL if num_files >= 2 else tk.DISABLED)
        self.clear_button.config(state=tk.NORMAL if num_files > 0 else tk.DISABLED)
        self.remove_button.config(state=tk.NORMAL if selection else tk.DISABLED)
        
        if selection:
            index = selection[0]
            self.move_up_button.config(state=tk.NORMAL if index > 0 else tk.DISABLED)
            self.move_down_button.config(state=tk.NORMAL if index < num_files - 1 else tk.DISABLED)
        else:
            self.move_up_button.config(state=tk.DISABLED)
            self.move_down_button.config(state=tk.DISABLED)
    
    def merge_pdfs(self):
        """Merge all PDFs in the list into a single file"""
        if len(self.pdf_files) < 2:
            messagebox.showwarning("Not Enough Files", 
                                  "Please add at least 2 PDF files to merge.")
            return
        
        output_file = filedialog.asksaveasfilename(
            title="Save merged PDF as",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="merged.pdf"
        )
        
        if not output_file:
            return
        
        try:
            self.merger_status_label.config(text="Merging PDFs...")
            self.root.update()
            
            writer = PdfWriter()
            total_pages = 0
            
            for pdf_file in self.pdf_files:
                reader = PdfReader(pdf_file)
                for page in reader.pages:
                    writer.add_page(page)
                    total_pages += 1
            
            with open(output_file, "wb") as output:
                writer.write(output)
            
            self.merger_status_label.config(text=f"Success! Merged {len(self.pdf_files)} files ({total_pages} pages)")
            messagebox.showinfo("Success", 
                               f"PDFs merged successfully!\n\n"
                               f"Files merged: {len(self.pdf_files)}\n"
                               f"Total pages: {total_pages}\n\n"
                               f"Saved to: {Path(output_file).name}")
            
        except Exception as e:
            self.merger_status_label.config(text="Error during merge")
            messagebox.showerror("Error", f"Failed to merge PDFs:\n{str(e)}")
    
    # ========== READER FUNCTIONS ==========
    
    def open_pdf(self):
        """Open a PDF file for reading"""
        file_path = filedialog.askopenfilename(
            title="Open PDF file",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        if not PYMUPDF_AVAILABLE:
            messagebox.showerror("Missing Dependency", 
                               "PDF Reader requires PyMuPDF and Pillow.\n\n"
                               "Install with:\npip install PyMuPDF Pillow")
            return
        
        try:
            # Close previous PDF if open
            if self.pdf_document:
                self.pdf_document.close()
            
            # Open new PDF
            self.pdf_document = fitz.open(file_path)
            self.current_pdf = file_path
            self.total_pages = len(self.pdf_document)
            self.current_page = 0
            self.zoom_level = 1.0
            
            # Update UI
            self.update_zoom_label()
            self.render_all_pages()
            
            filename = Path(file_path).name
            self.reader_status_label.config(text=f"Opened: {filename}")
            self.page_info_label.config(text=f"{self.total_pages} pages")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF:\n{str(e)}")
    
    def render_all_pages(self):
        """Render all pages to the canvas in a scrollable view"""
        if not self.pdf_document or self.total_pages == 0:
            return
        
        try:
            # Clear the canvas
            self.pdf_canvas.delete("all")
            
            # Render all pages and stack them vertically
            y_offset = 10
            self.page_images = []  # Keep references to prevent garbage collection
            self.page_positions = []  # Y offset (top) for each page
            total_width = 0
            gap = 20
            
            page_index = 0
            # Two-up rendering with optional book-style facing pages (cover on right)
            if self.two_up:
                facing_on = False
                try:
                    facing_on = bool(self.facing_cover_right.get())
                except Exception:
                    facing_on = False

                # If facing with cover on right, render the very first page as a right-side single
                if facing_on and page_index < self.total_pages:
                    page = self.pdf_document[page_index]
                    mat = fitz.Matrix(self.zoom_level, self.zoom_level)
                    pix = page.get_pixmap(matrix=mat)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    photo = ImageTk.PhotoImage(img)
                    self.page_images.append(photo)

                    x1 = 10
                    x2 = x1 + pix.width + gap
                    # Draw the first page on the right side (blank left)
                    self.pdf_canvas.create_image(x2, y_offset, anchor=tk.NW, image=photo)
                    self.page_positions.append(y_offset)
                    self.pdf_canvas.create_text(x2 + pix.width + 10, y_offset + 10,
                                               text=f"Page {page_index + 1}",
                                               font=("Helvetica", 8), fill="gray", anchor=tk.W)
                    y_offset += pix.height + 20
                    total_width = max(total_width, x2 + pix.width + 20)
                    page_index += 1

                # Now render remaining pages as left/right pairs
                while page_index < self.total_pages:
                    # Left page
                    page_left = self.pdf_document[page_index]
                    mat = fitz.Matrix(self.zoom_level, self.zoom_level)
                    pix_left = page_left.get_pixmap(matrix=mat)
                    img_left = Image.frombytes("RGB", [pix_left.width, pix_left.height], pix_left.samples)
                    photo_left = ImageTk.PhotoImage(img_left)
                    self.page_images.append(photo_left)

                    x1 = 10
                    x2 = x1 + pix_left.width + gap

                    # Right page if exists
                    photo_right = None
                    pix_right = None
                    if page_index + 1 < self.total_pages:
                        page_right = self.pdf_document[page_index + 1]
                        pix_right = page_right.get_pixmap(matrix=mat)
                        img_right = Image.frombytes("RGB", [pix_right.width, pix_right.height], pix_right.samples)
                        photo_right = ImageTk.PhotoImage(img_right)
                        self.page_images.append(photo_right)

                    # Draw left
                    self.pdf_canvas.create_image(x1, y_offset, anchor=tk.NW, image=photo_left)
                    self.page_positions.append(y_offset)

                    # Draw right if present
                    if photo_right:
                        self.pdf_canvas.create_image(x2, y_offset, anchor=tk.NW, image=photo_right)
                        self.page_positions.append(y_offset)
                        row_width = pix_left.width + gap + pix_right.width
                        row_height = max(pix_left.height, pix_right.height)
                        label_x = x2 + (pix_right.width if pix_right else 0) + 10
                        self.pdf_canvas.create_text(label_x, y_offset + 10,
                                                   text=f"Pages {page_index + 1} / {page_index + 2}",
                                                   font=("Helvetica", 8), fill="gray", anchor=tk.W)
                    else:
                        row_width = pix_left.width
                        row_height = pix_left.height
                        label_x = x1 + pix_left.width + 10
                        self.pdf_canvas.create_text(label_x, y_offset + 10,
                                                   text=f"Page {page_index + 1}",
                                                   font=("Helvetica", 8), fill="gray", anchor=tk.W)

                    y_offset += row_height + 20
                    total_width = max(total_width, row_width + x1 + 20)
                    page_index += 2 if photo_right else 1
            else:
                # Single-column rendering (one page per row)
                # Get canvas width for centering
                canvas_width = self.pdf_canvas.winfo_width()
                if canvas_width <= 1:  # If not yet rendered, use default
                    canvas_width = 800
                
                while page_index < self.total_pages:
                    page = self.pdf_document[page_index]
                    mat = fitz.Matrix(self.zoom_level, self.zoom_level)
                    pix = page.get_pixmap(matrix=mat)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    photo = ImageTk.PhotoImage(img)
                    self.page_images.append(photo)

                    # Calculate center x position for the page
                    center_x = canvas_width / 2

                    # Add to canvas centered horizontally
                    self.pdf_canvas.create_image(center_x, y_offset, anchor=tk.N, image=photo)
                    # Record the top position for this page
                    self.page_positions.append(y_offset)

                    # Add page number label to the right of the page
                    self.pdf_canvas.create_text(center_x + pix.width / 2 + 10, y_offset + 10,
                                               text=f"Page {page_index + 1}",
                                               font=("Helvetica", 8), fill="gray", anchor=tk.W)

                    # Update y offset for next page
                    y_offset += pix.height + 20
                    total_width = max(total_width, canvas_width)
                    page_index += 1
            
            # Update canvas scrollregion and total rendered size
            self.total_render_height = max(y_offset, 1)
            total_width = max(total_width, 800)
            self.pdf_canvas.config(scrollregion=(0, 0, total_width, self.total_render_height))
            
        except Exception as e:
            messagebox.showerror("Rendering Error", f"Failed to render pages:\n{str(e)}")
    
    def jump_to_page(self, event=None):
        """Jump to a specific page number"""
        try:
            page_num = int(self.goto_page_entry.get()) - 1  # Convert to 0-indexed
            if 0 <= page_num < self.total_pages:
                # Use recorded page positions if available for exact jump
                if hasattr(self, 'page_positions') and len(self.page_positions) == self.total_pages:
                    y_position = self.page_positions[page_num]
                    frac = y_position / float(getattr(self, 'total_render_height', max(y_position, 1)))
                    self.pdf_canvas.yview_moveto(frac)
                else:
                    # Fallback: approximate
                    y_position = page_num * 300
                    self.pdf_canvas.yview_moveto(y_position / (self.total_pages * 300))
                self.goto_page_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Invalid Page", 
                                      f"Please enter a page number between 1 and {self.total_pages}")
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid page number")
    
    def zoom_in(self):
        """Increase zoom level"""
        if self.zoom_level < 3.0:
            self.zoom_level += 0.2
            self.update_zoom_label()
            self.render_all_pages()
    
    def zoom_out(self):
        """Decrease zoom level"""
        if self.zoom_level > 0.4:
            self.zoom_level -= 0.2
            self.update_zoom_label()
            self.render_all_pages()
    
    def update_zoom_label(self):
        """Update the zoom percentage label"""
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.pdf_canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def _on_key_up(self, event):
        """Scroll up when Up arrow key is pressed"""
        try:
            self.pdf_canvas.yview_scroll(-3, "units")
        except Exception:
            pass

    def _on_key_down(self, event):
        """Scroll down when Down arrow key is pressed"""
        try:
            self.pdf_canvas.yview_scroll(3, "units")
        except Exception:
            pass

    def _on_page_up(self, event):
        """Handle PageUp key - scroll up by a larger amount"""
        try:
            # If we have page positions, jump exactly one page up
            if hasattr(self, 'page_positions') and self.page_positions:
                top_y = self.pdf_canvas.canvasy(0)
                # find current page index
                idx = 0
                for i, py in enumerate(self.page_positions):
                    if py <= top_y + 1:
                        idx = i
                    else:
                        break
                target = max(0, idx - 1)
                y = self.page_positions[target]
                frac = y / float(getattr(self, 'total_render_height', max(y, 1)))
                self.pdf_canvas.yview_moveto(frac)
            else:
                # Fallback: scroll up by several viewport units
                self.pdf_canvas.yview_scroll(-25, "units")
        except Exception:
            pass

    def _on_page_down(self, event):
        """Handle PageDown key - scroll down by a larger amount"""
        try:
            # If we have page positions, jump exactly one page down
            if hasattr(self, 'page_positions') and self.page_positions:
                top_y = self.pdf_canvas.canvasy(0)
                # find current page index
                idx = 0
                for i, py in enumerate(self.page_positions):
                    if py <= top_y + 1:
                        idx = i
                    else:
                        break
                target = min(len(self.page_positions) - 1, idx + 1)
                y = self.page_positions[target]
                frac = y / float(getattr(self, 'total_render_height', max(y, 1)))
                self.pdf_canvas.yview_moveto(frac)
            else:
                self.pdf_canvas.yview_scroll(25, "units")
        except Exception:
            pass

    def _on_home(self, event):
        """Jump to the top of the document"""
        try:
            self.pdf_canvas.yview_moveto(0.0)
        except Exception:
            pass

    def _on_end(self, event):
        """Jump to the end/bottom of the document"""
        try:
            self.pdf_canvas.yview_moveto(1.0)
        except Exception:
            pass

    def toggle_two_up(self):
        """Toggle two-page side-by-side view and re-render"""
        try:
            self.two_up = not getattr(self, 'two_up', False)
            # If disabling two-up, also disable facing-book mode
            if not self.two_up:
                try:
                    self.facing_cover_right.set(False)
                except Exception:
                    pass
            # Update button label
            if self.two_up:
                self.two_up_btn.config(text="Single")
            else:
                self.two_up_btn.config(text="2-Up")
            # Re-render pages in the new layout
            self.render_all_pages()
        except Exception:
            pass

    def toggle_facing_mode(self):
        """Toggle facing-page (book-style) mode. Enabling facing will turn on two-up view."""
        try:
            facing = bool(self.facing_cover_right.get())
            if facing and not getattr(self, 'two_up', False):
                # Ensure two-up is enabled when facing mode is selected
                self.two_up = True
                self.two_up_btn.config(text="Single")
            # Re-render to apply facing layout
            self.render_all_pages()
        except Exception:
            pass
    
    def extract_page_text(self):
        """Extract and display text from all pages for copying"""
        if not self.pdf_document or self.total_pages == 0:
            messagebox.showwarning("No PDF", "Please open a PDF first.")
            return
        
        try:
            # Extract text from all pages
            all_text = ""
            for page_num in range(self.total_pages):
                page = self.pdf_document[page_num]
                text = page.get_text()
                all_text += f"\n--- Page {page_num + 1} ---\n{text}"
            
            if not all_text.strip():
                messagebox.showinfo("No Text", "No text found in the PDF.")
                return
            
            # Create a new window to display the text
            text_window = tk.Toplevel(self.root)
            text_window.title(f"PDF Text - {Path(self.current_pdf).name}")
            text_window.geometry("600x400")
            
            # Add a frame with label and close button
            top_frame = ttk.Frame(text_window)
            top_frame.pack(fill=tk.X, padx=5, pady=5)
            
            ttk.Label(top_frame, text="Select and copy text below:", font=("Helvetica", 10)).pack(side=tk.LEFT)
            copy_btn = ttk.Button(top_frame, text="Copy All", 
                                 command=lambda: self.copy_to_clipboard(all_text))
            copy_btn.pack(side=tk.RIGHT, padx=5)
            
            # Create text widget with scrollbar
            text_frame = ttk.Frame(text_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            text_frame.columnconfigure(0, weight=1)
            text_frame.rowconfigure(0, weight=1)
            
            scrollbar = ttk.Scrollbar(text_frame)
            scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
            
            text_widget = tk.Text(text_frame, 
                                 yscrollcommand=scrollbar.set,
                                 wrap=tk.WORD,
                                 font=("Courier", 10))
            text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            scrollbar.config(command=text_widget.yview)
            
            # Insert the extracted text
            text_widget.insert(1.0, all_text)
            text_widget.config(state=tk.NORMAL)
            
            # Add bottom frame with info
            bottom_frame = ttk.Frame(text_window)
            bottom_frame.pack(fill=tk.X, padx=5, pady=5)
            
            char_count = len(all_text)
            word_count = len(all_text.split())
            info_label = ttk.Label(bottom_frame, 
                                  text=f"Characters: {char_count} | Words: {word_count}",
                                  font=("Helvetica", 9),
                                  foreground="gray")
            info_label.pack(side=tk.LEFT)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract text:\n{str(e)}")
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()
            messagebox.showinfo("Success", "Text copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard:\n{str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """PDF Merger & Reader

Version 2.0

Features:
• Merge multiple PDFs into one
• Read and view PDF files
• Continuous scroll view for entire documents
• Zoom and search pages
• Edit text in PDFs
• Extract and copy text
• User-friendly interface

Created with Python, tkinter, pypdf, and PyMuPDF"""
        
        messagebox.showinfo("About", about_text)
    
    # ========== TEXT EDITOR FUNCTIONS ==========
    
    def editor_open_pdf(self):
        """Open a PDF file for text editing"""
        file_path = filedialog.askopenfilename(
            title="Open PDF file for editing",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        if not PYMUPDF_AVAILABLE:
            messagebox.showerror("Missing Dependency", 
                               "PDF Editor requires PyMuPDF and Pillow.\n\n"
                               "Install with:\npip install PyMuPDF Pillow")
            return
        
        try:
            # Close previous PDF if open
            if self.pdf_document:
                self.pdf_document.close()
            
            # Open new PDF for editing
            self.pdf_document = fitz.open(file_path)
            self.current_pdf = file_path
            self.total_pages = len(self.pdf_document)
            self.current_page = 0
            self.is_editing = True
            
            # Update spinbox range
            self.editor_page_spinbox.config(to=self.total_pages)
            self.editor_page_spinbox.set(1)
            self.editor_page_label.config(text=f"of {self.total_pages}")
            
            # Load first page text
            self.editor_load_page()
            
            filename = Path(file_path).name
            self.editor_status_label.config(text=f"Editing: {filename}")
            self.editor_info_label.config(text="Ready to edit")
            
            # Enable buttons
            self.editor_reload_btn.config(state=tk.NORMAL)
            self.editor_apply_btn.config(state=tk.NORMAL)
            self.editor_save_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF:\n{str(e)}")
    
    def editor_load_page(self):
        """Load text from the current page"""
        if not self.pdf_document or not self.is_editing:
            return
        
        try:
            # Get page number from spinbox
            page_num = int(self.editor_page_spinbox.get()) - 1
            if page_num < 0 or page_num >= self.total_pages:
                messagebox.showwarning("Invalid Page", 
                                      f"Page must be between 1 and {self.total_pages}")
                return
            
            self.current_page = page_num
            
            # Extract text from page
            page = self.pdf_document[self.current_page]
            text = page.get_text()
            
            # Store original text
            self.original_text = text
            
            # Display text in editor
            self.editor_text.delete(1.0, tk.END)
            self.editor_text.insert(1.0, text)
            
            self.editor_info_label.config(text=f"Loaded page {self.current_page + 1} - {len(text)} characters")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load page:\n{str(e)}")
    
    def editor_apply_changes(self):
        """Apply the edited text to the PDF"""
        if not self.pdf_document or not self.is_editing:
            return
        
        try:
            # Get edited text
            edited_text = self.editor_text.get(1.0, tk.END).rstrip()
            
            if edited_text == self.original_text:
                messagebox.showinfo("No Changes", "The text hasn't been modified.")
                return
            
            # Get current page
            page = self.pdf_document[self.current_page]
            
            # Get text blocks with their locations
            text_dict = page.get_text("dict")
            
            if not text_dict.get("blocks"):
                messagebox.showwarning("Error", "No text found on this page to edit.")
                return
            
            # Find all text blocks and cover them with white rectangles
            text_blocks = []
            for block in text_dict["blocks"]:
                if block["type"] == 0:  # Text block
                    text_blocks.append(fitz.Rect(block["bbox"]))
            
            if not text_blocks:
                messagebox.showwarning("Error", "No text found on this page to edit.")
                return
            
            # Cover all text blocks with white rectangles to hide old text
            for text_rect in text_blocks:
                # Draw a white filled rectangle to cover the text
                page.draw_rect(text_rect, color=None, fill=(1, 1, 1))
            
            # Insert the new edited text at the location of the first text block
            first_block_rect = text_blocks[0]
            page.insert_text(first_block_rect.tl, edited_text, 
                            fontname="helv", fontsize=11, color=(0, 0, 0))
            
            # Store as edited
            self.edited_pdf_path = self.current_pdf
            self.editor_info_label.config(text=f"Changes applied to page {self.current_page + 1} - Ready to save")
            messagebox.showinfo("Success", "Changes applied! Click 'Save PDF' to save.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply changes:\n{str(e)}")
    
    def editor_save_pdf(self):
        """Save the edited PDF"""
        if not self.pdf_document or not self.is_editing:
            messagebox.showwarning("Error", "No PDF is open for editing.")
            return
        
        try:
            # Ask user where to save
            output_file = filedialog.asksaveasfilename(
                title="Save edited PDF as",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=f"edited_{Path(self.current_pdf).stem}.pdf"
            )
            
            if not output_file:
                return
            
            # Save the modified PDF
            self.pdf_document.save(output_file)
            
            self.editor_info_label.config(text=f"Saved to: {Path(output_file).name}")
            messagebox.showinfo("Success", 
                               f"PDF saved successfully!\n\n"
                               f"Saved to: {Path(output_file).name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PDF:\n{str(e)}")


def main():
    """Main entry point for the application"""
    root = tk.Tk()
    app = PDFMergerReaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
