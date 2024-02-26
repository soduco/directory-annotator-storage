import codecs
import json
from io import BytesIO

from flask import Blueprint, request, jsonify, send_file, abort, current_app

from directory_annotator_storage.backend_annotations import (
    AnnotationsNotFoundError, InvalidDocumentNameError, SaveError, get_document_annotations_as_zip_file, load_annotations, replace_document_annotations, save_annotations)
from directory_annotator_storage.backend_documents import (
    DocumentNotFoundError, DocumentReadError, InvalidViewIndexError, document_list, get_document_pages, get_image_from_view)
from directory_annotator_storage.constants_config import (TOKENS, DOC_PATH, ANNOT_PATH)
import directory_annotator_storage.path_utils as pu

bp = Blueprint('directories', __name__, url_prefix='/directories')
bp.config = {}

@bp.before_request
def before_request_func():
    if request.method == "OPTIONS":
        return
    request_token = request.headers.get('Authorization')
    #if Authorization header not defined, request_token = None
    if request_token not in bp.config[TOKENS]:
        abort(403, "Invalid request token.")

@bp.record
def record_config(setup_state):
    bp.config = setup_state.app.config

# ROUTES
#######################################################################
@bp.route('/', methods=['GET'])
def show_all_directories():
    list_doc = document_list(bp.config[DOC_PATH])
    directories = { pu.get_stem_with_extension(d, 'pdf'): {} for d in list_doc }
    res_dict = { "directories":  directories }
    return jsonify(res_dict)

@bp.route('/<document>', methods=['GET'])
def get_directory(document):
    document_path = pu.get_stem_with_extension(document, "pdf")
    pages = None
    try:
        pages = get_document_pages(bp.config[DOC_PATH], document_path)
    except DocumentReadError:
        abort(500, description="Error reading document.")
    except DocumentNotFoundError:
        abort(404, "Document not found.")
    result = {
        "num_pages": pages,
        "filename": document_path
    }
    return jsonify(result)

@bp.route('/<document>/<int:view>/annotation', methods=['GET', 'PUT'])
def access_annotation(document, view):
    '''
    Access the annotation of a view of a document.
    -----------
    Parameters
    ----------
    document: (str)
        name of the document (e.g. `"Didot_1851a.pdf"`)

    view : (Integer)
        id of the view in the pdf (1-indexed)

    Methods
    -------
    GET|PUT

    Action
    ------
    download: (None|'0'|'1')
    '''
    if request.method == 'GET':
        download = turn_to_bool(request.args.get('download'))
        content = None
        try:
            content = load_annotations(bp.config[ANNOT_PATH], document, view)
        except AnnotationsNotFoundError:
            abort(404, f"No annotation available for view '{view}' of document '{document}'.")
        except InvalidDocumentNameError:
            abort(400, f"Invalid document name '{document}'.")
        
        if download:
            buf = BytesIO()
            buf.write(codecs.encode(json.dumps(content)))
            return send_file(buf, as_attachment=True, mimetype='text/plain')
        else:
            return jsonify({ "content": content })

    elif request.method == 'PUT':
        json_data = request.get_json(force=True)
        # we use `force=True` to tolerate PUT requests with 'Content-Type' header different from 'application/json'
        
        if json_data is None or not isinstance(json_data, dict):
            current_app.logger.info("Could not parse JSON payload")
            return "Could not parse JSON payload.", 500
        content = json_data['content']
        if not isinstance(content, list):
            current_app.logger.info("Content is not a list, but a %s", type(content))
        try:
            save_annotations(bp.config[ANNOT_PATH], document, view, content)
        except SaveError:
            return "Error saving the content", 500
        return "Content saved on the server", 200


@bp.route('/<document>/<int:view>/image', methods=['GET'])
def get_image(document, view):
    try:
        image_data = get_image_from_view(bp.config[DOC_PATH], document, view)
    except DocumentReadError:
        return "Error reading the document", 500
    except DocumentNotFoundError:
        abort(404, "Document not found.")
    except InvalidViewIndexError:
        abort(404, "View is not available.")
    except NotImplementedError:
        abort(500, "Image need to be rasterize")
    data = BytesIO(image_data)
    return send_file(data, mimetype='image/jpeg')


@bp.route('/<directory>/download_directory', methods=['GET'])
def download_directory(directory):
    data = get_document_annotations_as_zip_file(bp.config[ANNOT_PATH], directory)
    if data is None:
        abort(404, f"zip file of {directory} not found")
    return send_file(data, as_attachment=True, download_name=f"{directory}.zip", mimetype="application/zip")


# TODO add options to merge (with or without replacement)
@bp.route('/<directory>/replace_directory', methods=['PUT'])
def replace_directory(directory):
    zip_data = request.data
    replace_document_annotations(bp.config[ANNOT_PATH], directory, zip_data)
    return "Content saved on the server", 200



# HELPERS
#######################################################################

def turn_to_bool(action):
    if not action or action == '0':
        return False
    if action == '1':
        return True
    abort(400, "bad request. Download can be only 0 or 1!")
