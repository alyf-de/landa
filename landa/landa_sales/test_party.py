from unittest import TestCase
from unittest.mock import Mock, patch

from landa.landa_sales.party import set_billing_address, set_shipping_address
from landa.property_setters import get_property_setters


class TestPartyAddressDefaults(TestCase):
	def test_address_fetch_from_property_setters_removed(self):
		setters = get_property_setters()
		removed = {
			("customer_address", "fetch_from"),
			("customer_address", "fetch_if_empty"),
			("shipping_address_name", "fetch_from"),
			("shipping_address_name", "fetch_if_empty"),
		}

		for doctype in ("Sales Invoice", "Delivery Note"):
			present = {(field, prop) for field, prop, _value in setters[doctype] if field}
			self.assertFalse(removed & present)

	@patch("landa.landa_sales.party.get_address_display", side_effect=lambda addr: f"display:{addr}")
	def test_party_details_use_customer_default_addresses(self, _mock_display):
		customer = Mock(
			default_billing_address="BILL-1",
			default_shipping_address="SHIP-1",
		)
		party_details = {}

		set_billing_address(party_details, customer)
		set_shipping_address(party_details, customer)

		self.assertEqual(party_details["customer_address"], "BILL-1")
		self.assertEqual(party_details["address_display"], "display:BILL-1")
		self.assertEqual(party_details["shipping_address_name"], "SHIP-1")
		self.assertEqual(party_details["shipping_address"], "display:SHIP-1")
