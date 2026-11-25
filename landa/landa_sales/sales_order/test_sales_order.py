from unittest import TestCase
from unittest.mock import patch

from landa.landa_sales.sales_order.sales_order import make_landa_sales_invoice

MODULE = "landa.landa_sales.sales_order.sales_order"


@patch(f"{MODULE}.update_doc")
@patch(f"{MODULE}.frappe.get_doc")
class TestMakeLandaSalesInvoice(TestCase):
	@patch(f"{MODULE}.make_sales_invoice")
	def test_passes_arguments_to_erpnext_by_keyword(self, mock_make_sales_invoice, _get_doc, _update_doc):
		args = {"filtered_children": ["SO-ITEM-1"]}

		make_landa_sales_invoice("SO-1", None, args=args, ignore_permissions=True)

		mock_make_sales_invoice.assert_called_once_with("SO-1", None, args=args, ignore_permissions=True)
