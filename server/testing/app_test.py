import pytest
from server.app import app, db, Message  # relative import
from datetime import datetime

# -------------------- Fixture: seed DB before every test --------------------
@pytest.fixture(autouse=True)
def seed_db():
    """Drops all tables, creates them, and seeds one default message"""
    with app.app_context():
        db.drop_all()
        db.create_all()

        default_message = Message(body="Hello 👋", username="Liza")
        db.session.add(default_message)
        db.session.commit()

        yield  # run the test

        db.session.remove()
        db.drop_all()


class TestApp:

    def test_has_correct_columns(self):
        with app.app_context():
            message = Message.query.first()
            assert message.body == "Hello 👋"
            assert message.username == "Liza"
            assert isinstance(message.created_at, datetime)

    def test_returns_list_of_json_objects_for_all_messages_in_database(self):
        with app.app_context():
            response = app.test_client().get("/messages")
            records = Message.query.all()
            for message in response.json:
                assert message["id"] in [r.id for r in records]
                assert message["body"] in [r.body for r in records]

    def test_creates_new_message_in_the_database(self):
        with app.app_context():
            client = app.test_client()
            client.post("/messages", json={"body": "Test", "username": "Tester"})
            msg = Message.query.filter_by(body="Test").first()
            assert msg is not None

    def test_updates_body_of_message_in_database(self):
        with app.app_context():
            client = app.test_client()
            message = Message.query.first()
            message_id = message.id

            client.patch(f"/messages/{message_id}", json={"body": "Updated 👋"})

            updated_message = Message.query.get(message_id)
            assert updated_message.body == "Updated 👋"

    def test_returns_data_for_updated_message_as_json(self):
        with app.app_context():
            client = app.test_client()
            message = Message.query.first()
            message_id = message.id

            response = client.patch(f"/messages/{message_id}", json={"body": "Updated 👋"})
            assert response.json["body"] == "Updated 👋"

    def test_deletes_message_from_database(self):
        with app.app_context():
            client = app.test_client()
            message = Message.query.first()
            message_id = message.id

            client.delete(f"/messages/{message_id}")
            assert Message.query.get(message_id) is None
