from brain.project_generator.template_models import (
    ResolvedTemplateSet,
    TemplateMetadata,
    TemplateValidationResult,
)


def test_template_metadata_defaults():
    t = TemplateMetadata(id="t1", name="Template 1", category="base")
    assert t.id == "t1"
    assert t.supported_languages == []
    assert t.priority == 0
    assert t.version == "1.0.0"

def test_resolved_template_set_export():
    t = TemplateMetadata(id="t1", name="Template 1", category="base")
    rts = ResolvedTemplateSet(
        selected_templates=[t],
        selection_rationale={"t1": "reason"},
        dependency_ordering=["t1"],
        validation_result=TemplateValidationResult(is_valid=True)
    )
    
    d = rts.export_dict()
    assert "selected_templates" in d
    assert d["selected_templates"][0]["id"] == "t1"
    
    j = rts.export_json()
    assert "t1" in j
    
    s = rts.summary()
    assert "t1" in s
    assert "Valid: True" in s
