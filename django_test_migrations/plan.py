from typing import List, Optional, Set, Tuple

from django.apps import apps
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.graph import Node
from django.db.migrations.loader import MigrationLoader


def all_migrations(
    database: str = DEFAULT_DB_ALIAS,
    app_names: Optional[List[str]] = None,
) -> List[Node]:
    """
    Returns the sorted list of migrations nodes.

    The order is the same as when migrations are applied.

    When you might need this function?
    When you are testing the migration order.

    For example, imagine that you have a direct dependency:
    ``main_app.0002_migration`` and ``other_app.0001_initial``
    where ``other_app.0001_initial`` relies on the model or field
    introduced in ``main_app.0002_migration``.

    You can use ``dependencies`` field
    to ensure that everything works correctly.

    But, sometimes migrations are squashed,
    sometimes they are renamed, refactored, and moved.

    It would be better to have a test that will ensure
    that ``other_app.0001_initial`` comes after ``main_app.0002_migration``.
    And everything works as expected.
    """
    loader = MigrationLoader(connections[database])

    if app_names:
        _validate_app_names(app_names)
        targets = [
            key
            for key in loader.graph.leaf_nodes()
            if key[0] in app_names
        ]
    else:
        targets = loader.graph.leaf_nodes()
    return _generate_plan(targets, loader)


def nodes_to_tuples(nodes: List[Node]) -> List[Tuple[str, str]]:
    """Utility function to transform nodes to tuples."""
    return [
        (node[0], node[1])
        for node in nodes
    ]


def _validate_app_names(app_names: List[str]) -> None:
    """
    Validates the provided app names.

    Raises ```LookupError`` when incorrect app names are provided.
    """
    for app_name in app_names:
        apps.get_app_config(app_name)


def _generate_plan(
    targets: List[Node],
    loader: MigrationLoader,
) -> List[Node]:
    plan = []
    seen: Set[Node] = set()

    # Generate the plan
    for target in targets:
        for migration in loader.graph.forwards_plan(target):
            if migration not in seen:
                node = loader.graph.node_map[migration]
                plan.append(node)
                seen.add(migration)
    return plan
