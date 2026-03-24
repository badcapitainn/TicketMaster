"""
TicketMaster API — Integration Tests
Run: pytest tests/ -v  (from the backend/ directory with venv activated)
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# ── In-memory SQLite for tests ────────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite:///./test_ticketmaster.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True, scope="function")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


# ── Helpers ───────────────────────────────────────────────────────────────────

def register(username, email, password, role="standard_user"):
    return client.post("/api/auth/register", json={
        "username": username, "email": email, "password": password, "role": role
    })


def login(email, password):
    return client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


def auth_headers(email, password):
    resp = login(email, password)
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ── Auth Tests ────────────────────────────────────────────────────────────────

class TestAuth:
    def test_register_success(self):
        resp = register("alice", "alice@example.com", "secret123")
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "alice@example.com"
        assert data["role"] == "standard_user"
        assert "password_hash" not in data

    def test_register_duplicate_email(self):
        register("alice", "alice@example.com", "secret123")
        resp = register("alice2", "alice@example.com", "other")
        assert resp.status_code == 400

    def test_register_duplicate_username(self):
        register("alice", "alice@example.com", "secret123")
        resp = register("alice", "other@example.com", "other")
        assert resp.status_code == 400

    def test_login_success(self):
        register("alice", "alice@example.com", "secret123")
        resp = login("alice@example.com", "secret123")
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self):
        register("alice", "alice@example.com", "secret123")
        resp = login("alice@example.com", "wrongpassword")
        assert resp.status_code == 401

    def test_login_unknown_email(self):
        resp = login("nobody@example.com", "pass")
        assert resp.status_code == 401


# ── Ticket Tests ──────────────────────────────────────────────────────────────

class TestTickets:
    def setup_method(self):
        register("alice", "alice@example.com", "secret123")
        register("bob", "bob@example.com", "secret123", role="agent")
        register("admin", "admin@example.com", "secret123", role="admin")
        self.alice_headers = auth_headers("alice@example.com", "secret123")
        self.bob_headers = auth_headers("bob@example.com", "secret123")
        self.admin_headers = auth_headers("admin@example.com", "secret123")

    def _create_ticket(self, headers=None, priority="High"):
        headers = headers or self.alice_headers
        return client.post("/api/tickets", json={
            "title": "Printer broken",
            "description": "The printer on floor 2 is not working.",
            "priority": priority,
        }, headers=headers)

    def test_create_ticket(self):
        resp = self._create_ticket()
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Printer broken"
        assert data["status"] == "Open"
        assert data["priority"] == "High"

    def test_create_ticket_unauthenticated(self):
        resp = client.post("/api/tickets", json={"title": "X", "description": "Y"})
        assert resp.status_code == 401

    def test_list_tickets(self):
        self._create_ticket()
        self._create_ticket()
        resp = client.get("/api/tickets", headers=self.alice_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert len(data["tickets"]) == 2

    def test_list_tickets_filter_by_status(self):
        self._create_ticket()
        resp = client.get("/api/tickets?status=Open", headers=self.alice_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    def test_list_tickets_filter_by_priority(self):
        self._create_ticket(priority="High")
        self._create_ticket(priority="Low")
        resp = client.get("/api/tickets?priority=High", headers=self.alice_headers)
        assert resp.json()["total"] == 1

    def test_get_ticket(self):
        created = self._create_ticket().json()
        resp = client.get(f"/api/tickets/{created['id']}", headers=self.alice_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == created["id"]

    def test_get_ticket_not_found(self):
        resp = client.get("/api/tickets/9999", headers=self.alice_headers)
        assert resp.status_code == 404

    def test_standard_user_update_own_ticket_status(self):
        created = self._create_ticket().json()
        resp = client.patch(
            f"/api/tickets/{created['id']}",
            json={"status": "Pending"},
            headers=self.alice_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "Pending"

    def test_standard_user_cannot_update_others_ticket(self):
        created = self._create_ticket(headers=self.bob_headers).json()
        resp = client.patch(
            f"/api/tickets/{created['id']}",
            json={"status": "Closed"},
            headers=self.alice_headers,
        )
        assert resp.status_code == 403

    def test_standard_user_cannot_change_priority(self):
        created = self._create_ticket().json()
        resp = client.patch(
            f"/api/tickets/{created['id']}",
            json={"priority": "Critical"},
            headers=self.alice_headers,
        )
        assert resp.status_code == 403

    def test_agent_can_update_any_ticket(self):
        created = self._create_ticket().json()
        resp = client.patch(
            f"/api/tickets/{created['id']}",
            json={"status": "Resolved", "priority": "Low"},
            headers=self.bob_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "Resolved"
        assert data["priority"] == "Low"

    def test_delete_ticket_admin_only(self):
        created = self._create_ticket().json()
        # alice (standard_user) cannot delete
        resp = client.delete(f"/api/tickets/{created['id']}", headers=self.alice_headers)
        assert resp.status_code == 403
        # admin can delete
        resp = client.delete(f"/api/tickets/{created['id']}", headers=self.admin_headers)
        assert resp.status_code == 200

    def test_ticket_history_recorded_on_update(self):
        created = self._create_ticket().json()
        client.patch(
            f"/api/tickets/{created['id']}",
            json={"status": "Pending"},
            headers=self.alice_headers,
        )
        resp = client.get(f"/api/tickets/{created['id']}/history", headers=self.alice_headers)
        assert resp.status_code == 200
        history = resp.json()
        assert len(history) >= 1
        assert history[0]["field_name"] == "status"
        assert history[0]["old_value"] == "Status.open"
        assert history[0]["new_value"] == "Status.pending"

    def test_add_and_list_comments(self):
        created = self._create_ticket().json()
        client.post(
            f"/api/tickets/{created['id']}/comments",
            json={"body": "Working on it!"},
            headers=self.bob_headers,
        )
        resp = client.get(f"/api/tickets/{created['id']}/comments", headers=self.alice_headers)
        assert resp.status_code == 200
        comments = resp.json()
        assert len(comments) == 1
        assert comments[0]["body"] == "Working on it!"


# ── User Tests ────────────────────────────────────────────────────────────────

class TestUsers:
    def setup_method(self):
        register("alice", "alice@example.com", "secret123")
        register("admin", "admin@example.com", "secret123", role="admin")
        self.alice_headers = auth_headers("alice@example.com", "secret123")
        self.admin_headers = auth_headers("admin@example.com", "secret123")

    def test_get_me(self):
        resp = client.get("/api/users/me", headers=self.alice_headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "alice@example.com"

    def test_list_users_authenticated(self):
        resp = client.get("/api/users", headers=self.alice_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 2

    def test_change_role(self):
        # Get alice's id
        alice = client.get("/api/users/me", headers=self.alice_headers).json()
        resp = client.patch(
            f"/api/users/{alice['id']}/role",
            json={"role": "agent"},
            headers=self.admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "agent"

    def test_deactivate_user(self):
        alice = client.get("/api/users/me", headers=self.alice_headers).json()
        resp = client.patch(f"/api/users/{alice['id']}/deactivate", headers=self.admin_headers)
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False
        # Deactivated user cannot login
        resp = login("alice@example.com", "secret123")
        assert resp.status_code == 403


# ── Stats Tests ───────────────────────────────────────────────────────────────

class TestStats:
    def setup_method(self):
        register("alice", "alice@example.com", "secret123")
        register("admin", "admin@example.com", "secret123", role="admin")
        self.alice_headers = auth_headers("alice@example.com", "secret123")
        self.admin_headers = auth_headers("admin@example.com", "secret123")

    def test_stats_admin_only(self):
        resp = client.get("/api/stats", headers=self.alice_headers)
        assert resp.status_code == 403

    def test_stats_returns_counts(self):
        client.post("/api/tickets", json={
            "title": "T1", "description": "D1", "priority": "High"
        }, headers=self.alice_headers)
        resp = client.get("/api/stats", headers=self.admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_tickets"] == 1
        assert "by_status" in data
        assert "by_priority" in data
        assert data["by_status"]["Open"] == 1
        assert data["by_priority"]["High"] == 1
