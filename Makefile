.PHONY: run-server run-client mypy-server mypy-client

run-server:
	python src/battleship/server.py

run-server-large:
	ulimit -n 4096; python src/battleship/server.py

run-server-interop:
	ulimit -n 4096; python src/battleship/server.py -i 10.0.0.204 -p 8004

run-client:
	python src/battleship/client.py

run-client1:
	python src/battleship/client.py -l client1.log

run-client2:
	python src/battleship/client.py -l client2.log

run-client1-interop:
	python src/battleship/client.py -l client1.log -p 8004 -i 10.0.0.201

run-client2-interop:
	python src/battleship/client.py -l client2.log -p 8004 -i 10.0.0.201


mypy-server:
	cd src/battleship; mypy --fast-parser --strict-optional --check-untyped-defs --show-column-numbers --warn-no-return --python-version 3.6 server.py; cd ../../

mypy-client:
	cd src/battleship; mypy --fast-parser --strict-optional --check-untyped-defs --show-column-numbers --warn-no-return --python-version 3.6 --ignore-missing-imports client.py; cd ../../

