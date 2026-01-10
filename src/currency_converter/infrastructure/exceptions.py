class ExternalServiceError(Exception):
    pass


class ExternalServiceUnavailable(ExternalServiceError):
    pass


class ExternalServiceBadRequest(ExternalServiceError):
    pass
