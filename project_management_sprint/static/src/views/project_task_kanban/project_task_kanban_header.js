/** @odoo-module **/

import { ProjectTaskKanbanHeader } from "@project/views/project_task_kanban/project_task_kanban_header";
import { user } from "@web/core/user";
import { onWillStart } from "@odoo/owl";

export class ExtendedProjectTaskKanbanHeader extends ProjectTaskKanbanHeader {
    setup() {
        super.setup();

        // Override the onWillStart method to use our custom group
        onWillStart(async () => {
            if (this.props.list.isGroupedByStage) { // no need to check it if not grouped by stage
                this.isProjectManager = await user.hasGroup('project_management_sprint.group_unrestricted_admin');
                console.log(this.isProjectManager)
            }
        });
    }

    /**
     * @override
     * Add support for archiving groups based on project manager permissions
     */
    canArchiveGroup(group) {
        return super.canArchiveGroup(group) && (!this.props.list.isGroupedByStage || this.isProjectManager);
    }
}