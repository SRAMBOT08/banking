from __future__ import annotations
from dataclasses import dataclass
from random import Random
from typing import Any


@dataclass
class EnterpriseGenerators:
    rng: Random

    def identity(self, index: int = 0) -> dict[str, Any]:
        first = ['Aisha', 'Daniel', 'Priya', 'Marcus', 'Sofia', 'Noah', 'Grace', 'Ethan'][index % 8]
        last = ['Patel', 'Morgan', 'Chen', 'Williams', 'Garcia', 'Okafor', 'Nakamura', 'Brown'][(index // 2) % 8]
        return {'user_id': f'user-{index + 1001}', 'username': f'{first.lower()}.{last.lower()}@demo-bank.example', 'display_name': f'{first} {last}', 'department': ['treasury', 'retail-banking', 'security', 'finance'][index % 4], 'role': ['analyst', 'manager', 'administrator', 'operations'][index % 4]}

    def customer(self, index: int = 0) -> dict[str, Any]:
        return {'customer_id': f'customer-{index + 20001}', 'name': f'Customer {index + 1:04d}', 'segment': ['retail', 'premium', 'business'][index % 3]}

    def account(self, index: int = 0) -> dict[str, Any]:
        return {'account_id': f'acct-{index + 30001}', 'account_type': ['checking', 'savings', 'commercial'][index % 3], 'currency': 'USD', 'balance_band': ['low', 'medium', 'high'][index % 3]}

    def device(self, index: int = 0, trusted: bool = True) -> dict[str, Any]:
        return {'device_id': f'device-{index + 40001}', 'os': ['Windows 11', 'macOS', 'iOS', 'Android'][index % 4], 'browser': ['Chrome', 'Edge', 'Safari', 'Firefox'][index % 4], 'managed': trusted, 'trusted': trusted, 'fingerprint': f'fp-{self.rng.getrandbits(48):012x}'}

    def location(self, index: int = 0) -> dict[str, Any]:
        return [{'city': 'New York', 'country': 'US', 'lat': 40.7128, 'lon': -74.0060}, {'city': 'London', 'country': 'GB', 'lat': 51.5072, 'lon': -0.1276}, {'city': 'Singapore', 'country': 'SG', 'lat': 1.3521, 'lon': 103.8198}, {'city': 'Toronto', 'country': 'CA', 'lat': 43.6532, 'lon': -79.3832}][index % 4]

    def ip(self, private: bool = False, tor: bool = False) -> str:
        if tor:
            return f'185.220.{self.rng.randrange(1, 250)}.{self.rng.randrange(1, 250)}'
        if private:
            return f'10.{self.rng.randrange(1, 250)}.{self.rng.randrange(1, 250)}.{self.rng.randrange(1, 250)}'
        return f'198.51.{self.rng.randrange(1, 250)}.{self.rng.randrange(1, 250)}'

    def network(self, index: int = 0, tor: bool = False) -> dict[str, Any]:
        return {'ip_address': self.ip(tor=tor), 'asn': 'AS64500' if tor else f'AS{64510 + index % 20}', 'network_type': 'tor_exit' if tor else ('corporate' if index % 2 == 0 else 'residential'), 'vpn': index % 5 == 0 and not tor}

    def transaction(self, index: int = 0, amount: float | None = None) -> dict[str, Any]:
        return {'transaction_id': f'txn-{index + 50001}', 'amount': amount if amount is not None else round(self.rng.uniform(12, 950), 2), 'currency': 'USD', 'merchant': ['grocer', 'utility', 'travel', 'electronics'][index % 4], 'channel': ['online', 'branch', 'mobile'][index % 3]}


class IdentityGenerator(EnterpriseGenerators):
    pass


class DeviceGenerator(EnterpriseGenerators):
    pass


class GeoGenerator(EnterpriseGenerators):
    pass


class NetworkGenerator(EnterpriseGenerators):
    pass


class TransactionGenerator(EnterpriseGenerators):
    pass
