import pytest
from app import create_app
from models import db

@pytest.fixture
def client():
    app = create_app()
    app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI="sqlite:///:memory:", WTF_CSRF_ENABLED=False)
    with app.app_context():
        db.create_all()
    client = app.test_client()
    yield client
