import pytest
import json
from brain.architecture.models import Architecture, Module, Component, Dependency, APIEndpoint, DataModel
from brain.architecture.exporter import ArchitectureExporter

def test_export_dict():
    arch = Architecture(project_name="Arch Test")
    d = ArchitectureExporter.to_dict(arch)
    assert d["project_name"] == "Arch Test"

def test_export_json():
    arch = Architecture(project_name="Arch Test")
    j = ArchitectureExporter.to_json(arch)
    assert "Arch Test" in j
    assert json.loads(j)["project_name"] == "Arch Test"

def test_summary():
    arch = Architecture(project_name="Arch Test")
    arch.modules.append(Module(id="m1", name="M1"))
    s = ArchitectureExporter.summary(arch)
    assert "Arch Test" in s
    assert "Modules: 1" in s

def test_statistics():
    arch = Architecture(
        modules=[Module(id="m1", name="M1", components=[Component(id="c1", name="C1", description="")])],
        apis=[APIEndpoint(id="a1", path="/", method="GET", description="")],
        data_models=[DataModel(id="d1", name="D1")],
        dependencies=[Dependency(source_id="c1", target_id="c2")]
    )
    stats = ArchitectureExporter.statistics(arch)
    assert stats["modules_count"] == 1
    assert stats["components_count"] == 1
    assert stats["apis_count"] == 1
    assert stats["data_models_count"] == 1
    assert stats["dependencies_count"] == 1
