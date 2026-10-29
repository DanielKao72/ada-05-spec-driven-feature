"""Custom domain and application exceptions."""


class CustomerAlreadyExistsError(Exception):
    """Raised when attempting to register a customer with an existing email address."""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"Customer with email '{email}' already exists.")


class StorageCorruptedError(Exception):
    """Raised when the JSON storage file exists but cannot be decoded."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        super().__init__(f"Customer storage file '{file_path}' contains invalid JSON.")
