from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.app_context().push()

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        # Loop through each column in the data record.
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            # print(column.name)
            # print(getattr(self, column.name))
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


# with app.app_context():
#     db.create_all()

@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    all_cafes = db.session.execute(db.select(Cafe)).scalars().all()
    random_cafe = random.choice(all_cafes)
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all")
def cafes():
    all_cafes = db.session.execute(db.select(Cafe)).scalars().all()
    cafe_list = []
    for cafe in all_cafes:
        new_data = cafe.to_dict()
        cafe_list.append(new_data)
    return jsonify(cafes=cafe_list)


@app.route("/search")
def search():
    location = request.args.get("loc")
    all_cafes = db.session.execute(db.select(Cafe).filter_by(location=location)).scalars().all()
    located_cafes = [cafe.to_dict() for cafe in all_cafes]
    if located_cafes:
        return jsonify(cafe=located_cafes)
    else:
        message = {"Not found": "Sorry we don't have a cafe at that location"}
        return jsonify(error=message)


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    cafe = db.get_or_404(Cafe, cafe_id)
    if cafe:
        cafe.coffee_price = request.args.get("new_price")
        db.session.commit()
        return jsonify(response={"success": "Successfully added the new cafe."}), 200
    else:
        return jsonify(error={"Not found": "Sorry a cafe with that id was not found in the database"}), 404


# HTTP DELETE - Delete Record
@app.route("/report-closed/<cafe_id>")
def delete_cafe(cafe_id):
    correct_api_key = "yesilovecoffee"
    api_key = request.args.get("api-key")
    if api_key == correct_api_key:
        cafe = db.get_or_404(Cafe, cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully added the new cafe."}), 200
        else:
            return jsonify(error={"Not found": "Sorry a cafe with that id was not found in the database"}), 404
    else:
        return jsonify(error="Sorry, that's not allowed. Make sure you have the correct api key"), 403


if __name__ == '__main__':
    app.run(debug=True)
