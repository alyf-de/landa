// Copyright (c) 2016, Real Experts GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Current Member Data"] = {
    "filters": [
        {
            "fieldname": "organization",
            "fieldtype": "Link",
            "options": "Organization",
            "label": __("Organization"),
            "mandatory": 0,
            "wildcard_filter": 0,
            "default": frappe.defaults.get_user_default("Organization"),
        },
    ],
    onload: function (query_report) {
        const b = cur_page.page.page.wrapper.find(".sub-heading");
        b.html(`
        <p>Dieser Bericht gibt einen schnellen Überblick über die Daten, die bei einer Fangbuchausgabe erfasst werden. Dazu gehören vor allem die primär genutzte Adresse sowie der zuletzt ausgegebene Erlaubnisschein.</p>
        <p>Um alle anderen Daten eines Mitglieds zu sehen (z. B. auch Telefonnummer und Mitgliedsfunktion) nutzen Sie bitte stattdessen <a href="/app/query-report/Members%20with%20Member%20Functions" target=_blank style="color: blue;">diesen vollständigen Bericht</a>!</p>
        <p>Dieser Bericht dient außerdem als Vorlage für den Mitgliedsdatenimport mit Hilfe des <a href="/app/data-import" target=_blank style="color: blue;">Datenimport Werkzeugs</a>. Sehen Sie sich bitte unbedingt vor der ersten Benutzung <a href="https://youtu.be/CZRcqaMOYso" target=_blank style="color: blue;">dieses Video</a> an.</p>
        <p>Über den Mitgliedsdatenimport können sowohl Daten geändert als auch Daten hinzugefügt werden. Um eine Adresse zu ändern, ändern Sie die Angaben wie die Adresszeile und Postleitzahl, aber lassen Sie die “Eindeutige Adress-Identifikation” gleich. Wenn Sie die alte Adresse erhalten und eine neue Adresse hinzufügen möchten, lassen sie die “Eindeutige Adress-Identifikation” leer und ändern Sie die Angaben wie die Adresszeile und Postleitzahl! Gleiches gilt für den Erlaubnisschein. Wird beim Import die “Eindeutige Erlaubnisschein Identifikation” leer gelassen und Angaben wie Erlaubnisscheinnummer, Mitglied und Jahr ausgefüllt, erstellt das System beim Import einen neuen Erlaubnisschein. </p>
        `).toggleClass("hide", false);
    }
};
