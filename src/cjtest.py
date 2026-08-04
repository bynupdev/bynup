# #!/usr/bin/env python
# import os
# import django

# # Setup Django environment
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")
# django.setup()

# from payments.models import Order, OrderItem

# def clear_all_orders():
#     print("Deleting all OrderItems...")
#     OrderItem.objects.all().delete()
#     print("Deleting all Orders...")
#     Order.objects.all().delete()
#     print("All orders and order items have been deleted!")

# if __name__ == "__main__":
#     clear_all_orders()