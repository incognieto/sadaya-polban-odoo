/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class SiPlangDashboard extends Component {
    setup() {
        this.action = useService("action");
    }

    openPaket() {
        this.action.doAction("si_plang.si_plang_paket_action_window");
    }

    openKontrak() {
        this.action.doAction("si_plang.si_plang_kontrak_action_window");
    }
}

SiPlangDashboard.template = "si_plang_dashboard";
registry.category("actions").add("si_plang_dashboard", SiPlangDashboard);
