
# Constants to access application configuration items, and their descriptions

# ENVIRONMENT VARIABLES
#######################################################################

# Name of the environment variable pointing to the settings file.
SODUCO_SETTINGS = "SODUCO_SETTINGS"


# DEFINED IN THE CONFIGURATION FILE
#######################################################################

# app.config[DOC_PATH]: str
# Path to the directory which contains the original documents (PDF files of "directories").
DOC_PATH = "SODUCO_DIRECTORIES_PATH"

# app.config[ANNOT_PATH]: str
# Path to the directory which contains the annotations for each document (cheap DB).
ANNOT_PATH = "SODUCO_ANNOTATIONS_PATH"

# app.config[SECRET_KEY_PATH]: str
# Path to the file contaning secret auth tokens (cheap auth).
SECRET_KEY_PATH = "SODUCO_PATH_SECRET_KEY"

# DEFINED INTERNALLY 
#######################################################################

# app.config[TOKENS]: List[str]
# Each element is a valid auth token to use the app.
# Defined by reading a secret token file upon app initialization.
TOKENS = "TOKENS"

# OTHER CONSTANTS
#######################################################################

# Default token to add to authorized authentication tokens when debug is active.
DEBUG_TOKEN = "12345678"
