/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";

export class SadayaLangsungDashboard extends Component {
    setup() {
        this.action = useService("action");
    }

    openPaket() {
        this.action.doAction("sadaya_langsung.action_sadaya_langsung_paket");
    }

    openKontrak() {
        this.action.doAction("sadaya_langsung.action_sadaya_langsung_kontrak");
    }
}

SadayaLangsungDashboard.template = "sadaya_langsung.Dashboard";

registry.category("actions").add("sadaya_langsung_dashboard_action", SadayaLangsungDashboard);
