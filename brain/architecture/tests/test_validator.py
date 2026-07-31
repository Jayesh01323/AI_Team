import pytest
from brain.architecture.validator import ArchitectureValidator
from brain.architecture.models import Architecture, Module, Component, Dependency, APIEndpoint, TraceabilityLink

def test_validation_passes():
    arch = Architecture(
        modules=[
            Module(id="m1", name="M1", components=[
                Component(id="c1", name="C1", description="")
            ])
        ]
    )
    result = ArchitectureValidator.validate(arch)
    assert result.is_valid

def test_validation_duplicate_components():
    arch = Architecture(
        modules=[
            Module(id="m1", name="M1", components=[
                Component(id="c1", name="C1", description=""),
                Component(id="c1", name="C1 Duplicate", description="")
            ])
        ]
    )
    result = ArchitectureValidator.validate(arch)
    assert not result.is_valid
    assert any("Duplicate component" in err for err in result.errors)

def test_validation_circular_dependency():
    arch = Architecture(
        modules=[
            Module(id="m1", name="M1", components=[
                Component(id="c1", name="C1", description=""),
                Component(id="c2", name="C2", description="")
            ])
        ],
        dependencies=[
            Dependency(source_id="c1", target_id="c2"),
            Dependency(source_id="c2", target_id="c1")
        ]
    )
    result = ArchitectureValidator.validate(arch)
    assert not result.is_valid
    assert any("Circular dependency" in err for err in result.errors)

def test_validation_invalid_api_module():
    arch = Architecture(
        apis=[APIEndpoint(id="api1", path="/", method="GET", description="", module_id="unknown")]
    )
    result = ArchitectureValidator.validate(arch)
    assert not result.is_valid
    assert any("references unknown module" in err for err in result.errors)

def test_validation_invalid_traceability():
    arch = Architecture(
        traceability_links=[
            TraceabilityLink(source_type="req", source_id="r1", target_type="component", target_id="unknown")
        ]
    )
    result = ArchitectureValidator.validate(arch)
    assert not result.is_valid
    assert any("unknown component" in err for err in result.errors)
