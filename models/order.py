from db import db
from datetime import datetime


class TimeMixin(object):
    created_at = db.Column(db.DateTime(), default=datetime.today())

class OrderModel(db.Model, TimeMixin):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("cutomer.id"), nullable=False)
    order_data = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(120), nullable=False)
    
    customer = db.relationship("CustomerModel", backref=db.backref('orders', lazy=True))

    def __init__(self, cutomer_id, order_data, status):
        self.customer_id = customer_id
        self.order_data = order_data
        self.status = status

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()