class RatesProviderError(Exception):
    pass


class RatesProviderUnavailable(RatesProviderError):
    pass


class RatesProviderBadRequest(RatesProviderError):
    pass
