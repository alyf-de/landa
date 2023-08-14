import frappe
import requests

FISH_SPECIES = (
	(1, "Aal"),
	(2, "Äsche"),
	(3, "Aland"),
	(4, "Bachforelle"),
	(5, "Bachsaibling"),
	(6, "Barbe"),
	(7, "Barsch"),
	(8, "Bitterling"),
	(9, "Blei"),
	(10, "Döbel"),
	(11, "Edelkrebs"),
	(12, "Elritze"),
	(13, "Flussmuschel"),
	(14, "Flussperlmuschel"),
	(15, "Giebel"),
	(16, "Graskarpfen"),
	(17, "Groppe"),
	(18, "Gründling"),
	(19, "Güster"),
	(20, "Hasel"),
	(21, "Hecht"),
	(22, "Karausche"),
	(23, "Schuppenkarpfen"),
	(24, "Spiegelkarpfen"),
	(25, "Kaulbarsch"),
	(26, "Lachs"),
	(27, "Maifisch"),
	(28, "Maräne groß"),
	(29, "Maräne klein"),
	(30, "Marmorkarpfen"),
	(31, "Meerforelle"),
	(32, "Moderlieschen"),
	(33, "Nase"),
	(34, "Flussneunauge"),
	(35, "Neunstachliger Stichling"),
	(36, "Nordseeschnäpel"),
	(37, "Quappe"),
	(38, "Rapfen"),
	(39, "Regenbogenforelle"),
	(40, "Rotauge (Plötze)"),
	(41, "Rotfeder"),
	(42, "Schlammpeitzger"),
	(43, "Schleie"),
	(44, "Schmerle"),
	(45, "Schneider"),
	(46, "Seeforelle"),
	(47, "Seesaibling"),
	(48, "Silberkarpfen"),
	(49, "Sonnenbarsch"),
	(50, "Steinbeißer"),
	(51, "Stör"),
	(151, "Störhybride / nicht geschonte Störart"),
	(52, "Stromgründling"),
	(53, "Ukelei"),
	(54, "Wels"),
	(55, "Zährte"),
	(56, "Zander"),
	(57, "Zope"),
	(58, "Zwergwels"),
)


def execute():
	for id, name in FISH_SPECIES:
		if not frappe.db.exists("Fish Species", name):
			continue

		image = download_image(f"https://www.angelatlas-sachsen.de/img/fish_big/{id}.png")
		image_url = save_attachment(name, "image", f"{id}_big.png", image)

		thumbnail = download_image(f"https://www.angelatlas-sachsen.de/img/fish_small/{id}.png")
		thumbnail_url = save_attachment(name, "thumbnail", f"{id}_small.png", thumbnail)

		frappe.db.update("Fish Species", name, {"image": image_url, "thumbnail": thumbnail_url})


def download_image(url: str) -> bytes:
	r = requests.get(url, stream=True)
	return r.content if r.status_code == 200 else None


def save_attachment(
	fish_species: str, attached_to_field: str, file_name: str, image: bytes
) -> str:
	f = frappe.new_doc("File")
	f.file_name = file_name
	f.is_private = 0
	f.attached_to_doctype = "Fish Species"
	f.attached_to_name = fish_species
	f.attached_to_field = attached_to_field
	f.content = image
	f.save()

	return f.file_url
