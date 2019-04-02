install:
	apt-get update
	apt-get -y install python3 python3-pip python3-nose2
	pip3 install -r requirements.txt

test:
	nose2

clean:
	rm -f -r .idea
	find -type f -name *.pyc -exec rm -f {} \;
	find -type d -name __pycache__ -exec rm -f -r {} \;
	rm -f parser.log
	rm -f -r specs/generated/*

run:
	python3 launcher.py
