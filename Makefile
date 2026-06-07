.PHONY: dev-api dev-web install test demo bench bench-fetch docker-api deploy-fly

install:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements-api.txt
	cd frontend && npm install

install-full:
	cd backend && . .venv/bin/activate && pip install -r requirements.txt greenlet

dev-api:
	cd backend && . .venv/bin/activate && cd .. && MPLBACKEND=Agg PYTHONPATH=. uvicorn app.main:app --reload --port 8000 --app-dir backend

dev-web:
	cd frontend && npm run dev

test:
	cd backend && . .venv/bin/activate && cd .. && PYTHONPATH=. python -c "from app.core.config import settings; assert settings.api_prefix"

bench-fetch:
	PYTHONPATH=. python -m pipeline.benchmarks.run --dataset pbmc3k --fetch --max-cells 800

bench:
	PYTHONPATH=. python -m pipeline.benchmarks.run --dataset all --fetch

bench-pbmc:
	PYTHONPATH=. python -m pipeline.benchmarks.run --dataset pbmc3k --fetch

docker-api:
	docker build -f Dockerfile.backend -t cce-api .
	docker run --rm -p 8000:8000 -v "$$(pwd)/data:/app/data" cce-api

deploy-fly:
	fly deploy

demo:
	curl -s -X POST http://127.0.0.1:8000/api/v1/jobs -F "data_file=@/dev/null;filename=demo.h5ad" -F "demo=true"
