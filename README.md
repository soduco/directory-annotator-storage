# directory-annotator-storage

Standalone server for annotation storage.

## 📦 INSTALL
Either from sources (`git clone`) or using a pre-packaged Python wheel from the [package repository](https://gitlab.lre.epita.fr/soduco/directory-annotator-storage/-/packages).

## 🔌 API REFERENCE

General route structure:
```
<scheme><host>:<port>/<prefix>/<route>
```

Example:
```
http://localhost:3000/directories/Didot_1842a.pdf/700/image
^      ^         ^    ^           ^
 \      \_ host   \    \_ prefix   \
  \_ scheme        \_ port          \_ route
```

### Available routes
| Route                               | Method | Description                                                                 | Result / Param                                 |
| ----------------------------------- | ------ | --------------------------------------------------------------------------- | ---------------------------------------------- |
| `<prefix>/`                         | GET    | List available documents                                                    | JSON result                                    |
| `<prefix>/<doc>`                    | GET    | List available views for document `<doc>`                                   | JSON result                                    |
| `<prefix>/<doc>/download_directory` | GET    | Download a compressed archive of all annotations for document `<doc>`       | ZIP file with JSON files inside                |
| `<prefix>/<doc>/replace_directory`  | PUT    | Upload a compressed archive to replace all annotations for document `<doc>` | ZIP file with JSON files inside (no multipart) |
| `<prefix>/<doc>/<view>/annotation`  | GET    | Read annotations for view `<view>` of document `<doc>`                      | JSON result                                    |
| `<prefix>/<doc>/<view>/annotation`  | PUT    | Update annotations for view `<view>` of document `<doc>`                    | JSON payload                                   |
| `<prefix>/<doc>/<view>/image`       | GET    | Read image for view `<view>` of document `<doc>`                            | binary result (JPEG image)                     |
| `<prefix>/health_check`             | GET    | Test whether the server replies (and which server it is).                   | Simple string                                  |

### Sample queries and details

**TODO (see separate API doc, show `curl` example for each)**

Upload/replace a local zip file for a complete directory using curl:
```
curl -X PUT -H "Authorization: 12345678" http://localhost:8010/soduco/directory-annotator/storage/directories/00-dataset_das22_test.pdf/replace_directory -T merged.zip
```

Test upload with:
```
curl -X GET -H "Authorization: 12345678" http://localhost:8010/soduco/directory-annotator/storage/directories/00-dataset_das22_test.pdf/6/annotation | jq -C '.["content"]' | less -R
```


## 🚀 DEPLOY USING DOCKER

### Get the sources and configure
1. Clone the repository.
2. If needed, edit the parameters (path to files, listen interface and port, etc.) in `docker/.env` (default values should be fine).
3. Rebuild and run the service using `docker-compose up --build` (from the `docker` directory).


### Frontend configuration
Make sure your configuration for the frontend is correct:
1. Update URL parameters for the "back" in your `~/.config/soduco_annot/general_config.ini` so it matches the scheme (`http` or `https`), hostname (e.g. `docker.lre.epita.fr`), port (e.g. `8001`) and prefix (e.g. `soduco/directory-annotator-storage`) defined in the `flaskenv` file.
2. Update the authentication token for the "back" according to the `.secret_keys` file used.


## 🔧 DEVELOP

### Run the server locally

1. Copy `settings_example.cfg` to some new file to store you new configuration:  
   ```shell
   cp settings_example.cfg settings.cfg
   # Then edit settings.cfg
   ```
2. Export the required environment variable to inform your server of its configuration file:  
   ```shell
   # Note that path must be absolute
   export SODUCO_SETTINGS=$(realpath settings.cfg)
   ```
3. Run the server using `tox` (checks all requirements are satisfied):  
   ```shell
   tox -e serve
   ```
   or  
   run the server directly (faster startup, requires a `poetry install`):  
   ```shell
   python -m flask run
   ```

### Prepare a development environment
Install [Python Poetry](https://python-poetry.org/), preferably using the `pipx` method or the direct method.
Then, create a new virtual environment with all required dependencies with
```shell
poetry install
```

### Summary of easy dev commands
| Action                       | Command        |
| ---------------------------- | -------------- |
| Run the tests                | `tox`          |
| Check code quality (linting) | `tox -e lint`  |
| Run server in dev. mode      | `tox -e serve` |


### Frontend configuration for development
Make sure your configuration for the frontend is correct:
1. Update URL parameters for the "back" in your `~/.config/soduco_annot/general_config.ini` so it matches the scheme (`http` or `https`), hostname (e.g. `docker.lre.epita.fr`), port (e.g. `8001`) and prefix (e.g. `soduco/directory-annotator-storage`) defined in the `.flaskenv` file.
2. Update the authentication token for the "back" to add the default debug token `12345678`.


## 🐛 🐞 🦗 🪳 Things to fix

Try to use a **better PDF library** to improve the support of weird image they can contain.
Some suggestions to try (all open source):
- https://github.com/mstamy2/PyPDF2 — current option, last commit: Jun. 2018, ☆: 3.9k, full Python
- https://github.com/pikepdf/pikepdf — last commit: this week, ☆: 800, requires C++ lib. qpdf
- https://github.com/pdfminer/pdfminer.six — last commit: last month, ☆: 3.2k
- https://github.com/pymupdf/PyMuPDF — last commit: this week, ☆: 1.3k, requires C++ lib/tool MuPDF
- (maybe later: http://pdfbox.apache.org/ Java tool with Python bindings, used in [Apache Tika](https://tika.apache.org/))


