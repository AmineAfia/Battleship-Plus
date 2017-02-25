.PHONY: run-server run-client mypy-server mypy-client

run-server:
	python3 src/battleship/server.py

run-client:
	python3 src/battleship/client.py

run-client1:
	python3 src/battleship/client.py -l client1.log

run-client2:
	python3 src/battleship/client.py -l client2.log

run-client1:
	python src/battleship/client.py -l client1.log

run-client2:
	python src/battleship/client.py -l client2.log

mypy-server:
	cd src/battleship; mypy --fast-parser --strict-optional --check-untyped-defs --show-column-numbers --warn-no-return --python-version 3.6 server.py; cd ../../

mypy-client:
	cd src/battleship; mypy --fast-parser --strict-optional --check-untyped-defs --show-column-numbers --warn-no-return --python-version 3.6 --ignore-missing-imports client.py; cd ../../
