import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.dependencies import get_db
from app.database import Base
from sqlalchemy_utils import database_exists, create_database, drop_database

url = "sqlite:///./test.db"
engine = create_engine(url, connect_args={"check_same_thread": False})


def get_test_db():
    SessionLocal = sessionmaker(bind=engine)
    test_db = SessionLocal()
    try:
        yield test_db
    finally:
        for tbl in reversed(Base.metadata.sorted_tables):
            engine.execute(tbl.delete())
        test_db.close()


@pytest.fixture()
def database_test_session():
    yield from get_test_db()


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    if database_exists(url):
        drop_database(url)
    create_database(url)
    Base.metadata.create_all(engine)
    app.dependency_overrides[get_db] = get_test_db
    yield
    drop_database(url)


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client
