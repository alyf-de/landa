import { test, expect } from "../support";

const ITEM_QUERY = "/api/method/erpnext.controllers.queries.item_query";

test.describe("Sales Order", () => {
	let data;

	test.beforeAll(async ({ admin }) => {
		const response = await admin.call("landa.tests.ui_test_helpers.create_sales_order_data");
		data = response.message;
	});

	test.beforeEach(async ({ page }) => {
		// The default year of settlement depends on the date. The test items exist for fixed years.
		await page.clock.setFixedTime(new Date(data.year, 5, 15));
	});

	test("local organization user gets company, customer, year and items", async ({
		desk,
		page,
	}) => {
		const prefills = count_prefills(page);

		await desk.login(data.local_user);
		await desk.new_form("Sales Order");
		await form_is_settled(page);

		await expect(desk.get_field("company", "Link")).toHaveValue(data.company);
		await expect(desk.get_field("customer", "Link")).toHaveValue(data.customer);
		await expect(desk.get_field("year_of_settlement", "Int")).toHaveValue(String(data.year));
		await expect(item_codes(page)).toHaveText(containing(data.items));
		expect(prefills.count).toBe(1);
	});

	test("regional organization user gets the items after the customer is set", async ({
		admin,
		desk,
		page,
	}) => {
		await desk.login(data.regional_user);
		// The login sets the regional office as the default customer.
		await admin.call("landa.tests.ui_test_helpers.clear_default_customer", {
			user: data.regional_user,
		});
		await desk.new_form("Sales Order");

		await expect(desk.get_field("year_of_settlement", "Int")).toHaveValue(String(data.year));
		await expect(desk.get_field("customer", "Link")).toHaveValue("");
		await expect(item_codes(page)).toHaveCount(0);

		await desk.fill_field("customer", data.customer, "Link");
		await expect(item_codes(page)).toHaveText(containing(data.items));
	});

	test("a failed item request is repeated on the next change", async ({ admin, desk, page }) => {
		await desk.login(data.regional_user);
		await admin.call("landa.tests.ui_test_helpers.clear_default_customer", {
			user: data.regional_user,
		});
		await desk.new_form("Sales Order");
		await expect(desk.get_field("customer", "Link")).toHaveValue("");

		await page.route(`**${ITEM_QUERY}`, (route) => route.abort(), { times: 1 });
		const failed_request = page.waitForEvent("requestfailed", (request) =>
			request.url().endsWith(ITEM_QUERY),
		);
		await desk.fill_field("customer", data.regional_office_customer, "Link");
		await failed_request;
		await expect(item_codes(page)).toHaveCount(0);

		await replace_customer(desk, data.customer);
		await expect(item_codes(page)).toHaveText(containing(data.items));
	});

	test("new order from the organization gets the items once", async ({ desk, page }) => {
		const prefills = count_prefills(page);

		await desk.login(data.local_user);
		await page.goto(`/app/organization/${data.customer}`);
		await page.locator('.document-link[data-doctype="Sales Order"] .btn-new').click();
		await expect(page.locator("body")).toHaveAttribute(
			"data-route",
			/^Form\/Sales Order\/new-sales-order-/,
		);
		await form_is_settled(page);

		await expect(desk.get_field("customer", "Link")).toHaveValue(data.customer);
		await expect(item_codes(page)).toHaveText(containing(data.items));
		expect(prefills.count).toBe(1);
	});

	test("new order from the list keeps the year of the filter", async ({ desk, page }) => {
		await desk.login(data.local_user);
		await page.goto(`/app/sales-order?year_of_settlement=${data.next_year}`);
		await page.locator(".page-head:visible .primary-action").click();
		await expect(page.locator("body")).toHaveAttribute(
			"data-route",
			/^Form\/Sales Order\/new-sales-order-/,
		);
		await form_is_settled(page);

		await expect(desk.get_field("year_of_settlement", "Int")).toHaveValue(
			String(data.next_year),
		);
		await expect(item_codes(page)).toHaveText(containing(data.items_next_year));
	});

	test("duplicated order keeps the copied items", async ({ desk, page }) => {
		await desk.login(data.local_user);
		await desk.new_form("Sales Order");
		await form_is_settled(page);
		await set_qty(desk, page, 2, 3);
		await save(desk);

		await page.locator(".page-head:visible .menu-btn-group > .btn").click();
		await desk.click_menu_item("Duplicate");
		await expect(page.locator("body")).toHaveAttribute(
			"data-route",
			/^Form\/Sales Order\/new-sales-order-/,
		);
		await form_is_settled(page);

		await expect(item_codes(page)).toHaveText(containing([data.items[1]]));
		await expect.poll(() => quantities(page)).toEqual([3]);
	});

	test("a new year of settlement replaces the items", async ({ desk, page }) => {
		await desk.login(data.local_user);
		await desk.new_form("Sales Order");
		await form_is_settled(page);
		await expect(item_codes(page)).toHaveText(containing(data.items));

		await set_year_of_settlement(desk, data.next_year);
		await expect(item_codes(page)).toHaveText(containing(data.items_next_year));
	});

	test("no year of settlement empties the items", async ({ desk, page }) => {
		await desk.login(data.local_user);
		await desk.new_form("Sales Order");
		await form_is_settled(page);
		await expect(item_codes(page)).toHaveText(containing(data.items));

		await set_year_of_settlement(desk, "");
		await expect(item_codes(page)).toHaveCount(0);

		await set_year_of_settlement(desk, data.year);
		await expect(item_codes(page)).toHaveText(containing(data.items));
	});

	test("a new customer keeps the items and quantities", async ({ desk, page }) => {
		await desk.login(data.regional_user);
		await desk.new_form("Sales Order");
		await form_is_settled(page);
		await expect(desk.get_field("customer", "Link")).toHaveValue(
			data.regional_office_customer,
		);
		await expect(item_codes(page)).toHaveText(containing(data.items));
		await set_qty(desk, page, 2, 3);

		await replace_customer(desk, data.customer);
		await form_is_settled(page);

		await expect(item_codes(page)).toHaveText(containing(data.items));
		await expect.poll(() => quantities(page)).toEqual([0, 3]);
	});

	test("save removes the rows with quantity 0", async ({ desk, page }) => {
		await desk.login(data.local_user);
		await desk.new_form("Sales Order");
		await form_is_settled(page);
		await expect(item_codes(page)).toHaveText(containing(data.items));

		await set_qty(desk, page, 2, 3);
		await save(desk);

		await expect(item_codes(page)).toHaveText(containing([data.items[1]]));
	});
});

function item_codes(page) {
	return page.locator(
		'.frappe-control[data-fieldname="items"] .grid-body .grid-static-col[data-fieldname="item_code"]',
	);
}

function quantities(page) {
	return page.evaluate(() => cur_frm.doc.items.map((row) => row.qty));
}

function containing(codes) {
	// A user who can read the items sees the item name after the item code.
	// A row in edit mode also shows the texts of its input.
	return codes.map((code) => new RegExp(`\\b${code}\\b`));
}

function count_prefills(page) {
	const prefills = { count: 0 };
	page.on("request", (request) => {
		if (request.url().endsWith(ITEM_QUERY)) {
			prefills.count += 1;
		}
	});
	return prefills;
}

async function form_is_settled(page) {
	// ERPNext sets its own item query when the form opens. LANDA replaces it a moment later.
	// Until then, the items are not filtered by year.
	const has_landa_item_query = () =>
		page.evaluate(() => {
			const item_code = cur_frm.fields_dict.items.grid.get_field("item_code");
			return "valid_from_year" in item_code.get_query(cur_frm.doc).filters;
		});
	await expect.poll(has_landa_item_query).toBe(true);

	await requests_are_done(page);
}

async function requests_are_done(page) {
	// A response refreshes the form and would discard new input. It can also start the
	// next request. Wait until no request is open for a moment.
	const is_idle = () => {
		window.idle_polls = frappe.request.ajax_count ? 0 : (window.idle_polls || 0) + 1;
		return window.idle_polls >= 5;
	};
	await page.waitForFunction(is_idle, null, { polling: 100 });
}

async function set_year_of_settlement(desk, year) {
	const input = desk.get_field("year_of_settlement", "Int");
	await input.fill(String(year));
	await input.blur();
	await expect(input).toHaveValue(String(year));
}

async function replace_customer(desk, customer) {
	// `desk.fill_field` does not replace the existing value of a Link field.
	const input = desk.get_field("customer", "Link");
	const first_option = input.locator("xpath=..").getByRole("option").first();
	// A late response to an earlier change can refresh the form and restore the old value.
	await expect(async () => {
		await input.fill(customer);
		await expect(first_option).toContainText(customer, { timeout: 3000 });
	}).toPass();
	await input.press("Enter");
	await input.blur();
	await expect(input).toHaveValue(customer);
}

async function set_qty(desk, page, row_idx, qty) {
	// ERPNext gets the pricing rules for the new quantity and refreshes the form.
	const priced = page.waitForResponse((response) =>
		response.url().endsWith("pricing_rule.apply_pricing_rule"),
	);
	await desk.get_table_field("items", row_idx, "qty").click();
	const input = desk.get_table_field("items", row_idx, "qty");
	await input.fill(String(qty));
	await input.blur();
	await priced;
	await requests_are_done(page);
}

async function save(desk) {
	const response = await desk.save();
	expect(response.status(), await response.text()).toBe(200);
}
