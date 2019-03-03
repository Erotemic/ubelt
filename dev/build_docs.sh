pip install sphinx sphinx-autobuild
pip install sphinx-autobuild
pip install sphinx
pip install sphinxcontrib-napoleon -U

mkdir -p docs
cd docs
sphinx-quickstart

#sphinx-autobuild
#sphinx-autobuild ../ build/html/
RELEASE_VERSION=$(python -c "import setup; print(setup.version)")
DOC_VERSION=$(python -c "import setup; print(setup.version[:-3])")
sphinx-apidoc --force --full --maxdepth="2" --doc-author="Jon Crall" --doc-version="$DOC_VERSION" --doc-release="$RELEASE_VERSION" --output-dir="doc" 
#'--private',  # Include "_private" modules
#'--separate',  # Put documentation for each module on its own page


cd doc 
make html
