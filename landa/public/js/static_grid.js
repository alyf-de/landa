export function render_static_grid({ id, label, data = [], columns = [] }) {
	const rows = data.map((row) => render_static_grid_row(row, columns)).join("");

	// Copying the HTML structure from frappe/frappe/public/js/frappe/form/grid.js here
	// to make custom read-only data look like the other grids.
	return `
	<div class="grid-field">
		<label class="control-label" for="${frappe.utils.escape_html(id)}">
			${frappe.utils.escape_html(label)}
		</label>
		<div class="form-grid-container" id="${frappe.utils.escape_html(id)}">
			<div class="form-grid">
				<div class="grid-heading-row">
					<div class="grid-row">
						<div class="data-row row">
							${columns.map((column) => render_static_grid_heading(column, columns)).join("")}
						</div>
					</div>
				</div>
				<div class="grid-body">
					<div class="rows">${rows}</div>
					${data.length ? "" : render_static_grid_empty_state()}
				</div>
			</div>
		</div>
	</div>`;
}

function render_static_grid_row(row, columns) {
	return `<div class="grid-row">
		<div class="data-row row">
			${columns.map((column) => render_static_grid_cell(row, column, columns)).join("")}
		</div>
	</div>`;
}

function render_static_grid_heading(column, columns) {
	return `<div
		class="${get_static_grid_column_class(column, columns)}"
		data-fieldname="${frappe.utils.escape_html(column.fieldname)}"
		data-fieldtype="${frappe.utils.escape_html(column.fieldtype || "Data")}"
	>
		<div class="static-area ellipsis">${frappe.utils.escape_html(column.label)}</div>
	</div>`;
}

function render_static_grid_cell(row, column, columns) {
	return `<div
		class="${get_static_grid_column_class(column, columns)}"
		data-fieldname="${frappe.utils.escape_html(column.fieldname)}"
		data-fieldtype="${frappe.utils.escape_html(column.fieldtype || "Data")}"
	>
		<div class="static-area ellipsis">${render_static_grid_value(row, column)}</div>
	</div>`;
}

function render_static_grid_value(row, column) {
	if (column.formatter) {
		return column.formatter(get_static_grid_value(row, column), row, column);
	}

	const value = get_static_grid_value(row, column);
	if (value == null) {
		return "";
	}

	if (column.fieldtype === "Link" && column.route) {
		return `<a
			href="${frappe.utils.escape_html(get_static_grid_url(row, column))}"
			target="_blank"
			rel="noopener noreferrer"
		>
			${frappe.utils.escape_html(String(value))}
		</a>`;
	}

	return frappe.utils.escape_html(String(value));
}

function get_static_grid_value(row, column) {
	if (typeof column.value === "function") {
		return column.value(row);
	}

	return row[column.value || column.fieldname];
}

function get_static_grid_url(row, column) {
	const route = typeof column.route === "function" ? column.route(row) : column.route;
	return frappe.router.make_url(route);
}

function get_static_grid_column_class(column, columns) {
	const width = column.width || Math.floor(12 / columns.length);
	return `col grid-static-col ${column.column_class || `col-xs-${width}`}`;
}

function render_static_grid_empty_state() {
	return `<div class="grid-empty text-center">
		<img
			src="/assets/frappe/images/ui-states/grid-empty-state.svg"
			alt="${frappe.utils.escape_html(__("Grid Empty State"))}"
			class="grid-empty-illustration"
		>
		${frappe.utils.escape_html(__("No Data"))}
	</div>`;
}
