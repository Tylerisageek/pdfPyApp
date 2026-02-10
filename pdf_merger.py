#!/usr/bin/env python3
"""
PDF Merger & Reader - A desktop application for merging and reading PDF files
Created and maintained by
Ty Kemple
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import sys
import io
import fitz

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
        self.page_images = []  # Keep references for tkinter
        self.two_up = False  # two-page side-by-side mode
        self.facing_cover_right = tk.BooleanVar(value=False)

        # UI Setup
        self.setup_main_ui()
        
    ## ======== UI SETUP FUNCTIONS ==========

    def setup_main_ui(self):
        """Create the main UI with sidebar and content areas"""
        # Main container with horizontal layout
        main_container = ttk.Frame(self.root)
        main_container.grid(row=0, column=0, sticky="WENS")
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(0, weight=1)
        
        # Content area
        self.content_frame = ttk.Frame(main_container)
        self.content_frame.grid(row=0, column=0, sticky="WENS")
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)
        
        # Create two main views
        self.setup_merger_view()
        self.setup_reader_view()
        
        # Create side menu
        self.setup_side_menu(main_container)
        
        # Show merger view by default
        self.show_view('merger')
    
    ## Side menu
    def setup_side_menu(self, parent):
        menu_frame = ttk.Frame(parent, relief=tk.RAISED, borderwidth=2)
        menu_frame.grid(row=0, column=1, sticky="NS", padx=(10, 0))
        
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
        
        ttk.Separator(menu_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5, pady=10)
        
        # About button
        about_btn = ttk.Button(menu_frame, text="ℹ About", 
                              command=self.show_about,
                              width=15)
        about_btn.pack(pady=5, padx=10, side=tk.BOTTOM)
    
    ## Merger View
    def setup_merger_view(self):
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
        list_frame.grid(row=2, column=0, columnspan=2, sticky="WENS", pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky="NS")
        
        self.file_listbox = tk.Listbox(list_frame, 
                                       yscrollcommand=scrollbar.set,
                                       height=12,
                                       selectmode=tk.SINGLE)
        self.file_listbox.grid(row=0, column=0, sticky="WENS")
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
        self.merger_status_label.grid(row=6, column=0, columnspan=2, sticky="WE")
        
        # Bind listbox selection event
        self.file_listbox.bind('<<ListboxSelect>>', self.on_select)
    
    ## Reader View
    def setup_reader_view(self):
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
        toolbar.grid(row=1, column=0, columnspan=3, pady=(0, 10), sticky="WE")
        
        # Open PDF button
        open_btn = ttk.Button(toolbar, text="Open PDF", command=self.open_pdf)
        open_btn.pack(side=tk.LEFT, padx=5)
        
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
        display_frame.grid(row=2, column=0, columnspan=3, sticky="WENS")
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        
        # Create canvas with scrollbars
        v_scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL)
        v_scrollbar.grid(row=0, column=1, sticky="NS")
        
        h_scrollbar = ttk.Scrollbar(display_frame, orient=tk.HORIZONTAL)
        h_scrollbar.grid(row=1, column=0, sticky="WE")
        
        self.pdf_canvas = tk.Canvas(display_frame, 
                                    bg='gray85',
                                    xscrollcommand=h_scrollbar.set,
                                    yscrollcommand=v_scrollbar.set)
        self.pdf_canvas.grid(row=0, column=0, sticky="WENS")
        
        v_scrollbar.config(command=self.pdf_canvas.yview)
        h_scrollbar.config(command=self.pdf_canvas.xview)
        
        ## Bind keys
        self.pdf_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.root.bind_all("<Up>", self._on_key_up)
        self.root.bind_all("<Down>", self._on_key_down)
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
        self.reader_status_label.grid(row=4, column=0, columnspan=3, sticky="WE")
    
    ## Change Views
    def show_view(self, view_name):

        self.merger_frame.grid_forget()
        self.reader_frame.grid_forget()
        
        # Show requested view
        if view_name == 'merger':
            self.merger_frame.grid(row=0, column=0, sticky="WENS")
            self.current_view = 'merger'
            self.merger_btn.state(['pressed'])
            self.reader_btn.state(['!pressed'])
        elif view_name == 'reader':
            self.reader_frame.grid(row=0, column=0, sticky="WENS")
            self.current_view = 'reader'
            self.reader_btn.state(['pressed'])
            self.merger_btn.state(['!pressed'])
    
    # ========== MERGER FUNCTIONS ==========
    
    ## Open file dialog to add PDF files
    def add_files(self):
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
        try:
            reader = PdfReader(file_path)
            return len(reader.pages) > 0
        except Exception:
            return False
    
    def remove_selected(self):
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            self.file_listbox.delete(index)
            del self.pdf_files[index]
            self.update_merger_ui_state()
            self.merger_status_label.config(text="File removed")
    
    def move_file(self, direction):
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            self.pdf_files[index], self.pdf_files[index+direction] = \
                self.pdf_files[index+direction], self.pdf_files[index]
            item = self.file_listbox.get(index)
            self.file_listbox.delete(index)
            self.file_listbox.insert(index+direction, item)
            self.file_listbox.selection_set(index+direction)
            self.merger_status_label.config(text=f"File moved {'up' if direction == -1 else 'down'}")

    def move_up(self):
        self.move_file(-1)
    
    def move_down(self):
        self.move_file(1)
    
    def clear_all(self):
        if messagebox.askyesno("Clear All", "Remove all files from the list?"):
            self.file_listbox.delete(0, tk.END)
            self.pdf_files.clear()
            self.update_merger_ui_state()
            self.merger_status_label.config(text="All files removed")
    
    ## listbox selection change handler to update button states
    def on_select(self, event):
        self.update_merger_ui_state()
    
    ## Update button states and file count label based on current list state
    def update_merger_ui_state(self):
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
    
    ## Merge the PDFs in the list into a single file
    def merge_pdfs(self):
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
                else: # Fallback: approximate 
                    y_position = page_num * 300
                    self.pdf_canvas.yview_moveto(y_position / (self.total_pages * 300))
                self.goto_page_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Invalid Page", 
                                      f"Please enter a page number between 1 and {self.total_pages}")
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid page number")
    
    def zoom_in(self):
        if self.zoom_level < 3.0:
            self.zoom_level += 0.2
            self.update_zoom_label()
            self.render_all_pages()
    
    def zoom_out(self):
        if self.zoom_level > 0.4:
            self.zoom_level -= 0.2
            self.update_zoom_label()
            self.render_all_pages()
    
    def update_zoom_label(self):
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
    
    def _on_mousewheel(self, event):
        self.pdf_canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def _on_key_up(self, event):
        try:
            self.pdf_canvas.yview_scroll(-3, "units") # Scroll Up
        except Exception:
            pass

    def _on_key_down(self, event):
        try:
            self.pdf_canvas.yview_scroll(3, "units") # Scroll Down
        except Exception:
            pass

    def _on_page_butn_handler(self, event, direction):
        """Handle PageUp/PageDown keys"""
        if (self.two_up):
            direction *= 2

        try:
            # If we have page positions, jump exactly one page
            if hasattr(self, 'page_positions') and self.page_positions:
                y = self.page_positions[self.current_page + direction]
                frac = y / float(getattr(self, 'total_render_height', max(y, 1)))
                self.pdf_canvas.yview_moveto(frac)
            else:
                self.pdf_canvas.yview_scroll(-25, "units") # Fallback: scroll a larger amount than standard
        except Exception:
            pass

    def _on_page_up(self, event):
        """Handle PageUp key - scroll up by a larger amount"""
        self._on_page_butn_handler(event, direction= -1) # Previous Page

    def _on_page_down(self, event):
        self._on_page_butn_handler(event, direction= 1) # Next Page

    def _on_home(self, event):
        try:
            self.pdf_canvas.yview_moveto(0.0) # Scroll to top
        except Exception:
            pass

    def _on_end(self, event):
        try:
            self.pdf_canvas.yview_moveto(1.0) # Scroll to bottom
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

    """Toggle facing-page (book-style) mode. Enabling facing will turn on two-up view."""
    def toggle_facing_mode(self):  
        try:
            facing = bool(self.facing_cover_right.get())
            if facing and not getattr(self, 'two_up', False):
                self.two_up = True
                self.two_up_btn.config(text="Single")
            self.render_all_pages()
        except Exception:
            pass

    def show_about(self):
        about_text = """PDF Merger & Reader
            PDF Merger for combining multiple PDF files into one document. 
            PDF Reader for viewing and navigating PDF files.

            Created with Python, tkinter, pypdf, and PyMuPDF"""
        
        messagebox.showinfo("About", about_text)

def main():
    """Main entry point for the application"""
    root = tk.Tk()
    app = PDFMergerReaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
