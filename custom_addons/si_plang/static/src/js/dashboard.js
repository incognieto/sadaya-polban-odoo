/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";

export class SiPlangDashboard extends Component {
    setup() {
        this.action = useService("action");
    }

    openPaket() {
        this.action.doAction("si_plang.action_si_plang_paket");
    }

    openKontrak() {
        this.action.doAction("si_plang.action_si_plang_kontrak");
    }
}

SiPlangDashboard.template = "si_plang.Dashboard";

registry.category("actions").add("si_plang_dashboard_action", SiPlangDashboard);
