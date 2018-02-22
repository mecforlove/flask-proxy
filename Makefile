.PHONY: test format

test:
	python -m tests

format:
	yapf -irp tests
	yapf -irp flask_proxy