import json

from brain.specification.generator import LivingSpecificationGenerator
from brain.specification.models import LivingSpecification


def test_export_dict():
    spec = LivingSpecification(project_name="Test Project")
    data = LivingSpecificationGenerator.export_dict(spec)
    assert isinstance(data, dict)
    assert data["project_name"] == "Test Project"
    assert "last_updated" in data

def test_export_json():
    spec = LivingSpecification(project_name="Test Project")
    json_str = LivingSpecificationGenerator.export_json(spec)
    assert isinstance(json_str, str)
    data = json.loads(json_str)
    assert data["project_name"] == "Test Project"

def test_summary():
    spec = LivingSpecification(project_name="Test Project", vision="Great Vision")
    summary = LivingSpecificationGenerator.summary(spec)
    assert "Test Project" in summary
    assert "Great Vision" in summary

def test_statistics():
    spec = LivingSpecification(goals=["G1"], success_criteria=["SC1", "SC2"])
    stats = LivingSpecificationGenerator.statistics(spec)
    assert stats["goals_count"] == 1
    assert stats["success_criteria_count"] == 2
