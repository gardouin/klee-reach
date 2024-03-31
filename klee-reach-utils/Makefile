all: install

build: clean
	python3 setup.py sdist
	python3 setup.py bdist_wheel
	python3 setup.py build

install: build
	pip install .

uninstall:
	pip3 uninstall kreachdist

clean:
	rm -rf build
	rm -rf dist
	rm -rf kreachdist.egg-info
