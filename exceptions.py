class ProductNotFoundError(ValueError):
    pass


class DuplicateProductError(ValueError):
    pass


class InsufficientStockError(ValueError):
    pass