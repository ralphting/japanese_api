import os
import random

from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kanji.db'
db = SQLAlchemy(app)

class Kanji(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kanji = db.Column(db.String, unique=True, nullable=False)
    kunyomi = db.Column(db.String, nullable=False)
    onyomi = db.Column(db.String, nullable=False)
    meaning = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

# with app.app_context():
#     db.create_all()

@app.route('/')
def home():
    return "Japanese Kanji"

@app.route('/random', methods=["GET"])
def random_kanji():
    if request.method == "GET":
        rows = db.session.query(Kanji).count()
        random_id = random.randint(1, rows)
        random_word = Kanji.query.get(random_id)
        return jsonify(random_word.to_dict())

@app.route('/all', methods=["GET"])
def get_all():
    if request.method == "GET":
        all_kanji_db = db.session.execute(db.select(Kanji).order_by(Kanji.id)).scalars().all()
        all_kanji_list = [kanji.to_dict() for kanji in all_kanji_db]
        if all_kanji_list:
            return jsonify(all_kanji_list)
        else:
            return jsonify({"error": "No entries in database. Please try again."})

@app.route('/search', methods=["GET"])
def search_kanji():
    if request.method == "GET":
        kanji_id = request.args.get('id')
        try:
            kanji = db.session.query(Kanji).get(kanji_id)
            return jsonify(kanji.to_dict())
        except Exception as err:
            return jsonify({"error": str(err)})

@app.route('/add', methods=["POST"])
def add_kanji():
    if request.method == "POST":
        api_key = request.headers.get('apikey')
        if api_key == os.getenv('API_KEY'):
            new_kanji = Kanji(
                kanji=request.args.get('kanji'),
                kunyomi=request.args.get('kunyomi'),
                onyomi=request.args.get('onyomi'),
                meaning=request.args.get('meaning')
            )
            db.session.add(new_kanji)
            try:
                db.session.commit()
                return jsonify(response={"success": "Successfully added the new kanji."})
            except Exception as err:
                return jsonify(error={"failed": str(err)})
        else:
            return jsonify(error={"failed": "Invalid API_KEY."})

@app.route('/delete', methods=["DELETE"])
def delete_kanji():
    if request.method == "DELETE":
        api_key = request.headers.get('apikey')
        if api_key == os.getenv('API_KEY'):
            kanji_id = request.args.get('id')
            try:
                kanji_to_delete = db.get_or_404(Kanji, kanji_id)
                db.session.delete(kanji_to_delete)
                db.session.commit()
                return jsonify({"success": "The kanji has been successfully deleted"})
            except Exception as err:
                return jsonify({"error": str(err)})
        else:
            return jsonify({"error": "Invalid API_KEY."})

@app.route('/edit', methods=["PATCH"])
def edit_kanji():
    if request.method == "PATCH":
        api_key = request.headers.get('apikey')
        if api_key == os.getenv('API_KEY'):
            kanji_id  = request.args.get('id')
            try:
                kanji_to_edit = db.session.query(Kanji).get(kanji_id)
                if request.args.get('kunyomi'):
                    kanji_to_edit.kunyomi = request.args.get('kunyomi')
                if request.args.get('onyomi'):
                    kanji_to_edit.onyomi = request.args.get('onyomi')
                if request.args.get('meaning'):
                    kanji_to_edit.meaning = request.args.get('meaning')
                db.session.commit()
                return jsonify({"success": "The kanji has beeen successfully updated"})
            except Exception as err:
                return jsonify({"error": str(err)})

if __name__ == "__main__":
    app.run(debug=True)
