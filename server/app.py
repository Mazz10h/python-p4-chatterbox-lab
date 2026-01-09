from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)
db.init_app(app)

# Ensure tables exist
with app.app_context():
    db.create_all()


# -------------------- /messages route --------------------
@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'POST':
        data = request.get_json()
        if not data or "body" not in data or "username" not in data:
            return jsonify({"error": "Missing body or username"}), 400

        new_message = Message(body=data['body'], username=data['username'])
        db.session.add(new_message)
        db.session.commit()

        return jsonify({
            "id": new_message.id,
            "body": new_message.body,
            "username": new_message.username,
            "created_at": new_message.created_at.isoformat(),
            "updated_at": new_message.updated_at.isoformat()
        }), 201

    # GET all messages
    messages = Message.query.all()
    messages_list = [
        {
            "id": msg.id,
            "body": msg.body,
            "username": msg.username,
            "created_at": msg.created_at.isoformat(),
            "updated_at": msg.updated_at.isoformat()
        }
        for msg in messages
    ]
    return jsonify(messages_list), 200


# -------------------- /messages/<id> route --------------------
@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.get(id)
    if message is None:
        return jsonify({"error": "Message not found"}), 404

    # PATCH: update message body
    if request.method == 'PATCH':
        data = request.get_json()
        if not data or "body" not in data:
            return jsonify({"error": "Missing body"}), 400
        message.body = data["body"]
        db.session.commit()

    # DELETE: remove message
    if request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        return '', 204  # No Content

    # GET or after PATCH: return message JSON
    return jsonify({
        "id": message.id,
        "body": message.body,
        "username": message.username,
        "created_at": message.created_at.isoformat(),
        "updated_at": message.updated_at.isoformat()
    }), 200


# -------------------- Run app --------------------
if __name__ == '__main__':
    app.run(port=5555)
