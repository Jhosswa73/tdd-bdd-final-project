from flask import jsonify, request, abort
from flask import url_for
from service.models import Product, Category
from service.common import status
from . import app

@app.route("/health")
def healthcheck():
    return jsonify(status=200, message="OK"), status.HTTP_200_OK

@app.route("/")
def index():
    return app.send_static_file("index.html")

def check_content_type(content_type):
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
              f"Content-Type must be {content_type}")

    if request.headers["Content-Type"] != content_type:
        app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
        abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
              f"Content-Type must be {content_type}")

@app.route("/products", methods=["POST"])
def create_products():
    app.logger.info("Request to Create a Product...")
    check_content_type("application/json")

    data = request.get_json()
    product = Product()
    product.deserialize(data)
    product.create()
    location_url = url_for("get_products", product_id=product.id, _external=True)
    return jsonify(product.serialize()), status.HTTP_201_CREATED, {"Location": location_url}

@app.route("/products", methods=["GET"])
def list_products():
    app.logger.info("Request to list Products...")

    name = request.args.get("name")
    category = request.args.get("category")
    available = request.args.get("available")
    products = []

    if name:
        app.logger.info("Find by name: %s", name)
        products = Product.find_by_name(name)
    elif category:
        app.logger.info("Find by category: %s", category)
        category_value = getattr(Category, category.upper())
        products = Product.find_by_category(category_value)
    elif available:
        app.logger.info("Find by availability: %s", available)
        available_value = available.lower() in ["true", "yes", "1"]
        products = Product.find_by_availability(available_value)
    else:
        app.logger.info("Find all")
        products = Product.all()

    results = [product.serialize() for product in products]
    return results, status.HTTP_200_OK

@app.route("/products/<int:product_id>", methods=["GET"])
def get_products(product_id):
    app.logger.info("Request to Retrieve a product with id [%s]", product_id)
    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")
    return product.serialize(), status.HTTP_200_OK

@app.route("/products/<int:product_id>", methods=["PUT"])
def update_products(product_id):
    app.logger.info("Request to Update a product with id [%s]", product_id)
    check_content_type("application/json")
    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")

    product.deserialize(request.get_json())
    product.id = product_id
    product.update()
    return product.serialize(), status.HTTP_200_OK

@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_products(product_id):
    app.logger.info("Request to Delete a product with id [%s]", product_id)
    product = Product.find(product_id)
    if product:
        product.delete()
    return "", status.HTTP_204_NO_CONTENT
