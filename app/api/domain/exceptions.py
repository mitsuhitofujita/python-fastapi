"""Domain-level exceptions for business rule violations."""


class DomainValidationError(Exception):
    """Base class for domain validation errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class DuplicateCodeError(DomainValidationError):
    """Raised when a code already exists in the database."""

    def __init__(self, entity_type: str, code: str):
        self.entity_type = entity_type
        self.code = code
        message = f"{entity_type} with code '{code}' already exists"
        super().__init__(message)


class EntityNotFoundError(DomainValidationError):
    """Raised when a required entity does not exist."""

    def __init__(self, entity_type: str, entity_id: int):
        self.entity_type = entity_type
        self.entity_id = entity_id
        message = f"{entity_type} with id {entity_id} not found"
        super().__init__(message)
