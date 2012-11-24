"""
stanbicmm.exceptions
~~~~~~~~~~~~~~~~~~~~

This module contains exceptions defined for StanbicMM
"""


class AuthRequiredException(Exception):
    """When making a request for some resource and there's need for
    authentication or re-authentication, this exception is raised"""


class AuthDeniedException(Exception):
    """An exception that gets thrown when authentication details are
    incorrect or missing."""


class RequestErrorException(Exception):
    """Some requests will generate an error if the supplied
    request parameters are invalid"""


class InvalidAccountException(Exception):
    """When retrieving account details for an invalid or non-existent
    account, this exception gets thrown. This exception is also get
    raised if you're trying to retrieve account details for the currently
    authenticated account.
    """
