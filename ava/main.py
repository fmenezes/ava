import uuid

from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy

from ava.inference import infere 

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydatabase.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Conversation(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    messages = db.relationship("Message", backref="conversation", lazy=True)


class Message(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.String(2000), nullable=False)
    conversation_id = db.Column(
        db.String(36), db.ForeignKey("conversation.id"), nullable=False
    )


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/conversations", methods=["POST"])
def create_conversation():
    new_conversation = Conversation()
    db.session.add(new_conversation)
    db.session.commit()
    return jsonify({"id": new_conversation.id}), 201


@app.route("/conversations/<id>", methods=["GET"])
def get_conversation(id):
    conversation = Conversation.query.get_or_404(id)
    return jsonify(
        {
            "id": conversation.id,
            "messages": [
                {"id": msg.id, "role": msg.role, "content": msg.content}
                for msg in conversation.messages
            ],
        }
    )


@app.route("/conversations/<id>/messages", methods=["POST"])
def add_message(id):
    conversation = Conversation.query.get_or_404(id)
    data = request.get_json()
    user_message = Message(
        role="user", content=data["content"], conversation_id=conversation.id
    )
    db.session.add(user_message)
    db.session.commit()

    bot_content = infere(data["content"])
    bot_message = Message(
        role="bot", content=bot_content, conversation_id=conversation.id
    )
    db.session.add(bot_message)
    db.session.commit()

    return (
        jsonify(
            [{
                "id": user_message.id,
                "role": user_message.role,
                "content": user_message.content,
            }, {
                "id": bot_message.id,
                "role": bot_message.role,
                "content": bot_message.content,
            }]
        ),
        201,
    )


def _main() -> None:
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8080)


if __name__ == "__main__":
    _main()
