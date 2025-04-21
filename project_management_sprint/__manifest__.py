{
    "name": "Project Sprint",
    "version": "18.0.1.0.2",
    "category": "Project",
    "summary": """This app adds sprint functionality to the Odoo Project module,
    enabling efficient task management within fixed timeframes.""",
    "description": """This module enables the sprint functionality,
    inspired by Jira software, into the project module of Odoo. Sprints, fixed
    time periods during which teams tackle tasks from their product backlog, are
    efficiently managed within the Odoo environment.""",
    "author": "7Span",
    "company": "7Span",
    "maintainer": "7Span",
    "website": "https://www.7span.com",
    "depends": ["web", "base", "project", "hr_timesheet"],
    "data": [
        "security/security_groups.xml",
        "security/ir.model.access.csv",
        "views/project_sprint_views.xml",
        "views/project_project_views.xml",
        "views/project_task_views.xml",
        "views/project_task_type_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "project_management_sprint/static/src/views/project_task_kanban/*.js",
            "project_management_sprint/static/src/chatter.xml",
        ],
    },
    "license": "LGPL-3",
}
