from db import db
from datetime import datetime


class TimeMixin(object):
    created_at = db.Column(db.DateTime(), default=datetime.today())

class OrderModel(db.Model, TimeMixin):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    order_data = db.Column(db.String(1200), nullable=False)
    status = db.Column(db.String(120), nullable=False, default="Pending")
    amount = db.Column(db.Float(precision=3), nullable=False)
    billing_adress = db.Column(db.String(120), nullable=False)


    def __init__(self, customer_id, order_data, status, amount, billing_adress):
        self.customer_id = customer_id
        self.order_data = order_data
        self.status = status
        self.amount = amount
        self.billing_adress = billing_adress

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()