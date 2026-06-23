import pytest
import json
from app import create_app, db

@pytest.fixture
def client():
    """
    This is a pytest fixture - it sets up a fresh test environment
    before each test and cleans up after.
    We use a separate in-memory SQLite database for tests
    so we don't mess up our real data.
    """
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def test_health_check(client):
    """Test that health endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "healthy"


def test_create_link_success(client):
    """Test creating a valid link."""
    payload = {"original_url": "https://google.com", "title": "Google"}
    response = client.post("/links", json=payload)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert "short_code" in data
    assert data["original_url"] == "https://google.com"
    assert data["click_count"] == 0


def test_create_link_invalid_url(client):
    """Test that invalid URLs are rejected."""
    payload = {"original_url": "not-a-real-url"}
    response = client.post("/links", json=payload)
    assert response.status_code == 400


def test_create_link_missing_url(client):
    """Test that missing URL returns error."""
    response = client.post("/links", json={})
    assert response.status_code == 400


def test_create_link_custom_slug(client):
    """Test creating a link with a custom slug."""
    payload = {"original_url": "https://github.com", "custom_slug": "my-github"}
    response = client.post("/links", json=payload)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["short_code"] == "my-github"


def test_list_links(client):
    """Test listing all links."""
    client.post("/links", json={"original_url": "https://google.com"})
    client.post("/links", json={"original_url": "https://github.com"})
    response = client.get("/links")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["total"] == 2


def test_delete_link(client):
    """Test soft-deleting a link."""
    create_resp = client.post("/links", json={"original_url": "https://google.com"})
    link_id = json.loads(create_resp.data)["id"]
    delete_resp = client.delete(f"/links/{link_id}")
    assert delete_resp.status_code == 200
    list_resp = client.get("/links")
    assert json.loads(list_resp.data)["total"] == 0