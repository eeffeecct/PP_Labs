class ElectronicsStoreError(Exception):
    pass


class InsufficientStockError(ElectronicsStoreError):
    def __init__(self, product_name: str, requested: int, available: int):
        self.product_name = product_name
        self.requested = requested
        self.available = available
        super().__init__(
            f"Insufficient stock for '{product_name}'. "
            f"Requested: {requested}, Available: {available}"
        )


class ProductNotFoundError(ElectronicsStoreError):
    def __init__(self, product_id: int):
        self.product_id = product_id
        super().__init__(f"Product with ID {product_id} not found")


class CustomerNotFoundError(ElectronicsStoreError):
    def __init__(self, customer_id: int):
        self.customer_id = customer_id
        super().__init__(f"Customer with ID {customer_id} not found")


class OrderProcessingError(ElectronicsStoreError):
    pass

class DataValidationError(ElectronicsStoreError):
    def __init__(self, message: str, field: str = None, value: object = None):
        self.field = field
        self.value = value
        super().__init__(f"Data validation error: {message}")
