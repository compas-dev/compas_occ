class BrepError(Exception):
    """Base class for exceptions in this module."""

    pass


class BrepFilletError(BrepError):
    """Exception raised for errors in filleting."""

    pass


class BrepBooleanError(BrepError):
    """Exception raised for errors in (re-)building breps."""

    pass
