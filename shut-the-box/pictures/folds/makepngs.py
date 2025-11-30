import pymupdf
import os
from pathlib import Path

def pdf2pngs(pdf_file_name, file_prepend, png_dir_name, _dpi, _jpg_quality):
    if not os.path.exists(pdf_file_name):
        print(f"File {pdf_file_name} does not exist, skipping")
        return

    doc = pymupdf.open(pdf_file_name)
    for pageno, page in enumerate(doc):
        page_pix = page.get_pixmap(dpi = _dpi)
        
        basename = f"{file_prepend}_{pageno:03d}.png"
        png_file_name = os.path.join(png_dir_name, basename)
        try:
            page_pix.save(png_file_name, jpg_quality = _jpg_quality)
        except Exception as e:
            print(f"Unexpected error while saving {png_file_name}: {e}")

def PDFs2pngs(pdf_file_names, pngs_dir_name, _dpi, _jpg_quality):
    if not os.path.exists(pngs_dir_name):
        try:
            os.mkdir(pngs_dir_name)
        except Exception as e:
            print(f"Unexpected error while trying to make directory '{png_dir_name}': {e}")
                
    for pdfno, pdf_file_name in enumerate(pdf_file_names):
        print(f'{pdfno:02d}/{len(pdf_file_names)-1:02d}')        
        file_prepend = Path(pdf_file_name).stem
        pdf2pngs(pdf_file_name, file_prepend, pngs_dir_name, _dpi, _jpg_quality)
        
def doFolds():
    num_pdfs = 17
    pngs_dir_name = 'frames'
    pdf_file_names = [f'TeX/fold{i}.pdf' for i in range(num_pdfs+1)]
    dpi = 200 #dots per inch
    jpg_quality = 70 # 98 is near lossless
    PDFs2pngs(pdf_file_names, pngs_dir_name, dpi, jpg_quality)    

if __name__ == '__main__':
    pdf2pngs('TeX/complete-box.pdf', 'box-complete', 'frames', 200, 85)


    
