all: test
	# readme
	make -C _building
	make -C docs html

.PHONY: test
test:
	sudo env "PATH=$$PATH" UT_DEBUG=0 PYTHONPATH="$$(cd ..; pwd)" python -m unittest discover -c --failfast -s .

