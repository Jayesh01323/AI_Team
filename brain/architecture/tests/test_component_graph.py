import pytest
from brain.architecture.component_graph import ComponentGraph
from brain.architecture.models import Component, Dependency

def test_component_graph_no_cycle():
    graph = ComponentGraph()
    c1 = Component(id="c1", name="C1", description="")
    c2 = Component(id="c2", name="C2", description="")
    dep = Dependency(source_id="c1", target_id="c2")
    
    graph.build_from_architecture([c1, c2], [dep])
    assert not graph.has_cycle()

def test_component_graph_cycle():
    graph = ComponentGraph()
    c1 = Component(id="c1", name="C1", description="")
    c2 = Component(id="c2", name="C2", description="")
    dep1 = Dependency(source_id="c1", target_id="c2")
    dep2 = Dependency(source_id="c2", target_id="c1")
    
    graph.build_from_architecture([c1, c2], [dep1, dep2])
    assert graph.has_cycle()
    
def test_component_graph_invalid_dep():
    graph = ComponentGraph()
    c1 = Component(id="c1", name="C1", description="")
    dep1 = Dependency(source_id="c1", target_id="c2") # c2 doesn't exist
    with pytest.raises(ValueError):
        graph.build_from_architecture([c1], [dep1])

def test_get_dependencies():
    graph = ComponentGraph()
    c1 = Component(id="c1", name="C1", description="")
    c2 = Component(id="c2", name="C2", description="")
    dep = Dependency(source_id="c1", target_id="c2")
    graph.build_from_architecture([c1, c2], [dep])
    assert graph.get_dependencies("c1") == ["c2"]
    assert graph.get_dependents("c2") == ["c1"]
