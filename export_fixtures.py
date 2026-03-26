import os
from django.core.management import call_command


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

import django

django.setup()

print("I'm starting data export...")

# Ways to files of fixtures
categories_path = os.path.join(os.getcwd(), "fixtures", "goods", "categories.json")
products_path = os.path.join(os.getcwd(), "fixtures", "goods", "products.json")

# Create fixtures/goods, because there is no
os.makedirs(os.path.dirname(categories_path), exist_ok=True)

try:
    # Export goods.Categories/Products to a file
    with open(categories_path, "w", encoding="utf-8") as file:
        call_command("dumpdata", "goods.Categories", indent=4, stdout=file)
    print(f"Data from goods.Categories successfully saved in {categories_path}")
except Exception as e:
    print(f"Merchandise while saving goods.Categories: {e}")

try:
    with open(products_path, "w", encoding="utf-8") as file:
        call_command("dumpdata", "goods.Products", indent=4, stdout=file)
    print(f"Data from goods.Products are successfully saved in {products_path}")
except Exception as e:
    print(f"Waiver while saving goods.Products: {e}")
