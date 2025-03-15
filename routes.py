from flask import request, jsonify
from datetime import datetime
from database import db, Medication, Customer, Order, OrderItem

def register_routes(app):
    # API Route for Medications
    @app.route('/api/medications', methods=['GET'])
    def get_medications():
        medications = Medication.query.all()
        return jsonify({
            'success': True,
            'medications': [med.to_dict() for med in medications]
        })


    @app.route('/api/medications/<int:id>', methods=['GET'])
    def get_medication(id):
        medication = Medication.query.get_or_404(id)
        return jsonify({
            'success': True,
            'medication': medication.to_dict()
        })


    @app.route('/api/medications', methods=['POST'])
    def create_medication():
        data = request.json

        new_medication = Medication(
            name=data.get('name'),
            description=data.get('description'),
            dosage=data.get('dosage'),
            stock=data.get('stock', 0),
            price=data.get('price')
        )

        db.session.add(new_medication)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Medication added successfully',
            'medication': new_medication.to_dict()
        }), 201


    @app.route('/api/medications/<int:id>', methods=['PUT'])
    def update_medication(id):
        medication = Medication.query.get_or_404(id)
        data = request.json

        medication.name = data.get('name', medication.name)
        medication.description = data.get('description', medication.description)
        medication.dosage = data.get('dosage', medication.dosage)
        medication.stock = data.get('stock', medication.stock)
        medication.price = data.get('price', medication.price)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Medication updated successfully',
            'medication': medication.to_dict()
        })


    @app.route('/api/medications/<int:id>', methods=['DELETE'])
    def delete_medication(id):
        medication = Medication.query.get_or_404(id)

        db.session.delete(medication)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Medication deleted successfully'
        })


    # API Routes for Customers
    @app.route('/api/customers', methods=['GET'])
    def get_customers():
        customers = Customer.query.all()
        return jsonify({
            'success': True,
            'customers': [customer.to_dict() for customer in customers]
        })


    @app.route('/api/customers/<int:id>', methods=['GET'])
    def get_customer(id):
        customer = Customer.query.get_or_404(id)
        return jsonify({
            'success': True,
            'customer': customer.to_dict()
        })


    @app.route('/api/customers', methods=['POST'])
    def create_customer():
        data = request.json

        new_customer = Customer(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address')
        )

        db.session.add(new_customer)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Customer added successfully',
            'customer': new_customer.to_dict()
        }), 201


    @app.route('/api/customers/<int:id>', methods=['PUT'])
    def update_customer(id):
        customer = Customer.query.get_or_404(id)
        data = request.json

        customer.name = data.get('name', customer.name)
        customer.email = data.get('email', customer.email)
        customer.phone = data.get('phone', customer.phone)
        customer.address = data.get('address', customer.address)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Customer updated successfully',
            'customer': customer.to_dict()
        })


    # API Routes for Orders
    @app.route('/api/orders', methods=['GET'])
    def get_orders():
        orders = Order.query.all()
        return jsonify({
            'success': True,
            'orders': [order.to_dict() for order in orders]
        })


    @app.route('/api/orders/<int:id>', methods=['GET'])
    def get_order(id):
        order = Order.query.get_or_404(id)
        return jsonify({
            'success': True,
            'order': order.to_dict()
        })


    @app.route('/api/orders', methods=['POST'])
    def create_order():
        data = request.json

        # Create new order
        new_order = Order(
            customer_id=data.get('customer_id'),
            status='pending'
        )

        db.session.add(new_order)
        db.session.flush()  # Flush to get the order ID

        total_amount = 0

        # Add order items
        for item in data.get('items', []):
            medication = Medication.query.get(item.get('medication_id'))
            if not medication:
                continue

            if medication.stock < item.get('quantity', 1):
                return jsonify({
                    'success': False,
                    'message': f'Insufficient stock for {medication.name}'
                }), 400

            # Reduce medication stock
            medication.stock -= item.get('quantity', 1)

            # Create order item
            new_item = OrderItem(
                order_id=new_order.id,
                medication_id=medication.id,
                quantity=item.get('quantity', 1),
                unit_price=medication.price
            )

            total_amount += new_item.quantity * new_item.unit_price
            db.session.add(new_item)

        new_order.total_amount = total_amount
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Order created successfully',
            'order': new_order.to_dict()
        }), 201


    @app.route('/api/orders/<int:id>', methods=['PUT'])
    def update_order_status(id):
        order = Order.query.get_or_404(id)
        data = request.json

        order.status = data.get('status', order.status)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Order status updated successfully',
            'order': order.to_dict()
        })


    # Dashboard statistics
    @app.route('/api/dashboard', methods=['GET'])
    def get_dashboard():
        total_medications = Medication.query.count()
        total_customers = Customer.query.count()
        total_orders = Order.query.count()

        # Low stock medications (less than 10)
        low_stock = Medication.query.filter(Medication.stock < 10).count()

        # Recent orders (last 7 days)
        recent_orders = Order.query.filter(
            Order.created_at >= datetime.utcnow().date()
        ).count()

        return jsonify({
            'success': True,
            'stats': {
                'total_medications': total_medications,
                'total_customers': total_customers,
                'total_orders': total_orders,
                'low_stock_count': low_stock,
                'recent_orders': recent_orders
            }
        })