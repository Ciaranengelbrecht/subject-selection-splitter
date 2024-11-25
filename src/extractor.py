"""
PDF Processing Script with GUI
Author: Ciaran Englebrecht & Josh Henry
Copyright (c) 2024 Prendiville Catholic College

Description:
This script extracts student names and numbers from each page of a PDF document,
uses OCR to recognize text, and saves each page as a separate PDF file named
according to the student's name and number in reverse order. After processing,
all individual PDFs are zipped into a single archive. The script features a
Graphical User Interface (GUI) built with Tkinter for enhanced user experience.

Dependencies:
- PyPDF2
- pdf2image
- pytesseract
- tqdm
- Pillow
- Tkinter
"""

import PyPDF2
from pdf2image import convert_from_path
import pytesseract
import os
import re
import sys
from tqdm import tqdm
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.ttk import Style
import zipfile
from pathlib import Path

class SubjectSelectionSplitter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Subject Selection PDF Splitter")
        self.root.configure(bg='#f0f0f0')
        self.setup_styles()
        self.setup_gui()
        
    def setup_styles(self):
        # Configure modern styles
        style = Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Modern.TFrame', background='#f0f0f0')
        style.configure('Modern.TButton',
                       padding=10,
                       background='#0066cc',
                       foreground='white',
                       font=('Helvetica', 11))
        style.configure('Modern.TLabel',
                       background='#f0f0f0',
                       font=('Helvetica', 11))
        style.configure('Modern.TEntry',
                       padding=5,
                       fieldbackground='white')
        style.configure('Modern.Horizontal.TProgressbar',
                       troughcolor='#f0f0f0',
                       background='#0066cc')
        
    def setup_gui(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="30", style='Modern.TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # File selection
        ttk.Label(main_frame, text="Select PDF File:", style='Modern.TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=(0,10))
        
        file_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0,20))
        
        self.file_path = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path, 
                             width=50, style='Modern.TEntry')
        file_entry.grid(row=0, column=0, padx=(0,10))
        
        browse_btn = ttk.Button(file_frame, text="Browse", 
                              command=self.browse_file, style='Modern.TButton')
        browse_btn.grid(row=0, column=1)
        
        # Year selection
        ttk.Label(main_frame, text="Year:", style='Modern.TLabel').grid(
            row=2, column=0, sticky=tk.W, pady=(0,10))
        
        current_year = datetime.now().year
        self.year = tk.StringVar(value=str(current_year))
        year_entry = ttk.Entry(main_frame, textvariable=self.year,
                             width=10, style='Modern.TEntry')
        year_entry.grid(row=3, column=0, sticky=tk.W, pady=(0,20))
        
        # Process button
        process_btn = ttk.Button(main_frame, text="Process PDF",
                               command=self.process_pdf, style='Modern.TButton')
        process_btn.grid(row=4, column=0, pady=(0,20))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, length=400,
                                      mode='determinate',
                                      style='Modern.Horizontal.TProgressbar')
        self.progress.grid(row=5, column=0, pady=(0,10))

    def browse_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf")]
        )
        if filename:
            self.file_path.set(filename)
            
    def extract_student_info(self, text):
        # Updated regex pattern to capture year level
        pattern = r'\[?(STU\d+)\]?\s*([^,]+),\s*([^(\n]+)(?:\s*\(([^)]+)\))?.*?(Yr\d+)'
        match = re.search(pattern, text)
        
        if match:
            student_id = match.group(1)
            lastname = match.group(2).strip()
            firstname = match.group(3).strip()
            year_level = match.group(5)
            return student_id, lastname, firstname, year_level
        return None, None, None, None
        
    def process_pdf(self):
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select a PDF file")
            return
            
        try:
            pdf_reader = PyPDF2.PdfReader(self.file_path.get())
            num_pages = len(pdf_reader.pages)
            
            # Create output directory
            output_dir = os.path.join(os.path.dirname(self.file_path.get()), "split_pdfs")
            os.makedirs(output_dir, exist_ok=True)
            
            self.progress['maximum'] = num_pages
            
            for page_num in range(num_pages):
                # Extract text from page
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                # Get student information
                student_id, lastname, firstname, year_level = self.extract_student_info(text)
                
                if all([student_id, lastname, firstname, year_level]):
                    # Create new PDF with single page
                    output_pdf = PyPDF2.PdfWriter()
                    output_pdf.add_page(page)
                    
                    # Updated filename format with underscore before year level
                    filename = f"{student_id}_{lastname}_{firstname}_{year_level}_{self.year.get()}_Subject_Selection.pdf"
                    filepath = os.path.join(output_dir, filename)
                    
                    # Save PDF
                    with open(filepath, 'wb') as output_file:
                        output_pdf.write(output_file)
                
                self.progress['value'] = page_num + 1
                self.root.update()
            
            zip_path = self.create_zip_archive(output_dir)
            messagebox.showinfo("Success", 
                f"Successfully processed {num_pages} pages\n"
                f"Output directory: {output_dir}\n"
                f"Zip file created: {zip_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.progress['value'] = 0

    def create_zip_archive(self, pdf_dir):
        # Get input PDF name without extension
        base_name = Path(self.file_path.get()).stem
        # Create zip file path
        zip_path = os.path.join(os.path.dirname(pdf_dir), f"{base_name}_split.zip")
        
        # Create zip file
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through directory and add files
            for root, dirs, files in os.walk(pdf_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, pdf_dir)
                    zipf.write(file_path, arcname)
        
        return zip_path
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SubjectSelectionSplitter()
    app.run()
