"""Custom domain and application exceptions."""


class CustomerAlreadyExistsError(Exception):
    """Raised when attempting to register a customer with an existing email address."""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"Customer with email '{email}' already exists.")


class CustomerStorageError(Exception):
    """Raised when the customer storage file cannot be read or parsed."""

    def __init__(self, file_path: str, reason: str) -> None:
        self.file_path = file_path
        self.reason = reason
        super().__init__(f"Customer storage file '{file_path}' could not be read: {reason}")
