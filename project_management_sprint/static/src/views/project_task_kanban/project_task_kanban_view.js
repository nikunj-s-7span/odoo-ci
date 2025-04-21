/** @odoo-module */

import { registry } from "@web/core/registry";
import { projectTaskKanbanView } from "@project/views/project_task_kanban/project_task_kanban_view";
import { ExtendedProjectTaskKanbanRenderer } from './project_task_kanban_renderer';

export const extendedProjectTaskKanbanView = {
    ...projectTaskKanbanView,
    Renderer: ExtendedProjectTaskKanbanRenderer,
};

registry.category('views').add('extended_project_task_kanban', extendedProjectTaskKanbanView);