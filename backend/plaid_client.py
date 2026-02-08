"""
Plaid API client for fetching bank transactions and account data.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions


class PlaidClient:
    """Client for interacting with Plaid API."""
    
    def __init__(self):
        """Initialize Plaid client with credentials from environment."""
        self.client_id = os.getenv("PLAID_CLIENT_ID")
        self.secret = os.getenv("PLAID_SECRET")
        self.env = os.getenv("PLAID_ENV", "sandbox")
        
        if not self.client_id or not self.secret:
            raise Exception("Missing PLAID_CLIENT_ID or PLAID_SECRET in .env")
        
        # Configure Plaid client
        configuration = plaid.Configuration(
            host=self._get_plaid_host(),
            api_key={
                'clientId': self.client_id,
                'secret': self.secret,
            }
        )
        
        api_client = plaid.ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)
    
    def _get_plaid_host(self) -> str:
        """Get Plaid API host based on environment."""
        env_hosts = {
            'sandbox': plaid.Environment.Sandbox,
            'development': plaid.Environment.Development,
            'production': plaid.Environment.Production,
        }
        return env_hosts.get(self.env.lower(), plaid.Environment.Sandbox)
    
    def create_link_token(self, user_id: str) -> Dict:
        """
        Create a link token for Plaid Link initialization.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dict with link_token and expiration
        """
        try:
            request = LinkTokenCreateRequest(
                user=LinkTokenCreateRequestUser(client_user_id=user_id),
                client_name="AccountantAI",
                products=[Products("transactions")],
                country_codes=[CountryCode("US")],
                language="en",
            )
            
            response = self.client.link_token_create(request)
            return {
                "link_token": response['link_token'],
                "expiration": response['expiration']
            }
        except plaid.ApiException as e:
            raise Exception(f"Plaid API error creating link token: {e}")
    
    def exchange_public_token(self, public_token: str) -> Dict:
        """
        Exchange a public token for an access token.
        
        Args:
            public_token: Public token from Plaid Link
            
        Returns:
            Dict with access_token and item_id
        """
        try:
            request = ItemPublicTokenExchangeRequest(public_token=public_token)
            response = self.client.item_public_token_exchange(request)
            
            return {
                "access_token": response['access_token'],
                "item_id": response['item_id']
            }
        except plaid.ApiException as e:
            raise Exception(f"Plaid API error exchanging token: {e}")
    
    def get_transactions(
        self, 
        access_token: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Fetch transactions for an access token.
        
        Args:
            access_token: Plaid access token
            start_date: Start date for transactions (default: 30 days ago)
            end_date: End date for transactions (default: today)
            
        Returns:
            List of transaction dictionaries
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        try:
            request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date.date(),
                end_date=end_date.date(),
                options=TransactionsGetRequestOptions()
            )
            
            response = self.client.transactions_get(request)
            transactions = response['transactions']
            
            # Format transactions
            formatted_transactions = []
            for tx in transactions:
                formatted_transactions.append({
                    "transaction_id": tx.get('transaction_id'),
                    "date": tx.get('date'),
                    "name": tx.get('name'),
                    "merchant_name": tx.get('merchant_name'),
                    "amount": float(tx.get('amount', 0)),
                    "category": tx.get('category', []),
                    "payment_channel": tx.get('payment_channel'),
                    "pending": tx.get('pending', False),
                })
            
            return formatted_transactions
            
        except plaid.ApiException as e:
            raise Exception(f"Plaid API error fetching transactions: {e}")
    
    def get_accounts(self, access_token: str) -> List[Dict]:
        """
        Fetch account information for an access token.
        
        Args:
            access_token: Plaid access token
            
        Returns:
            List of account dictionaries
        """
        try:
            from plaid.model.accounts_get_request import AccountsGetRequest
            
            request = AccountsGetRequest(access_token=access_token)
            response = self.client.accounts_get(request)
            
            accounts = []
            for account in response['accounts']:
                accounts.append({
                    "account_id": account.get('account_id'),
                    "name": account.get('name'),
                    "type": account.get('type'),
                    "subtype": account.get('subtype'),
                    "balance": {
                        "current": account.get('balances', {}).get('current'),
                        "available": account.get('balances', {}).get('available'),
                    }
                })
            
            return accounts
            
        except plaid.ApiException as e:
            raise Exception(f"Plaid API error fetching accounts: {e}")
