.PHONY: dev-api dev-web install test demo

install:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements-api.txt
	cd frontend && npm install

dev-api:
	cd backend && . .venv/bin/activate && cd .. && MPLBACKEND=Agg PYTHONPATH=. uvicorn app.main:app --reload --port 8000 --app-dir backend

dev-web:
	cd frontend && npm run dev

test:
	cd backend && . .venv/bin/activate && cd .. && PYTHONPATH=. python -c "from pipeline.runner import run_pipeline; import tempfile; r=run_pipeline('t','/dev/null',None,tempfile.mkdtemp(),demo_mode=True); assert r['communication_edges']"

demo:
	curl -s -X POST http://127.0.0.1:8000/api/v1/jobs -F "data_file=@/dev/null;filename=demo.h5ad" -F "demo=true"
