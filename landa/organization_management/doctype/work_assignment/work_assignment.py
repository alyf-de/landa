# Copyright (c) 2026, ALYF GmbH and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class WorkAssignment(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from landa.organization_management.doctype.work_assignment_member.work_assignment_member import (
			WorkAssignmentMember,
		)

		date: DF.Date
		description: DF.SmallText | None
		location: DF.Data | None
		members: DF.Table[WorkAssignmentMember]
		naming_series: DF.Literal["WORK-.YYYY.-.#####"]
		organization: DF.Link
		organization_name: DF.Data | None
		planned_duration: DF.Float
		title: DF.Data
		water_body: DF.Link | None
		water_body_title: DF.Data | None
	# end: auto-generated types

