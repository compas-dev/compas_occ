class BrepError(Exception):
    """Base class for exceptions in this module."""

    pass


class BrepFilletError(BrepError):
    """Exception raised for errors in filleting."""

    pass


class BrepBooleanError(BrepError):
    """Exception raised for errors in (re-)building breps."""

    pass


class BrepTessellationError(BrepError):
    """Exception raised when Open CASCADE cannot tessellate a BRep completely."""

    pass
