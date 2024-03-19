init:
	rye sync
	python -m modal setup
	. .venv/bin/activate

lint:
	rye run ruff check .

af:
	rye run ruff format .

run:
	uvicorn src.generation_scaling.main:app --reload

serve:
	modal serve src/generation_scaling/main.py
