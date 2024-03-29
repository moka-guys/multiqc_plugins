venv: venv/touchfile

venv/touchfile: requirements.txt
	test -d venv || python3 -m venv venv
	. venv/bin/activate; pip install -Ur requirements.txt
	touch venv/touchfile

test: venv
	. venv/bin/activate; nosetests project/test

clean:
	rm -rf venv
	find -iname "*.pyc" -delete
