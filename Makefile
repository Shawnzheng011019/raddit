.PHONY: help install-frontend install-backend run-frontend run-backend run-all stop-all clean

help:
	@echo "Available commands:"
	@echo "  install-frontend  - Install frontend dependencies"
	@echo "  install-backend   - Install backend dependencies"
	@echo "  run-frontend      - Run frontend development server"
	@echo "  run-backend       - Run backend server"
	@echo "  run-all           - Run both frontend and backend"
	@echo "  stop-all          - Stop all services"
	@echo "  clean             - Clean build artifacts"

install-frontend:
	cd frontend && npm install

install-backend:
	cd backend && pip install -r requirements.txt

run-frontend:
	cd frontend && npm run dev

run-backend:
	cd backend && python scripts/init_db.py && uvicorn app.main:app --reload

run-all:
	@echo "Starting backend and frontend servers..."
	@cd backend && python scripts/init_db.py && uvicorn app.main:app --reload & cd ../frontend && npm run dev

stop-all:
	@pkill -f "uvicorn" || true
	@pkill -f "vite" || true

clean:
	rm -rf frontend/node_modules
	rm -rf backend/*.egg-info
	rm -rf backend/build
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +