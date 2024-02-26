'''
Common set of fixtures used in the tests.
'''

import os
import shutil
import tempfile
from shutil import copy

import pytest

from directory_annotator_storage import create_app
from directory_annotator_storage.constants_config import ANNOT_PATH, DOC_PATH

# ROUTES
@pytest.fixture
def app():
    doc_path = tempfile.mkdtemp()
    annot_path = tempfile.mkdtemp()

    app = create_app({
        'TESTING': True,
        DOC_PATH: doc_path,
        ANNOT_PATH: annot_path
    })

    app.logger.debug(f"Created (temporary) fake document dir '{doc_path}'.")
    app.logger.debug(f"Created (temporary) fake annotation dir '{annot_path}'.")

    # Fake DB init: copy test resource data to temp. directories
    BASE_NAMES = [ "Didot_1842a-sample", "Didot_1848a-sample", "Didot_1851a-sample" ]
    BASE_PATH = os.path.join(os.path.dirname(__file__), 'resources')

    for bn in BASE_NAMES:
        # Documents
        src_file = os.path.join(BASE_PATH, "documents", bn + ".pdf")
        copy(src_file, app.config[DOC_PATH])
        # Annotations
        src_file = os.path.join(BASE_PATH, "annotations", bn + ".zip")
        copy(src_file, app.config[ANNOT_PATH])

    # with app.app_context():
    #     init_db()
    #     get_db().executescript(_data_sql)

    yield app

    shutil.rmtree(doc_path)
    shutil.rmtree(annot_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()


# BACKEND
@pytest.fixture
def annot_path():
    annot_path = tempfile.mkdtemp()
    try:
        yield annot_path
    finally:
        shutil.rmtree(annot_path)
