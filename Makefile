.PHONY: run-server run-client mypy-server mypy-client

run-server:
	python src/battleship/server.py

run-client:
	python src/battleship/client.py

mypy-server:
	cd src/battleship; mypy --fast-parser --strict-optional --check-untyped-defs --show-column-numbers --warn-no-return --python-version 3.6 server.py; cd ../../

mypy-client:
	cd src/battleship; mypy --fast-parser --strict-optional --check-untyped-defs --show-column-numbers --warn-no-return --python-version 3.6 client.py; cd ../../
