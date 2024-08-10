from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Resource, fields

app = Flask(__name__)

# Configuration for PostgreSQL connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
api = Api(app, version='1.0', title='Item API',
          description='A simple CRUD API for managing items')

ns = api.namespace('items', description='Operations related to items')

# Model definition
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name}

with app.app_context():
    db.create_all()

# Define a Flask-RESTX model for item serialization
item_model = api.model('Item', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of an item'),
    'name': fields.String(required=True, description='The name of the item')
})

@ns.route('/')
class ItemList(Resource):
    @ns.doc('list_items')
    @ns.marshal_list_with(item_model)
    def get(self):
        """List all items"""
        items = Item.query.all()
        return [item.to_dict() for item in items]

    @ns.doc('create_item')
    @ns.expect(item_model)
    @ns.marshal_with(item_model, code=201)
    def post(self):
        """Create a new item"""
        data = api.payload
        new_item = Item(name=data['name'])
        db.session.add(new_item)
        db.session.commit()
        return new_item.to_dict(), 201

@ns.route('/<int:id>')
@ns.response(404, 'Item not found')
@ns.param('id', 'The item identifier')
class ItemResource(Resource):
    @ns.doc('get_item')
    @ns.marshal_with(item_model)
    def get(self, id):
        """Fetch an item given its identifier"""
        item = Item.query.get_or_404(id)
        return item.to_dict()

    @ns.doc('update_item')
    @ns.expect(item_model)
    @ns.marshal_with(item_model)
    def put(self, id):
        """Update an item given its identifier"""
        item = Item.query.get_or_404(id)
        data = api.payload
        item.name = data['name']
        db.session.commit()
        return item.to_dict()

    @ns.doc('delete_item')
    @ns.response(204, 'Item deleted')
    def delete(self, id):
        """Delete an item given its identifier"""
        item = Item.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0')
