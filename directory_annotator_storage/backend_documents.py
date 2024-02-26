import glob
import os
from pikepdf import Pdf, PdfImage

from io import BytesIO

from werkzeug.utils import safe_join


def document_list(documents_dir: str) -> list:
    list_doc = sorted(glob.glob(os.path.join(documents_dir, '*.pdf')))
    return list_doc


class DocumentReadError(RuntimeError):
    pass

class DocumentNotFoundError(RuntimeError):
    pass

class InvalidViewIndexError(RuntimeError):
    pass

def get_document_pages(documents_dir: str, document_name: str) -> int:
    document_path = safe_join(documents_dir, document_name)
    if not os.path.exists(document_path):
        raise DocumentNotFoundError()

    try:
        pdf_file = Pdf.open(document_path)
        pages = len(pdf_file.pages)
        return pages
    except RuntimeError:
        raise DocumentReadError()

def _need_rasterization(page) -> bool:
    # The minimal size of a pdf page
    MIN_WIDTH, MIN_HEIGHT = (512, 512)

    nb_whole_page_image = 0
    for image_id in page.images:
        image = PdfImage(page.images[image_id])
        if (image.width > MIN_WIDTH and image.height > MIN_HEIGHT):
            nb_whole_page_image += 1

    return nb_whole_page_image != 1

def get_image_from_view(documents_dir: str, document_name: str, view: int) -> bytes:
    # IMPORTANT: views are 1-indexed in parameter, and translated to 0-indexing here
    document_path = safe_join(documents_dir, document_name)
    if not os.path.exists(document_path):
        raise DocumentNotFoundError()

    image_data = None
    try:
        pdf_file = Pdf.open(document_path)
        num_pages = len(pdf_file.pages)
        if not 1 <= view <= num_pages:
            raise InvalidViewIndexError()
        page = pdf_file.pages[view - 1]

        if (_need_rasterization(page)):
            raise NotImplementedError # TODO

        for image in page.images:
            pdf_image = PdfImage(page.images[image])
            pil_image = pdf_image.as_pil_image()

            img_byte_arr = BytesIO()
            pil_image.save(img_byte_arr, format='PNG')
            image_data = img_byte_arr.getvalue()
            break
    except InvalidViewIndexError:
        raise
    except NotImplementedError:
        raise
    except RuntimeError:
        raise DocumentReadError()

    return image_data
