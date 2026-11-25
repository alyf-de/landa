from unittest import TestCase
from unittest.mock import patch

from landa.landa_sales.sales_order.sales_order import make_landa_delivery_note, make_landa_sales_invoice

MODULE = "landa.landa_sales.sales_order.sales_order"


@patch(f"{MODULE}.update_doc")
@patch(f"{MODULE}.frappe.get_doc")
class TestSalesOrderMappers(TestCase):
	@patch(f"{MODULE}.make_sales_invoice")
	def test_sales_invoice_passes_arguments_by_keyword(self, mock_make_sales_invoice, _get_doc, _update_doc):
		args = {"filtered_children": ["SO-ITEM-1"]}

		make_landa_sales_invoice("SO-1", None, args=args, ignore_permissions=True)

		mock_make_sales_invoice.assert_called_once_with("SO-1", None, args=args, ignore_permissions=True)

	@patch(f"{MODULE}.make_delivery_note")
	def test_delivery_note_passes_kwargs_by_keyword(self, mock_make_delivery_note, _get_doc, _update_doc):
		# "Get Items From" calls frappe.model.mapper.map_docs, which passes args as the third positional argument
		kwargs = {"for_reserved_stock": 1, "filtered_children": ["SO-ITEM-1"]}

		make_landa_delivery_note("SO-1", None, kwargs)

		mock_make_delivery_note.assert_called_once_with("SO-1", None, kwargs=kwargs)
