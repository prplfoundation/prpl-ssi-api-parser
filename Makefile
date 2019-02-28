install:
	pip3 install -r requirements.txt
	brew update
	brew install graphviz

test:
	nose2 -v

package: clean
	pipreqs . --force

clean:
	-rm -f -r .idea
	-find . -name *.pyc -exec rm -f {} \;
	-find . -name __pycache__ -exec rm -f -r {} \;
	-rm -f parser.log
	-rm -f -r specs/generated/*

run:
	python3 launcher.py
