from io import BytesIO
import zipfile
from directory_annotator_storage.constants_config import DEBUG_TOKEN

# HEALTH CHECK
def test_health_check(client):
    resp = client.get('/health_check/')
    assert resp.status_code == 200

# ANNOTATIONS
# TODO check annotation content from know test element (present, absent)
# TODO check invalid requests


# IMAGE
def test_get_last_valid_image(client):
    h = { 'Authorization': DEBUG_TOKEN }
    resp = client.get( '/directories/Didot_1842a-sample.pdf/4/image', headers = h)
    assert resp.status_code == 200
    assert len(resp.data) > 0

# def test_get_non_jpeg_image(client): #TODO: Sample a Pdf with all the different images type
#     h = { 'Authorization': DEBUG_TOKEN }
#     resp = client.get( '/directories/Didot_1842a-sample.pdf/1/image', headers = h)
#     assert resp.status_code == 200
#     assert len(resp.data) > 0

def test_get_rasterize_image(client):
    h = { 'Authorization': DEBUG_TOKEN }
    resp = client.get( '/directories/Didot_1842a-sample.pdf/1/image', headers = h)
    assert resp.status_code == 500 # TODO: On the long term should be fix to return code: 200
    assert len(resp.data) > 0

def test_get_unavailable_image(client):
    h = { 'Authorization': DEBUG_TOKEN }
    resp = client.get( '/directories/Didot_1842a-sample.pdf/10/image', headers = h)
    assert resp.status_code == 404

def test_get_unavailable_image_zero(client):
    h = { 'Authorization': DEBUG_TOKEN }
    resp = client.get( '/directories/Didot_1842a-sample.pdf/0/image', headers = h)
    assert resp.status_code == 404

def test_get_unavailable_image_negative(client):
    h = { 'Authorization': DEBUG_TOKEN }
    resp = client.get( '/directories/Didot_1842a-sample.pdf/-1/image', headers = h)
    assert resp.status_code == 404

def test_get_unavailable_image_unk_doc(client):
    h = { 'Authorization': DEBUG_TOKEN }
    resp = client.get( '/directories/unknown/10/image', headers = h)
    assert resp.status_code == 404

# DOWNLOAD / UPLOAD
def test_download_directory_unavail(client):
    h = { 'Authorization': DEBUG_TOKEN }
    resp = client.get( '/directories/unknown/download_directory', headers = h)
    assert resp.status_code == 404

def test_download_directory_avail(client):
    h = { 'Authorization': DEBUG_TOKEN }
    resp = client.get( '/directories/Didot_1842a-sample/download_directory', headers = h)
    assert resp.status_code == 200

    # TODO Check we have 1 file attached file in response?

    # Try to read file
    io_zip = BytesIO(resp.data)
    files_in_zip = None
    files_expected = set(["0003.json", "0004.json"])  # We know expected content
    with zipfile.ZipFile(io_zip, 'a') as zipObj:
        files_in_zip = set(zipObj.namelist())
    assert files_in_zip == files_expected
    
# Upload to new and existing
def test_upload_directory_new_then_existing(client):
    h_down = { 'Authorization': DEBUG_TOKEN }
    # get some valid content
    resp = client.get( '/directories/Didot_1842a-sample/download_directory', headers = h_down)
    assert resp.status_code == 200
    
    # Read file content
    io_zip = BytesIO(resp.data)

    # Make sure the new document does not exist yet
    new_doc_name = "newtestdir"
    resp2 = client.get(f'/directories/{new_doc_name}/download_directory', headers = h_down)
    assert resp2.status_code == 404

    # upload to new document
    h_up =  h_down.copy()
    h_up.update({ 'Content-type': 'application/zip' })

    resp3 = client.put(
        f'/directories/{new_doc_name}/replace_directory',
        headers = h_up, 
        data=io_zip.read()
        )
    assert resp3.status_code == 200

    # try to read again
    resp4 = client.get(f'/directories/{new_doc_name}/download_directory', headers = h_down)
    assert resp4.status_code == 200

    # check content
    io_zip = BytesIO(resp4.data)
    files_in_zip = None
    files_expected = set(["0003.json", "0004.json"])  # We know expected content
    with zipfile.ZipFile(io_zip, 'a') as zipObj:
        files_in_zip = set(zipObj.namelist())
    assert files_in_zip == files_expected

    # put some extra content which will be removed
    resp5 = client.put(
        '/directories/{new_doc_name}/10/annotation',
        headers = h_down,
        json={"content": {"test": "extra_data"}})
    assert resp5.status_code == 200

    # upload again and overwrite
    resp6 = client.put(
        f'/directories/{new_doc_name}/replace_directory',
        headers = h_up, 
        data=io_zip.read()
        )
    assert resp6.status_code == 200

    # try to read again
    resp7 = client.get(f'/directories/{new_doc_name}/download_directory', headers = h_down)
    assert resp7.status_code == 200

    # check content
    io_zip = BytesIO(resp7.data)
    files_in_zip = None
    with zipfile.ZipFile(io_zip, 'a') as zipObj:
        files_in_zip = set(zipObj.namelist())
    assert files_in_zip == files_expected

