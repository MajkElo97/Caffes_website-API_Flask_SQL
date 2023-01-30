from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import choice

app = Flask(__name__)

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
        # Method 1.
        # dictionary = {}
        # # Loop through each column in the data record
        # for column in self.__table__.columns:
        #     # Create a new dictionary entry;
        #     # where the key is the name of the column
        #     # and the value is the value of the column
        #     dictionary[column.name] = getattr(self, column.name)
        # return dictionary

        # Method 2. Alternatively use Dictionary Comprehension to do the same thing.
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


## HTTP GET - Read Record
@app.route("/random")  # , methods=["GET"]
def get_random_cafe():
    all_caffes = db.session.query(Cafe).all()
    random_cafe = choice(all_caffes)
    # return jsonify(cafe={
    #     "id": random_cafe.id,
    #     "name": random_cafe.name,
    #     "map_url": random_cafe.map_url,
    #     "img_url": random_cafe.img_url,
    #     "location": random_cafe.location,
    #     "seats": random_cafe.seats,
    #     "has_toilet": random_cafe.has_toilet,
    #     "has_wifi": random_cafe.has_wifi,
    #     "has_sockets": random_cafe.has_sockets,
    #     "can_take_calls": random_cafe.can_take_calls,
    #     "coffee_price": random_cafe.coffee_price,
    # })
    # return jsonify(cafe={
    #     # omit the id from the response
    #     # "id": random_cafe.id,
    #     "name": random_cafe.name,
    #     "map_url": random_cafe.map_url,
    #     "img_url": random_cafe.img_url,
    #     "location": random_cafe.location,
    #
    #     # Put some properties in a sub-category
    #     "amenities": {
    #         "seats": random_cafe.seats,
    #         "has_toilet": random_cafe.has_toilet,
    #         "has_wifi": random_cafe.has_wifi,
    #         "has_sockets": random_cafe.has_sockets,
    #         "can_take_calls": random_cafe.can_take_calls,
    #         "coffee_price": random_cafe.coffee_price,
    #     }
    # })
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all")
def get_all_cafes():
    all_caffes = db.session.query(Cafe).all()
    # all_cafe_dict = []
    # for cafe in all_caffes:
    #     cafe_dict = {
    #         "id": cafe.id,
    #         "name": cafe.name,
    #         "map_url": cafe.map_url,
    #         "img_url": cafe.img_url,
    #         "location": cafe.location,
    #         "seats": cafe.seats,
    #         "has_toilet": cafe.has_toilet,
    #         "has_wifi": cafe.has_wifi,
    #         "has_sockets": cafe.has_sockets,
    #         "can_take_calls": cafe.can_take_calls,
    #         "coffee_price": cafe.coffee_price}
    #     all_cafe_dict.append(cafe_dict)
    # return jsonify(all_cafe_dict)
    return jsonify(cafe=[cafe.to_dict() for cafe in all_caffes])


@app.route("/search")
def search():
    location = request.args.get("loc")
    print(location)
    cafe_in_location = Cafe.query.filter_by(location=location).all()
    if not cafe_in_location:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})
    else:
        return jsonify(cafe=[cafe.to_dict() for cafe in cafe_in_location])


## HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def post_new_cafe():
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


## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_cafe(cafe_id):
    new_price = request.args.get("new_price")
    cafe_to_update = Cafe.query.get(cafe_id)
    # cafe = db.session.query(Cafe).get(cafe_id) or this
    if cafe_to_update is None:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404
    else:
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated cafe."}), 200


## HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api = request.args.get("api-key")
    cafe_to_delete = Cafe.query.get(cafe_id)
    if api == "TopSecretAPIKey" and cafe_to_delete is not None:
        db.session.delete(cafe_to_delete)
        db.session.commit()
        return jsonify(response={"success": "Successfully updated cafe."}), 200
    elif api != "TopSecretAPIKey":
        return jsonify(error={"Wrong api-key": "Sorry, you don't have access"}), 403
    else:
        return jsonify(error={"no such caffe": "Sorry, we don't have this caffe"}), 403


if __name__ == '__main__':
    app.run(debug=True)
