build-Bunq2YnabLayer:
	mkdir -p  $(ARTIFACTS_DIR)/python
	python -m pip install --implementation cp \
	 --platform manylinux2010_x86_64 \
	 --only-binary=:all: --upgrade \
	 --python 3.8 \
	 -r requirements.txt -t $(ARTIFACTS_DIR)/python
