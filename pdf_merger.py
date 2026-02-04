#!/usr/bin/env python3
"""
PDF Merger - A desktop application for combining multiple PDF files
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import sys

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("Error: pypdf library not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf", "--break-system-packages"])
    from pypdf import PdfReader, PdfWriter


class PDFMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Merger")
        self.root.geometry("700x550")
        self.root.resizable(True, True)
        
        # List to store PDF file paths in order
        self.pdf_files = []
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="PDF Merger", 
                               font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                                text="Add PDF files below, arrange them in order, then merge",
                                font=("Helvetica", 10))
        instructions.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Listbox with scrollbar to show added PDFs
        list_frame = ttk.Frame(main_frame)
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
        self.file_count_label = ttk.Label(main_frame, text="No files added")
        self.file_count_label.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(0, 10))
        
        # Add files button
        self.add_button = ttk.Button(button_frame, text="Add PDF Files", 
                                     command=self.add_files)
        self.add_button.grid(row=0, column=0, padx=5)
        
        # Remove selected button
        self.remove_button = ttk.Button(button_frame, text="Remove Selected", 
                                        command=self.remove_selected, state=tk.DISABLED)
        self.remove_button.grid(row=0, column=1, padx=5)
        
        # Move up button
        self.move_up_button = ttk.Button(button_frame, text="↑ Move Up", 
                                         command=self.move_up, state=tk.DISABLED)
        self.move_up_button.grid(row=0, column=2, padx=5)
        
        # Move down button
        self.move_down_button = ttk.Button(button_frame, text="↓ Move Down", 
                                           command=self.move_down, state=tk.DISABLED)
        self.move_down_button.grid(row=0, column=3, padx=5)
        
        # Clear all button
        self.clear_button = ttk.Button(button_frame, text="Clear All", 
                                       command=self.clear_all, state=tk.DISABLED)
        self.clear_button.grid(row=0, column=4, padx=5)
        
        # Merge button (larger and prominent)
        self.merge_button = ttk.Button(main_frame, text="Merge PDFs", 
                                       command=self.merge_pdfs, state=tk.DISABLED)
        self.merge_button.grid(row=5, column=0, columnspan=2, pady=10, ipadx=20, ipady=5)
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Ready", 
                                     relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Bind listbox selection event
        self.file_listbox.bind('<<ListboxSelect>>', self.on_select)
        
    def add_files(self):
        """Open file dialog to add PDF files"""
        files = filedialog.askopenfilenames(
            title="Select PDF files",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if files:
            added_count = 0
            for file_path in files:
                # Validate it's actually a PDF
                if self.validate_pdf(file_path):
                    self.pdf_files.append(file_path)
                    filename = Path(file_path).name
                    self.file_listbox.insert(tk.END, filename)
                    added_count += 1
                else:
                    messagebox.showwarning("Invalid File", 
                                          f"Skipped: {Path(file_path).name}\n(Not a valid PDF)")
            
            self.update_ui_state()
            if added_count > 0:
                self.status_label.config(text=f"Added {added_count} file(s)")
    
    def validate_pdf(self, file_path):
        """Validate that the file is a readable PDF"""
        try:
            reader = PdfReader(file_path)
            # Check if it has at least one page
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
            self.update_ui_state()
            self.status_label.config(text="File removed")
    
    def move_up(self):
        """Move selected file up in the list"""
        selection = self.file_listbox.curselection()
        if selection and selection[0] > 0:
            index = selection[0]
            # Swap in list
            self.pdf_files[index], self.pdf_files[index-1] = \
                self.pdf_files[index-1], self.pdf_files[index]
            # Update listbox
            item = self.file_listbox.get(index)
            self.file_listbox.delete(index)
            self.file_listbox.insert(index-1, item)
            self.file_listbox.selection_set(index-1)
            self.status_label.config(text="File moved up")
    
    def move_down(self):
        """Move selected file down in the list"""
        selection = self.file_listbox.curselection()
        if selection and selection[0] < len(self.pdf_files) - 1:
            index = selection[0]
            # Swap in list
            self.pdf_files[index], self.pdf_files[index+1] = \
                self.pdf_files[index+1], self.pdf_files[index]
            # Update listbox
            item = self.file_listbox.get(index)
            self.file_listbox.delete(index)
            self.file_listbox.insert(index+1, item)
            self.file_listbox.selection_set(index+1)
            self.status_label.config(text="File moved down")
    
    def clear_all(self):
        """Clear all files from the list"""
        if messagebox.askyesno("Clear All", "Remove all files from the list?"):
            self.file_listbox.delete(0, tk.END)
            self.pdf_files.clear()
            self.update_ui_state()
            self.status_label.config(text="All files removed")
    
    def on_select(self, event):
        """Handle listbox selection change"""
        self.update_ui_state()
    
    def update_ui_state(self):
        """Update button states and file count based on current state"""
        num_files = len(self.pdf_files)
        selection = self.file_listbox.curselection()
        
        # Update file count
        if num_files == 0:
            self.file_count_label.config(text="No files added")
        elif num_files == 1:
            self.file_count_label.config(text="1 file added")
        else:
            self.file_count_label.config(text=f"{num_files} files added")
        
        # Enable/disable buttons
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
        
        # Ask where to save the merged file
        output_file = filedialog.asksaveasfilename(
            title="Save merged PDF as",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="merged.pdf"
        )
        
        if not output_file:
            return  # User cancelled
        
        try:
            self.status_label.config(text="Merging PDFs...")
            self.root.update()
            
            # Create PDF writer
            writer = PdfWriter()
            total_pages = 0
            
            # Add all pages from all PDFs
            for pdf_file in self.pdf_files:
                reader = PdfReader(pdf_file)
                for page in reader.pages:
                    writer.add_page(page)
                    total_pages += 1
            
            # Write to output file
            with open(output_file, "wb") as output:
                writer.write(output)
            
            self.status_label.config(text=f"Success! Merged {len(self.pdf_files)} files ({total_pages} pages)")
            messagebox.showinfo("Success", 
                               f"PDFs merged successfully!\n\n"
                               f"Files merged: {len(self.pdf_files)}\n"
                               f"Total pages: {total_pages}\n\n"
                               f"Saved to: {Path(output_file).name}")
            
        except Exception as e:
            self.status_label.config(text="Error during merge")
            messagebox.showerror("Error", f"Failed to merge PDFs:\n{str(e)}")


def main():
    """Main entry point for the application"""
    root = tk.Tk()
    app = PDFMergerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
