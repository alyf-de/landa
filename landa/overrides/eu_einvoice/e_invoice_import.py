from eu_einvoice.european_e_invoice.doctype.e_invoice_import.e_invoice_import import EInvoiceImport


class LandaEInvoiceImport(EInvoiceImport):
	def before_submit(self):
		# We don't want to create a Purchase Invoice from the E Invoice Import.
		# Hence, we can disable the validation of mandatory fields before submit.
		pass
