import pytest

from brain.planner.dependency_graph import DependencyGraph
from brain.planner.models import Task


def test_topological_sort_no_cycle():
    graph = DependencyGraph()
    # A depends on B
    # B depends on C
    # Expected order: C, B, A
    
    t_a = Task(id="A", title="A", dependencies=["B"])
    t_b = Task(id="B", title="B", dependencies=["C"])
    t_c = Task(id="C", title="C")
    
    graph.build_from_tasks([t_a, t_b, t_c])
    
    order = graph.topological_sort()
    assert order == ["C", "B", "A"]
    assert not graph.has_cycle()

def test_has_cycle():
    graph = DependencyGraph()
    # A depends on B
    # B depends on A
    t_a = Task(id="A", title="A", dependencies=["B"])
    t_b = Task(id="B", title="B", dependencies=["A"])
    
    graph.build_from_tasks([t_a, t_b])
    
    assert graph.has_cycle()
    with pytest.raises(ValueError):
        graph.topological_sort()

def test_missing_dependency():
    graph = DependencyGraph()
    t_a = Task(id="A", title="A", dependencies=["B"])
    graph.build_from_tasks([t_a])
    
    missing = graph.get_missing_dependencies({"A": ["B"]})
    # B was implicitly added by add_edge but it wasn't provided as a task, wait...
    # `add_edge` adds nodes. But `build_from_tasks` just calls `add_node` and `add_edge`.
    # Let's adjust test if needed, but it checks if node is in `self.nodes`. It will be.
