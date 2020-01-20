# https://www.gnu.org/software/make/manual/html_node/Phony-Targets.html
.PHONY: clean clean-pyc help test
# https://www.gnu.org/software/make/manual/html_node/Special-Variables.html
.DEFAULT_GOAL := help

PYTHON_ROOTDIR?=src
PYTHON_SOURCES=$(shell find $(PYTHON_ROOTDIR) -type f -name '*.py')

IMG_EXPORT_DIR?=cats
URL_IMG?=cats.txt

PYTEST_OPTIONS?=

# https://github.com/AnyBlok/anyblok-book-examples/blob/III-06_polymorphism/Makefile
define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-30s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

all: image_downloader_aio

image_downloader_aio: clean-img		## download images with asynchronous version
	@python $(PYTHON_ROOTDIR)/async/image_downloader.py \
		$(URL_IMG) \
		--export_dir $(IMG_EXPORT_DIR)

image_downloader_mp: clean-img		## download images with multiprocessing version
	@python $(PYTHON_ROOTDIR)/multiprocessing/image_downloader.py \
		$(URL_IMG)

nodejs_install:		## install nodejs packages
	@/bin/bash -c "pushd src/nodejs; \
		npm install .; \
		npm ls --depth 0; \
		popd;"

nodejs_clean:	## remove node_modules
	@rm -rf src/nodejs/node_modules

nodejs_image_downloader: clean-img		## download images with node-js version
	@node src/nodejs/image_downloader.js

clean: clean-img clean-pyc ## remove all venv, build, coverage and Python artifacts

img-export-dir:	## create images export directory
	@mkdir -p $(IMG_EXPORT_DIR)

clean-img: img-export-dir ## remove images files
	find $(IMG_EXPORT_DIR) -name '*.jpg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts (*.pyc,*.pyo,*~,__pycache__)
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	find . -name '.pytest_cache' -exec rm -fr {} +
