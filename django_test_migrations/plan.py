from django.apps import apps
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations import Migration
from django.db.migrations.graph import Node
from django.db.migrations.loader import MigrationLoader

from django_test_migrations.exceptions import MigrationNotInPlan
from django_test_migrations.logic.migrations import normalize
from django_test_migrations.types import MigrationPlan, MigrationTarget, MigrationSpec


def all_migrations(
    database: str = DEFAULT_DB_ALIAS,
    app_names: list[str] | None = None,
) -> list[Node]:
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
            key for key in loader.graph.leaf_nodes() if key[0] in app_names
        ]
    else:
        targets = loader.graph.leaf_nodes()
    return _generate_plan(targets, loader)


def nodes_to_tuples(nodes: list[Node]) -> list[tuple[str, str]]:
    """Utility function to transform nodes to tuples."""
    return [(node[0], node[1]) for node in nodes]


def _validate_app_names(app_names: list[str]) -> None:
    """
    Validates the provided app names.

    Raises ```LookupError`` when incorrect app names are provided.
    """
    for app_name in app_names:
        apps.get_app_config(app_name)


def _generate_plan(
    targets: list[Node],
    loader: MigrationLoader,
) -> list[Node]:
    plan = []
    seen: set[Node] = set()

    # Generate the plan
    for target in targets:
        for migration in loader.graph.forwards_plan(target):
            if migration not in seen:
                node = loader.graph.node_map[migration]
                plan.append(node)
                seen.add(migration)
    return plan


def find_maximum_plan_depth(targets: MigrationSpec, plan: MigrationPlan) -> MigrationTarget|None:
    """Find migration in plan at maximum depth before exceeding migration targets"""
    targets = normalize(targets)
    seen = {target: target[1] is None for target in targets}
    max_index = -1
    end = False

    for index, migration in enumerate(plan):
        for target in targets:
            # to_check[1] = None to match against any migration in that app if already seen target
            to_check = (target[0], None if seen[target] else target[1])
            if _filter_predicate(to_check, migration[0]):
                if seen[target]:
                    # reached the next migration after one of our targets
                    end = True
                    break
                else:
                    # we have reached a target migration and can proceed until the next
                    # migration from this app
                    seen[target] = True
        if end:
            break
        else:
            max_index += 1

    if max_index < 0:
        # all migrations in this plan exceed targets
        return None

    max_migration = plan[max_index][0]
    return max_migration.app_label, max_migration.name


def broad_plan(targets: MigrationSpec, loader: MigrationLoader) -> list[MigrationTarget]:
    """Generates the broadest possible plan without passing target migrations"""
    targets = normalize(targets)
    loader.build_graph()

    leaf_nodes = loader.graph.leaf_nodes()
    plan_nodes = set()

    for leaf_node in leaf_nodes:
        plan_node = loader.graph.node_map[leaf_node]  # default is to use this leaf
        seen = []
        def check_parents(node: Node) -> None:
            # check if a given node is our target; if not, check its parents recursively
            seen.append(node)
            if any(_filter_predicate(target, loader.graph.nodes[node.key]) for target in targets):
                # the starting leaf node results in a target migration being applied
                # name the target migration as the leaf node instead
                nonlocal plan_node
                plan_node = node
                return
            else:
                for parent in node.parents:
                    if parent not in seen:
                        check_parents(parent)
        check_parents(plan_node)
        plan_nodes.add(plan_node)

    return [node.key for node in plan_nodes]


def truncate_plan(
    targets: list[MigrationTarget],
    plan: MigrationPlan,
) -> MigrationPlan:
    """Truncate migrations ``plan`` up to ``targets``.

    This method is used mainly to truncate full/clean migrations plan
    to get as broad plan as possible.
    By "broad" plan we mean plan with all targets migrations included
    as well as all older migrations not related with targets.
    "Broad" plan is needed mostly to make ``Migrator`` API developers'
    friendly, just to not force developers to include migrations targets
    for all other models they want to use in test (e.g. to setup some
    model instances) in ``migrate_from``.
    Such plan will also produce database state really similar to state
    from our production environment just before new migrations are applied.
    Migrations plan for targets generated by Django's
    ``MigrationExecutor.migration_plan`` is minimum plan needed to apply
    targets migrations, it includes only migrations targets with all its
    dependencies, so it doesn't fit to our approach, that's why following
    function is needed.

    """
    if not targets or not plan:
        return plan

    target_max_index = max(_get_index(target, plan) for target in targets)
    return plan[: (target_max_index + 1)]


def _get_index(target: MigrationTarget, plan: MigrationPlan) -> int:
    try:
        index = next(
            index
            for index, (migration, _) in enumerate(plan)
            if _filter_predicate(target, migration)
        )
    except StopIteration:
        raise MigrationNotInPlan(target) from None
    return index - (target[1] is None)


def _filter_predicate(target: MigrationTarget, migration: Migration) -> bool:
    # when ``None`` passed as migration name then initial migration from
    # target's app will be chosen and handled properly in ``_get_index``
    # so in final all target app migrations will be excluded from plan
    index = 2 - (target[1] is None)
    return (migration.app_label, migration.name)[:index] == target[:index]
