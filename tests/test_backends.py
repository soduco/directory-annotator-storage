import zipfile
from directory_annotator_storage.backend_annotations import (
    load_annotations, save_annotations, get_document_annotations_as_zip_file, 
    replace_document_annotations)

def test_save_load_roundtrip(annot_path):
    data = {"a": 1, "b": 1.5, "c": "éàœß🚀" }
    doc_name = "testdoc.pdf"

    save_annotations(annot_path, doc_name, 1, data)
    data2 = load_annotations(annot_path, doc_name, 1)
    assert data == data2

def test_save_twice_load_roundtrip(annot_path):
    data = {"a": 1, "b": 1.5, "c": "éàœß🚀" }
    doc_name = "testdoc.pdf"

    save_annotations(annot_path, doc_name, 1, data)
    data2 = load_annotations(annot_path, doc_name, 1)
    assert data == data2
    save_annotations(annot_path, doc_name, 1, data)
    data2 = load_annotations(annot_path, doc_name, 1)
    assert data == data2


def test_save_empty_pages_before(annot_path):
    data = {"a": 1, "b": 1.5, "c": "éàœß🚀" }
    data3 = {"a": 1, "b": 1.5, "c": "updated" }
    doc_name = "testdoc.pdf"

    save_annotations(annot_path, doc_name, 1, {})
    save_annotations(annot_path, doc_name, 2, data)
    data2 = load_annotations(annot_path, doc_name, 2)
    assert data == data2
    save_annotations(annot_path, doc_name, 2, data3)
    data4 = load_annotations(annot_path, doc_name, 2)
    assert data3 == data4

def test_download_zipfile(annot_path):
    data = {"a": 1, "b": 1.5, "c": "éàœß🚀" }
    doc1_name = "testdoc1.pdf"
    views = [1, 2, 10]
    for v in views:
        save_annotations(annot_path, doc1_name, v, data)
    data_zip = get_document_annotations_as_zip_file(annot_path, doc1_name)
    files_in_zip = None
    files_expected = set([f"{view:04}.json" for view in views])
    with zipfile.ZipFile(data_zip, 'a') as zipObj:
        files_in_zip = set(zipObj.namelist())
    assert files_in_zip == files_expected
    
def test_download_upload_zipfile(annot_path):
    data = {"a": 1, "b": 1.5, "c": "éàœß🚀" }
    doc1_name = "testdoc1.pdf"
    views = [1, 2, 10]
    for v in views:
        save_annotations(annot_path, doc1_name, v, data)
    data_zip = get_document_annotations_as_zip_file(annot_path, doc1_name)
    # Add extra view
    save_annotations(annot_path, doc1_name, 20, data)
    # data_zip.seek(0)  # we do not want to do this for the first use
    replace_document_annotations(annot_path, doc1_name, data_zip.read())
    data_zip2 = get_document_annotations_as_zip_file(annot_path, doc1_name)
    files_in_zip2 = None
    files_expected = set([f"{view:04}.json" for view in views])
    with zipfile.ZipFile(data_zip2, 'a') as zipObj:
        files_in_zip2 = set(zipObj.namelist())
    assert files_in_zip2 == files_expected

    # Try to save a second time elsewhere
    doc2_name = "testdoc1.pdf"
    data_zip.seek(0)
    replace_document_annotations(annot_path, doc2_name, data_zip.read())
    data_zip3 = get_document_annotations_as_zip_file(annot_path, doc2_name)
    files_in_zip3 = None
    files_expected = set([f"{view:04}.json" for view in views])
    with zipfile.ZipFile(data_zip3, 'a') as zipObj:
        files_in_zip3 = set(zipObj.namelist())
    assert files_in_zip3 == files_expected

