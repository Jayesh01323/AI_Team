from brain.project_generator.code_renderer import CodeRenderer


def test_code_renderer():
    renderer = CodeRenderer()
    raw = "Hello {{NAME}}! Welcome to {{PROJECT}}."
    vars = {"NAME": "Alice", "PROJECT": "Wonderland"}
    
    rendered = renderer.render(raw, vars)
    assert rendered == "Hello Alice! Welcome to Wonderland."

def test_code_renderer_missing_var():
    renderer = CodeRenderer()
    raw = "Hello {{NAME}}! Welcome to {{PROJECT}}."
    vars = {"NAME": "Alice"}
    
    rendered = renderer.render(raw, vars)
    assert rendered == "Hello Alice! Welcome to {{PROJECT}}."
