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
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        # List to store PDF file paths for merger
        self.pdf_files = []
        
        # PDF Reader state
        self.current_pdf = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_level = 1.0
        self.pdf_document = None  # PyMuPDF document object
        
        # Current view ('merger' or 'reader')
        self.current_view = 'merger'
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the user interface"""
        # Main container with side menu
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Content area (left side)
        self.content_frame = ttk.Frame(container)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Side menu (right side)
        self.setup_side_menu(container)
        
        # Setup initial views (hidden by default)
        self.setup_merger_view()
        self.setup_reader_view()
        
        # Show merger view by default
        self.show_view('merger')
        
    def setup_side_menu(self, parent):
        """Create the vertical side menu"""
        menu_frame = ttk.Frame(parent, relief=tk.RAISED, borderwidth=2)
        menu_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
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
        
        # Zoom controls
        ttk.Label(toolbar, text="Zoom:").pack(side=tk.LEFT, padx=(20, 5))
        zoom_out_btn = ttk.Button(toolbar, text="-", command=self.zoom_out, width=3)
        zoom_out_btn.pack(side=tk.LEFT, padx=2)
        
        self.zoom_label = ttk.Label(toolbar, text="100%", width=6)
        self.zoom_label.pack(side=tk.LEFT, padx=2)
        
        zoom_in_btn = ttk.Button(toolbar, text="+", command=self.zoom_in, width=3)
        zoom_in_btn.pack(side=tk.LEFT, padx=2)
        
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
        
        # Navigation controls
        nav_frame = ttk.Frame(self.reader_frame)
        nav_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        self.prev_btn = ttk.Button(nav_frame, text="← Previous", 
                                   command=self.prev_page, state=tk.DISABLED)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.page_entry = ttk.Entry(nav_frame, width=8, justify=tk.CENTER)
        self.page_entry.pack(side=tk.LEFT, padx=5)
        self.page_entry.bind('<Return>', self.goto_page)
        
        self.next_btn = ttk.Button(nav_frame, text="Next →", 
                                   command=self.next_page, state=tk.DISABLED)
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        # Reader status bar
        self.reader_status_label = ttk.Label(self.reader_frame, text="Open a PDF to begin", 
                                            relief=tk.SUNKEN, anchor=tk.W)
        self.reader_status_label.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
    def show_view(self, view_name):
        """Switch between merger and reader views"""
        # Hide all views
        self.merger_frame.pack_forget()
        self.reader_frame.pack_forget()
        
        # Show requested view
        if view_name == 'merger':
            self.merger_frame.pack(fill=tk.BOTH, expand=True)
            self.current_view = 'merger'
            self.merger_btn.state(['pressed'])
            self.reader_btn.state(['!pressed'])
        elif view_name == 'reader':
            self.reader_frame.pack(fill=tk.BOTH, expand=True)
            self.current_view = 'reader'
            self.reader_btn.state(['pressed'])
            self.merger_btn.state(['!pressed'])
    
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
            self.render_page()
            self.update_reader_navigation()
            
            filename = Path(file_path).name
            self.reader_status_label.config(text=f"Opened: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF:\n{str(e)}")
    
    def render_page(self):
        """Render the current page to the canvas"""
        if not self.pdf_document or self.current_page >= self.total_pages:
            return
        
        try:
            # Get the page
            page = self.pdf_document[self.current_page]
            
            # Render page to pixmap with zoom
            mat = fitz.Matrix(self.zoom_level, self.zoom_level)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Convert to PhotoImage
            self.current_image = ImageTk.PhotoImage(img)
            
            # Clear canvas and display image
            self.pdf_canvas.delete("all")
            self.pdf_canvas.create_image(0, 0, anchor=tk.NW, image=self.current_image)
            
            # Update canvas scrollregion
            self.pdf_canvas.config(scrollregion=(0, 0, pix.width, pix.height))
            
        except Exception as e:
            messagebox.showerror("Rendering Error", f"Failed to render page:\n{str(e)}")
    
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.render_page()
            self.update_reader_navigation()
    
    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.render_page()
            self.update_reader_navigation()
    
    def goto_page(self, event=None):
        """Go to specific page number"""
        try:
            page_num = int(self.page_entry.get()) - 1  # Convert to 0-indexed
            if 0 <= page_num < self.total_pages:
                self.current_page = page_num
                self.render_page()
                self.update_reader_navigation()
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
            self.render_page()
    
    def zoom_out(self):
        """Decrease zoom level"""
        if self.zoom_level > 0.4:
            self.zoom_level -= 0.2
            self.update_zoom_label()
            self.render_page()
    
    def update_zoom_label(self):
        """Update the zoom percentage label"""
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.pdf_canvas.yview_scroll(-1 * (event.delta // 120), "units")
    
    def update_reader_navigation(self):
        """Update navigation controls and page info"""
        if self.total_pages > 0:
            # Update page entry
            self.page_entry.delete(0, tk.END)
            self.page_entry.insert(0, str(self.current_page + 1))
            
            # Update page info
            self.page_info_label.config(text=f"Page {self.current_page + 1} of {self.total_pages}")
            
            # Update navigation buttons
            self.prev_btn.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
            self.next_btn.config(state=tk.NORMAL if self.current_page < self.total_pages - 1 else tk.DISABLED)
        else:
            self.page_info_label.config(text="No PDF loaded")
            self.prev_btn.config(state=tk.DISABLED)
            self.next_btn.config(state=tk.DISABLED)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """PDF Merger & Reader
        
Version 2.0

Features:
• Merge multiple PDFs into one
• Read and view PDF files
• Zoom and navigate pages
• User-friendly interface

Created with Python, tkinter, pypdf, and PyMuPDF"""
        
        messagebox.showinfo("About", about_text)


def main():
    """Main entry point for the application"""
    root = tk.Tk()
    app = PDFMergerReaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
