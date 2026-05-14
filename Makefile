.PHONY: test user-stories reproduce run

run:
	python twilio_phone_server.py

user-stories:
	pytest tests/user_stories/test_ordering_stories.py --junitxml=reports/user_stories.xml -v

test:
	pytest tests --junitxml=reports/user_stories.xml --cov=src --cov-report=xml:reports/coverage.xml --cov-report=html:reports/coverage_html -v

reproduce:
	python -m src.build_vector_store
	pytest tests --junitxml=reports/user_stories.xml --cov=src --cov-report=xml:reports/coverage.xml --cov-report=html:reports/coverage_html -v