import json
import os
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

def load_customers():
    """Load customers from JSON file"""
    try:
        with open('data/customers.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Flask Mock Customer API'
    })

@app.route('/api/customers', methods=['GET'])
def get_customers():
    """Get paginated list of customers"""
    customers = load_customers()
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    
    # Validate pagination parameters
    if page < 1:
        page = 1
    if limit < 1:
        limit = 10
    if limit > 100:
        limit = 100
    
    # Calculate pagination
    total = len(customers)
    start_index = (page - 1) * limit
    end_index = start_index + limit
    
    # Get paginated data
    paginated_customers = customers[start_index:end_index]
    
    return jsonify({
        'data': paginated_customers,
        'total': total,
        'page': page,
        'limit': limit
    })

@app.route('/api/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get single customer by ID"""
    customers = load_customers()
    
    # Find customer by ID
    customer = next((c for c in customers if c['customer_id'] == customer_id), None)
    
    if customer is None:
        return jsonify({'error': 'Customer not found'}), 404
    
    return jsonify(customer)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
