from brain.planner.models import Epic, Feature, Milestone, Plan, Task
from brain.planner.validator import PlanValidator


def test_validation_passes_on_valid_plan():
    plan = Plan(
        milestones=[
            Milestone(id="m1", title="M1", epics=[
                Epic(id="e1", title="E1", features=[
                    Feature(id="f1", title="F1", tasks=[
                        Task(id="t1", title="T1", execution_order=0)
                    ])
                ])
            ])
        ]
    )
    result = PlanValidator.validate(plan)
    assert result.is_valid

def test_validation_fails_on_duplicate_tasks():
    plan = Plan(
        milestones=[
            Milestone(id="m1", title="M1", epics=[
                Epic(id="e1", title="E1", features=[
                    Feature(id="f1", title="F1", tasks=[
                        Task(id="t1", title="T1"),
                        Task(id="t1", title="T1 Duplicate")
                    ])
                ])
            ])
        ]
    )
    result = PlanValidator.validate(plan)
    assert not result.is_valid
    assert any("Duplicate" in err for err in result.errors)

def test_validation_fails_on_cycle():
    plan = Plan(
        milestones=[
            Milestone(id="m1", title="M1", epics=[
                Epic(id="e1", title="E1", features=[
                    Feature(id="f1", title="F1", tasks=[
                        Task(id="t1", title="T1", dependencies=["t2"]),
                        Task(id="t2", title="T2", dependencies=["t1"])
                    ])
                ])
            ])
        ]
    )
    result = PlanValidator.validate(plan)
    assert not result.is_valid
    assert any("cycle" in err for err in result.errors)

def test_validation_fails_on_unknown_dependency():
    plan = Plan(
        milestones=[
            Milestone(id="m1", title="M1", epics=[
                Epic(id="e1", title="E1", features=[
                    Feature(id="f1", title="F1", tasks=[
                        Task(id="t1", title="T1", dependencies=["t_unknown"]),
                    ])
                ])
            ])
        ]
    )
    result = PlanValidator.validate(plan)
    assert not result.is_valid
    assert any("unknown" in err for err in result.errors)
