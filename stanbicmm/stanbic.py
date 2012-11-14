"""
stanbicmm.stanbic
~~~~~~~~~~~~~~~~~~~~

This is the core module for all the functionality required
to interact with the Stanbic Mobile Money web application.
"""

from copy import deepcopy
import csv
from cStringIO import StringIO
from datetime import datetime
from .exceptions import *
import mechanize
import urllib


class StanbicMM(object):
    """
    Interacting with the Stanbic Mobile Money system using this library is
    easy. Simply create an object of this class using the account number and
    pin of the account you wish to interact with and call the methods representing
    the operation you want to carry out.

    Example:
    > mm = StanbicMM('2348012345678', '1234') # where '1234' is the pin
    > transactions = mm.get_transactions()

    It's that simple.
    """
    AUTH_URL = 'https://mobilemoney.stanbic.com/do/login'
    TRANSACTIONS_EXPORT_URL = 'https://mobilemoney.stanbic.com/do/exportAccountHistoryToCsv'
    TRANSACTIONS_URL = 'https://mobilemoney.stanbic.com/do/member/accountHistory?advanced=true&memberId=0&typeId=5'
    ERROR_URL = 'https://mobilemoney.stanbic.com/do/error'
    TRANSACTIONS_FORM = None

    def __init__(self, account, pin, browser=None):
        """
        In some occasions where you'll make a number of requests
        to the server, you will want to store the mechanize browser
        object in some cache so it can be reused.

        This has the advantage of reducing the number of requests
        necessary to complete given tasks.

        The browser object can simply be created this way:

        > browser = mechanize.Browser()
        """
        self.account = account
        self.pin = pin
        self.br = browser or mechanize.Browser()
        self.br.set_handle_robots(False)

    def get_transactions(self, **kwargs):
        """
        This method optionally takes the following extra
        keyword arguments:

        to_date: a datetime object representing the date the filter should end with
        from_date: a datetime object representing the date the filter should start from
        txn_ref: the transaction reference of a particular transaction

        If you specify txn_ref, then it's not necessary to specify to_date and from_date.
        """
        kw_map = {
            'to_date': 'query(period).end',
            'from_date': 'query(period).begin',
            'txn_ref': 'query(transactionNumber)'}

        if not self.TRANSACTIONS_FORM:
            try:
                self.get_url(self.TRANSACTIONS_URL)
            except AuthRequiredException:
                self._auth()
                self.get_url(self.TRANSACTIONS_URL)
            self.br.select_form("accountHistoryForm")
            self.br.form.method = 'POST'
            self.br.form.action = self.TRANSACTIONS_EXPORT_URL
            self.TRANSACTIONS_FORM = self.br.form
            _form = deepcopy(self.TRANSACTIONS_FORM)
        else:
            _form = deepcopy(self.TRANSACTIONS_FORM)

        for key, field_name in kw_map.items():
            if key in kwargs:
                # if the field is a date, format accordingly
                if key.endswith('_date'):
                    _form[field_name] = kwargs.get(key).strftime('%d/%m/%Y')
                else:
                    _form[field_name] = kwargs.get(key)

        try:
            r = self.post_url(self.TRANSACTIONS_EXPORT_URL, form=_form)
            return self._parse_transactions(r)
        except AuthRequiredException:
            self._auth()
            r = self.post_url(self.TRANSACTIONS_EXPORT_URL, form=_form)
            return self._parse_transactions(r)

    def make_payment(self, recipient, amount, description=None):
        """
        Not yet implemented
        """
        raise NotImplementedError

    def _auth(self):
        _form = urllib.urlencode({'principal': self.account, 'password': self.pin})
        self.br.open(self.AUTH_URL, _form)

        # a successful login response yields a 302 found status code
        # and a redirect location of https://mobilemoney.stanbic.com/do/member/home
        if self.br.geturl().startswith(self.ERROR_URL):
            raise AuthDeniedException
        else:
            return True

    def get_url(self, url):
        """
        Internally used to retrieve the contents of a URL
        """
        _r = self.br.open(url)

        # check that we've not been redirected to the login page
        if self.br.geturl().startswith(self.AUTH_URL):
            raise AuthRequiredException
        elif self.br.geturl().startswith(self.ERROR_URL):
            raise RequestErrorException
        else:
            return _r.read()

    def post_url(self, url, form):
        """
        Internally used to retrieve the contents of a URL using
        the POST request method.
        
        The `form` parameter is a mechanize.HTMLForm object

        This method will use a POST request type regardless of the method
        used in the `form`.
        """
        _r = self.br.open(url, form.click_request_data()[1])

        # check that we've not been redirected to the login page or an error occured
        if self.br.geturl().startswith(self.AUTH_URL):
            raise AuthRequiredException
        elif self.br.geturl().startswith(self.ERROR_URL):
            raise RequestErrorException
        else:
            return _r.read()

    def _parse_transactions(self, response):
        """
        This method parses the CSV output in `get_transactions`
        to generate a usable list of transactions that use native
        python data types
        """
        transactions = list()

        if response:
            f = StringIO(response)
            reader = csv.DictReader(f)

            for line in reader:
                txn = {}
                txn['date'] = datetime.strptime(line['Date'], '%d/%m/%Y %H:%M:%S')
                txn['description'] = line['Description']
                txn['amount'] = float(line['Amount'].replace(',', ''))
                txn['reference'] = line['Transaction number']
                txn['sender'] = line['???transfer.fromOwner???']
                txn['recipient'] = line['???transfer.toOwner???']
                txn['currency'] = 'NGN'
                txn['comment'] = line['Transaction type']

                transactions.append(txn)

        return transactions
