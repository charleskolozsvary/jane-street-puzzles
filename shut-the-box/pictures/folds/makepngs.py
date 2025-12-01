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

def doFolds(num_pdfs, pngs_dir_name, prefix_file_name, dpi, jpg_quality):
    pdf_file_names = [f'TeX/{prefix_file_name}fold{i}.pdf' for i in range(num_pdfs+1)]
    PDFs2pngs(pdf_file_names, pngs_dir_name, dpi, jpg_quality)

if __name__ == '__main__':
    # doFolds(12, 'frames', 'example-net-', 275, 60)
    # doFolds(17, 'frames', 'full-net-', 275, 55)

    doFolds(12, 'frames', 'static-example-net-', 350, 95)
    doFolds(17, 'frames', 'static-full-net-', 350, 95)


    
