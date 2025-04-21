/** @odoo-module */

import { ProjectTaskKanbanRenderer } from '@project/views/project_task_kanban/project_task_kanban_renderer';
import { ProjectTaskKanbanRecord } from '@project/views/project_task_kanban/project_task_kanban_record';
import { ExtendedProjectTaskKanbanHeader } from './project_task_kanban_header';
import { useService } from '@web/core/utils/hooks';
import { onWillStart } from "@odoo/owl";
import { user } from "@web/core/user";

export class ExtendedProjectTaskKanbanRenderer extends ProjectTaskKanbanRenderer {
    static components = {
        ...ProjectTaskKanbanRenderer.components,
        KanbanHeader: ExtendedProjectTaskKanbanHeader,
    };

    setup() {
        super.setup();
        this.action = useService('action');
    }
}
