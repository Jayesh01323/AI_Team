import shutil
from unittest.mock import patch

import pytest

from brain.project_generator.models import ProjectBlueprint
from brain.project_generator.pipeline import ProjectGenerationPipeline


@pytest.fixture
def temp_workspace(tmp_path):
    ws_dir = tmp_path / "pipeline_workspace"
    ws_dir.mkdir()
    yield str(ws_dir)
    if ws_dir.exists():
        shutil.rmtree(ws_dir)

@pytest.fixture
def valid_blueprint():
    # Requires valid templates to pass Template Resolution, Code Generation, etc.
    # In tests, if we don't have actual templates in registry, we might need a mock,
    # but the pipeline uses the real components. We'll use simple in-memory components
    # to let CodeGenerator generate a valid file. Wait, TemplateResolver reads from TemplateRegistry.
    # We might just use a minimal valid blueprint that doesn't trigger errors, or we mock the registry
    # in the pipeline's resolver for this test.
    # To keep it simple, since we can't easily mock here without patching, let's see if 
    # a basic blueprint works without components if the generator supports empty components.
    return ProjectBlueprint(project_name="TestPipelineApp")

def test_pipeline_missing_templates_fails_gracefully(temp_workspace, valid_blueprint):
    pipeline = ProjectGenerationPipeline()
    with patch.object(pipeline.resolver, 'resolve_templates', side_effect=Exception("Template not found")):
        result = pipeline.generate(valid_blueprint, temp_workspace)
        
    assert result.success is False
    assert result.statistics.total_stages == 1
    assert result.statistics.failed_stages == 1
    assert result.stage_summaries[0].name == "Template Resolution"
    assert result.stage_summaries[0].success is False

def test_pipeline_empty_blueprint(temp_workspace, valid_blueprint):
    pipeline = ProjectGenerationPipeline()
    result = pipeline.generate(valid_blueprint, temp_workspace)
    
    # Validation should fail because an empty project has no files, which might be valid or invalid
    # depending on our validator, but it will definitely run through stage 5 (Repair Planning)
    # and then likely skip Export if invalid, or succeed if valid.
    
    # Actually, if there are no templates, generated_project will be empty. 
    # Assembly will be empty. Validation will be run. If empty is valid, export runs.
    
    assert result.statistics.total_stages >= 5
    
    # Stage ordering should be deterministic
    orders = [s.execution_order for s in result.stage_summaries]
    assert orders == sorted(orders)
    
    # No duplicate stages
    names = [s.name for s in result.stage_summaries]
    assert len(names) == len(set(names))

def test_pipeline_serialization():
    from brain.project_generator.pipeline_models import PipelineResult, ProjectBlueprint
    pr = PipelineResult(blueprint=ProjectBlueprint(project_name="X"))
    d = pr.model_dump()
    assert d["blueprint"]["project_name"] == "X"
    assert d["success"] is False
