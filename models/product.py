from db import db
from datetime import datetime


class TimeMixin(object):
    created_at = db.Column(db.DateTime(), default=datetime.today())

class ProductModel(db.Model, TimeMixin):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    brand = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float(precision=3))
    catergory = db.Column(db.String(80), nullable=False)
    colour = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Integer)

    def __init__(self, name, brand, price, catergory, colour, quantity):
        self.name = name
        self.brand = brand
        self.price = price
        self.catergory = catergory
        self.colour = colour
        self.quantity = quantity

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()