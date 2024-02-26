from io import BytesIO
import os
import json
import tempfile
import zipfile
from pathlib import Path
from filelock import FileLock

from werkzeug.utils import safe_join

import directory_annotator_storage.path_utils as pu


class InvalidDocumentNameError(RuntimeError):
    pass

class AnnotationsNotFoundError(RuntimeError):
    pass

# Public members
# =============================================================================================


def load_annotations(annotation_directory: str, document_name: str, view: int) -> dict:
    """
    Load (maybe empty) annotations for a given view of a given document.

    Args:
        annotation_directory (str): Path to directory storing annotations
        document_name (str): Name of the document (e.g. "Didot_1851a.pdf")
        view (int): View of the document (e.g. `1` for the first page)

    Raises:
        InvalidDocumentNameError: If the document name is badly formed
        AnnotationsNotFoundError: If there is no annotation for this document/view.

    Returns:
        dict: Annotations for this particular view of the document. May be empty.
    """
    # Check for bad parameters
    if not(isinstance(document_name, str)) or len(document_name) == 0:
        raise InvalidDocumentNameError()

    # TODO check for existing document first?

    # Check archive exists
    zip_name = pu.get_stem_with_extension(document_name, "zip")
    zip_path = safe_join(annotation_directory, zip_name)
    if not os.path.exists(zip_path):
        raise AnnotationsNotFoundError()

    json_filename = f"{view:04}.json"
    annot_data = None
    with zipfile.ZipFile(zip_path) as zo:
        if json_filename not in zo.namelist():
            raise AnnotationsNotFoundError()
        with zo.open(json_filename) as json_file:
                annot_data = json.load(json_file)
                __data_filter_on_load(annot_data)
                json_file.close()  # FIXME do we need this?
        zo.close()  # FIXME do we need this?

    return annot_data



class SaveError(RuntimeError):
    '''
    Generic save error.
    '''
    def __init__(self, msg):
        super().__init__(msg)


def save_annotations(annotation_directory: str, document_name: str, view: int, data: dict):
    '''
    Tries to save the document in ZIP archive.
    The ZIP archive will contain files names like `0001.json` 
    where `0001` is the 0-padded, 4-digits number of the page.
    Any existing file inside the ZIP archive will be overwrote.

    Parameters
    ----------
    doc_content: (dict)
        DOM document content to be saved.

    filename: (str)
        Path to the target destination of the ZIP file.

    page_id: (int)
        Number of the page in the document.

    Returns
    -------
    None

    Exceptions
    ----------
    SaveError:
        When any save-related error is detected.
    '''
    
    def write_json_in_zip(json_data, zip_handle, file_name):
        json_data = __data_filter_on_save(json_data)
        json_bytes = json.dumps(json_data, ensure_ascii=False, indent=2)
        zip_handle.writestr(file_name, json_bytes)

    filename = safe_join(annotation_directory, pu.get_stem_with_extension(document_name, "zip"))

    zipPath = Path(filename)
    jsonName = f"{view:04}.json"
    lock = FileLock(filename + ".lock")
    with lock:
        if zipPath.exists():
            if not zipPath.is_file():
                raise SaveError(f"\"{zipPath}\" is not a file. Cannot save.")
            if not zipfile.is_zipfile(zipPath):
                raise SaveError(f"\"{zipPath}\" is not a valid zip file. Cannot save.")
        # else: we open/append the file and investigate further
        replace_json = False  # indicates whether replacing the json file is necessary
        with zipfile.ZipFile(zipPath, 'a') as zipObj:
            if jsonName in zipObj.namelist():
                replace_json = True
            else: # json file does not exist
                # since the file is open, we can add a new element
                write_json_in_zip(data, zipObj, jsonName)

        if replace_json:
            # Hack because we cannot remove/update a file in a ZIP file.
            opFile, tmpZip = tempfile.mkstemp(dir=os.path.dirname(zipPath))
            os.close(opFile)
            with zipfile.ZipFile(tmpZip, 'w') as zipOut:
                with zipfile.ZipFile(zipPath, 'r') as zipIn:
                    for f in zipIn.infolist():
                        if jsonName != f.filename:
                            data_tmp = zipIn.read(f.filename)
                            zipOut.writestr(f.filename, data_tmp)
                write_json_in_zip(data, zipOut, jsonName)
            os.remove(zipPath)
            os.rename(tmpZip, zipPath)

def get_document_annotations_as_zip_file(annotation_directory: str, document_name: str) -> BytesIO: # | None
    filename = safe_join(annotation_directory, pu.get_stem_with_extension(document_name, "zip"))
    io_zip = None
    if os.path.exists(filename):
        with open(filename, 'rb') as fh:
            io_zip = BytesIO(fh.read())
            io_zip.seek(0)  # be friendly, rewind
    return io_zip

# TODO add options to merge (with or without replacement)
def replace_document_annotations(annotation_directory: str, document_name: str, zip_data: bytes) -> None:
    filename = safe_join(annotation_directory, pu.get_stem_with_extension(document_name, "zip"))
    lock = FileLock(filename + ".lock")
    with lock:
        with open(filename, 'wb') as out_file:
            out_file.write(BytesIO(zip_data).getbuffer())


# Internal definitions
# =============================================================================================

def __data_filter_on_load(json_data):
    '''
    Transform annotation data after loading and before it is sent to the application.
    '''
    for x in json_data:
        if "type" in x and x["type"] in ["ENTRY", "TITLE_LEVEL_1", "TITLE_LEVEL_2"]:
            if x.get("origin") is None:
                x["origin"] = "computer"
            if x.get("checked") is None:
                x["checked"] = False

def __data_filter_on_save(doc_content):
    '''
    Transform annotation data before saving.
    '''
    return doc_content


