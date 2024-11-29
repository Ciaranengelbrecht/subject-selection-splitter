"""
PDF Processing Script with GUI
Author: Ciaran Englebrecht
Copyright (c) 2024 

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
from PIL import Image, ImageDraw
import io
from PyPDF2 import PdfReader, PdfWriter
import json
from PIL import ImageTk

class CalibrationTool:
    def __init__(self, pdf_path):
        self.root = tk.Toplevel()
        self.root.title("Column Blanking Calibration")
        
        # Create main container
        self.container = ttk.Frame(self.root, padding="10")
        self.container.pack(fill='both', expand=True)
        
        # Info label at top
        self.info_label = ttk.Label(
            self.container, 
            text="Click and drag to select regions to blank out",
            font=('Helvetica', 11)
        )
        self.info_label.pack(pady=(0, 10))
        
        # Convert PDF page to image
        images = convert_from_path(pdf_path)
        self.original_image = images[0]
        
        # Resize for display
        width = min(800, self.original_image.width)
        height = int(width * self.original_image.height / self.original_image.width)
        self.display_image = self.original_image.resize((width, height))
        
        # Canvas for image and selection
        self.canvas = tk.Canvas(
            self.container,
            width=width,
            height=height,
            bg='white'
        )
        self.canvas.pack(pady=10)
        
        # Display image
        self.photo = ImageTk.PhotoImage(self.display_image)
        self.canvas.create_image(0, 0, anchor='nw', image=self.photo)
        
        # Button frame
        btn_frame = ttk.Frame(self.container)
        btn_frame.pack(fill='x', pady=10)
        
        # Style for buttons
        style = ttk.Style()
        style.configure('Action.TButton', padding=5)
        
        # Control buttons
        self.preview_btn = ttk.Button(
            btn_frame,
            text="Preview",
            command=self.preview_blanking,
            style='Action.TButton'
        )
        self.preview_btn.pack(side='left', padx=5)
        
        self.save_btn = ttk.Button(
            btn_frame,
            text="Save Regions",
            command=self.save_regions,
            style='Action.TButton'
        )
        self.save_btn.pack(side='left', padx=5)
        
        self.reset_btn = ttk.Button(
            btn_frame,
            text="Reset",
            command=self.reset_regions,
            style='Action.TButton'
        )
        self.reset_btn.pack(side='left', padx=5)
        
        # Selection variables
        self.regions = []
        self.current_rectangle = None
        self.start_x = None
        self.start_y = None
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.start_selection)
        self.canvas.bind('<B1-Motion>', self.update_selection)
        self.canvas.bind('<ButtonRelease-1>', self.end_selection)
    
    def start_selection(self, event):
        self.start_x = event.x
        self.start_y = event.y
        
    def update_selection(self, event):
        if self.current_rectangle:
            self.canvas.delete(self.current_rectangle)
        self.current_rectangle = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
            outline='red', width=2
        )
    
    def end_selection(self, event):
        if self.start_x is not None:
            # Convert coordinates to percentages
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            x1 = min(self.start_x, event.x) / width
            y1 = min(self.start_y, event.y) / height
            x2 = max(self.start_x, event.x) / width
            y2 = max(self.start_y, event.y) / height
            
            self.regions.append({
                'x1': x1, 'y1': y1,
                'x2': x2, 'y2': y2
            })
            
            self.info_label.config(
                text=f"Selected {len(self.regions)} regions. Click Save when done."
            )
    
    def preview_blanking(self):
        if not self.regions:
            messagebox.showwarning("Warning", "No regions selected")
            return
            
        preview = self.original_image.copy()
        draw = ImageDraw.Draw(preview)
        
        width, height = preview.size
        for region in self.regions:
            x1 = int(region['x1'] * width)
            y1 = int(region['y1'] * height)
            x2 = int(region['x2'] * width)
            y2 = int(region['y2'] * height)
            draw.rectangle([x1, y1, x2, y2], fill='white')
        
        # Show preview
        preview.show()
    
    def save_regions(self):
        if not self.regions:
            messagebox.showwarning("Warning", "No regions selected")
            return
            
        config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'blanking_regions.json'
        )
        
        with open(config_path, 'w') as f:
            json.dump(self.regions, f)
        
        messagebox.showinfo(
            "Success",
            f"Saved {len(self.regions)} regions to configuration file"
        )
        self.root.destroy()
    
    def reset_regions(self):
        self.regions = []
        self.canvas.delete('all')
        self.canvas.create_image(0, 0, anchor='nw', image=self.photo)
        self.info_label.config(text="Click and drag to select regions")

# Modify blank_columns function to use saved regions
def blank_columns(image):
    """Blank out regions based on saved configuration"""
    draw = ImageDraw.Draw(image)
    width, height = image.size
    
    try:
        with open('blanking_regions.json', 'r') as f:
            regions = json.load(f)
            
        for region in regions:
            x1 = int(region['x1'] * width)
            y1 = int(region['y1'] * height)
            x2 = int(region['x2'] * width)
            y2 = int(region['y2'] * height)
            draw.rectangle([x1, y1, x2, y2], fill='white')
    except FileNotFoundError:
        print("No blanking regions configured")
    
    return image

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
        
        # Add calibration button
        calibrate_btn = ttk.Button(
            main_frame, 
            text="Configure Blanking Regions",
            command=self.launch_calibration,
            style='Modern.TButton'
        )
        calibrate_btn.grid(row=6, column=0, pady=(0,10))

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

    def blank_columns(self, image):
        """Blank out regions based on saved configuration"""
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        try:
            with open('blanking_regions.json', 'r') as f:
                regions = json.load(f)
                
            for region in regions:
                x1 = int(region['x1'] * width)
                y1 = int(region['y1'] * height)
                x2 = int(region['x2'] * width)
                y2 = int(region['y2'] * height)
                draw.rectangle([x1, y1, x2, y2], fill='white')
        except FileNotFoundError:
            print("No blanking regions configured")
        
        return image

    def process_single_pdf(self, input_path, output_path):
        """Process single page PDF and blank columns"""
        # Convert PDF to images
        images = convert_from_path(input_path)
        
        # Process first/only page
        modified_image = self.blank_columns(images[0])
        
        # Convert back to PDF
        img_byte_arr = io.BytesIO()
        modified_image.save(img_byte_arr, format='PDF')
        img_byte_arr.seek(0)
        
        return img_byte_arr

    def process_pdf(self):
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select a PDF file")
            return
            
        try:
            pdf_reader = PyPDF2.PdfReader(self.file_path.get())
            num_pages = len(pdf_reader.pages)
            
            output_dir = os.path.join(os.path.dirname(self.file_path.get()), "split_pdfs")
            os.makedirs(output_dir, exist_ok=True)
            
            self.progress['maximum'] = num_pages
            
            for page_num in range(num_pages):
                # Create temporary single page PDF
                temp_writer = PdfWriter()
                temp_writer.add_page(pdf_reader.pages[page_num])
                temp_path = os.path.join(output_dir, f"temp_{page_num}.pdf")
                
                with open(temp_path, 'wb') as temp_file:
                    temp_writer.write(temp_file)
                
                # Process and modify page
                modified_pdf_bytes = self.process_single_pdf(temp_path, None)
                
                # Extract student info from original page
                text = pdf_reader.pages[page_num].extract_text()
                student_id, lastname, firstname, year_level = self.extract_student_info(text)
                
                if all([student_id, lastname, firstname, year_level]):
                    # Create new PDF with single page
                    output_pdf = PyPDF2.PdfWriter()
                    output_pdf.add_page(page)
                    
                    # Updated filename format with underscore before year level
                    filename = f"{student_id}_{lastname}_{firstname}_{year_level}_{self.year.get()} Subjects.pdf"
                    filepath = os.path.join(output_dir, filename)
                    
                    with open(filepath, 'wb') as output_file:
                        output_file.write(modified_pdf_bytes.getvalue())
                
                # Clean up temp file
                os.remove(temp_path)
                
                self.progress['value'] = page_num + 1
                self.root.update()
            
            # Create zip archive
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
    
    def launch_calibration(self):
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select a PDF file first")
            return
        
        CalibrationTool(self.file_path.get())
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SubjectSelectionSplitter()
    app.run()
