import { test, expect } from "../support";

test.describe("Sales Order", () => {
	let data;

	test.beforeAll(async ({ admin }) => {
		const response = await admin.call("landa.tests.ui_test_helpers.create_sales_order_data");
		data = response.message;
	});

	test("local organization user gets the items of the year of settlement", async ({
		desk,
		page,
	}) => {
		const item_codes = page.locator(
			'.frappe-control[data-fieldname="items"] .grid-body [data-fieldname="item_code"]',
		);

		await desk.login(data.user);
		await desk.new_form("Sales Order");
		await expect(desk.get_field("company", "Link")).toHaveValue(data.company);
		await expect(desk.get_field("customer", "Link")).toHaveValue(data.customer);
		await form_is_settled(page);

		await set_year_of_settlement(desk, data.year);
		await expect(item_codes).toHaveText([data.item]);

		await set_year_of_settlement(desk, data.next_year);
		await expect(item_codes).toHaveText([data.item_next_year]);
	});
});

async function form_is_settled(page) {
	// ERPNext sets its own item query when the form opens. LANDA replaces it a moment later.
	// Until then, the items are not filtered by year.
	const has_landa_item_query = () =>
		page.evaluate(() => {
			const item_code = cur_frm.fields_dict.items.grid.get_field("item_code");
			return "valid_from_year" in item_code.get_query(cur_frm.doc).filters;
		});
	await expect.poll(has_landa_item_query).toBe(true);

	// The response with the customer details refreshes the form and would discard new input.
	await expect(page.locator("body")).toHaveAttribute("data-ajax-state", "complete");
}

async function set_year_of_settlement(desk, year) {
	const input = desk.get_field("year_of_settlement", "Int");
	await input.fill(String(year));
	await input.blur();
	await expect(input).toHaveValue(String(year));
}
