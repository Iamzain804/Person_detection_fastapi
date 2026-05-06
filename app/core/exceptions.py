from fastapi import HTTPException, status

class PersonDetectionException(Exception):
    def __init__(self, message: str, code: int = 500):
        self.message = message
        self.code = code

class CorruptedImageException(PersonDetectionException):
    def __init__(self, message: str = "The uploaded image is corrupted or invalid"):
        super().__init__(message, code=status.HTTP_400_BAD_REQUEST)

class ModelInferenceTimeoutException(PersonDetectionException):
    def __init__(self, message: str = "Model inference timed out"):
        super().__init__(message, code=status.HTTP_504_GATEWAY_TIMEOUT)

class AuthenticationFailureException(PersonDetectionException):
    def __init__(self, message: str = "Invalid or missing API Key"):
        super().__init__(message, code=status.HTTP_401_UNAUTHORIZED)
