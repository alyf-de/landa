// The fixtures and the Desk helpers come from the Frappe app in the same bench.
import { test as frappe_test, GUEST } from "../../../frappe/playwright/support";

export * from "../../../frappe/playwright/support";

// The test user of Frappe cannot exist in LANDA, because each user needs a LANDA Member.
// Each spec starts as a guest and logs in with `desk.login(user)`.
export const test = frappe_test.extend({ storageState: GUEST });
