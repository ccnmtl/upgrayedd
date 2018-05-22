OUTPUT_PATH=ve
VE ?= ./ve
FLAKE8 ?= $(VE)/bin/flake8
REQUIREMENTS ?= requirements.txt
SYS_PYTHON ?= python
PIP ?= $(VE)/bin/pip
PY_SENTINAL ?= $(VE)/sentinal
WHEEL_VERSION ?= 0.30.0
VIRTUALENV ?= virtualenv.py
SUPPORT_DIR ?= requirements/virtualenv_support/
MAX_COMPLEXITY ?= 7
INTERFACE ?= localhost
RUNSERVER_PORT ?= 8000
PY_DIRS ?= .

all: flake8

clean:
	rm -rf $(OUTPUT_PATH)

$(PY_SENTINAL):
	rm -rf $(VE)
	$(SYS_PYTHON) $(VIRTUALENV) --extra-search-dir=$(SUPPORT_DIR) $(VE)
	$(PIP) install wheel==$(WHEEL_VERSION)
	$(PIP) install --no-deps --requirement $(REQUIREMENTS)
	touch $@

flake8: $(PY_SENTINAL)
	$(FLAKE8) $(PY_DIRS) --exclude ve,virtualenv.py,sandbox
