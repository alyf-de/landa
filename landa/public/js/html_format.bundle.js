import * as prettier from "prettier/standalone";
import * as prettierPluginHtml from "prettier/plugins/html";

window.format_html_source = (source) =>
	prettier.format(source, {
		parser: "html",
		plugins: [prettierPluginHtml],
	});
