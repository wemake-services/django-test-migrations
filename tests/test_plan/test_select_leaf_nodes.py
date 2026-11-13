import pytest
from django.db import connections, DEFAULT_DB_ALIAS
from django.db.migrations.loader import MigrationLoader

from django_test_migrations.plan import (
    _select_root_nodes,
    _check_if_can_process_child,
    select_leaf_nodes
)


@pytest.mark.django_db
def test_select_root_nodes_dependencies():
    # should not pick auth 0001 since it depends on contenttypes 0001
    loader = MigrationLoader(connections[DEFAULT_DB_ALIAS])
    roots = [*_select_root_nodes(loader.graph, [])]
    assert ('auth', '0001_initial') not in roots
    assert ('contenttypes', '0001_initial') in roots


@pytest.mark.django_db
def test_select_root_nodes_none_target():
    # should not pick another_app 0001 since None target
    loader = MigrationLoader(connections[DEFAULT_DB_ALIAS])
    roots = [*_select_root_nodes(loader.graph, ['another_app'])]
    assert ('another_app', '0001_initial') not in roots


@pytest.mark.django_db
def test_can_check_child():
    # should select child since no concerns
    graph = MigrationLoader(connections[DEFAULT_DB_ALIAS]).graph
    node = graph.node_map[('another_app', '0001_initial')]
    assert _check_if_can_process_child(node, set(), [], [])


@pytest.mark.django_db
def test_can_check_child_seen():
    # should not select child since already seen
    graph = MigrationLoader(connections[DEFAULT_DB_ALIAS]).graph
    node = graph.node_map[('another_app', '0001_initial')]
    assert not _check_if_can_process_child(node, {node.key}, [], [])


@pytest.mark.django_db
def test_can_check_child_parent_not_seen():
    # should not select child since parent not yet checked
    graph = MigrationLoader(connections[DEFAULT_DB_ALIAS]).graph
    node = graph.node_map[('another_app', '0002_add_field')]
    assert not _check_if_can_process_child(node, set(), [], [])


@pytest.mark.django_db
def test_can_check_child_parent_target():
    # should not select child since parent is in app and is a target
    graph = MigrationLoader(connections[DEFAULT_DB_ALIAS]).graph
    node = graph.node_map[('another_app', '0002_add_field')]
    assert not _check_if_can_process_child(node, node.parents, [], [('another_app', '0001_initial')])


@pytest.mark.django_db
def test_can_check_child_parent_target():
    # should not select child since is from an app with a None target
    graph = MigrationLoader(connections[DEFAULT_DB_ALIAS]).graph
    node = graph.node_map[('another_app', '0003_converge')]
    assert not _check_if_can_process_child(node, node.parents, ['another_app'], [])


@pytest.mark.django_db
def test_select_leaf_nodes_no_targets():
    # should select another_app 0003 since no targets and it has no children
    graph = MigrationLoader(connections[DEFAULT_DB_ALIAS]).graph
    assert ('another_app', '0003_converge') in select_leaf_nodes([], graph)


@pytest.mark.django_db
def test_select_leaf_nodes_same_app_targets():
    # should not select another_app 0003 since 0001 is a target
    graph = MigrationLoader(connections[DEFAULT_DB_ALIAS]).graph
    nodes = select_leaf_nodes([('another_app', '0001_initial')], graph)
    assert ('another_app', '0003_converge') not in nodes
    assert ('another_app', '0001_initial') in nodes


@pytest.mark.django_db
def test_select_leaf_nodes_cross_app_parent_targets():
    # should select another_app 0003 even though main_app 0001 is a target
    graph = MigrationLoader(connections[DEFAULT_DB_ALIAS]).graph
    nodes = select_leaf_nodes([('main_app', '0001_initial')], graph)
    assert ('another_app', '0003_converge') in nodes


@pytest.mark.django_db
def test_does_not_select_target_with_leaf_child():
    # should not select target main_app 0001 since another leaf is dependent on it
    graph = MigrationLoader(connections[DEFAULT_DB_ALIAS]).graph
    nodes = select_leaf_nodes([('main_app', '0001_initial')], graph)
    assert ('main_app', '0001_initial') not in nodes


@pytest.mark.django_db
def test_does_not_exceed_target_with_cross_app_dependency():
    # should not select another_app 0003 even though 0002 is a target
    # 0003 depends on main_app 0001, this ensures the branch is not followed
    graph = MigrationLoader(connections[DEFAULT_DB_ALIAS]).graph
    nodes = select_leaf_nodes([('another_app', '0002_add_field')], graph)
    assert ('another_app', '0003_converge') not in nodes
    assert ('another_app', '0002_add_field') in nodes
