from brain.planner.models import Task, TaskStatus
from brain.planner.scheduler import Scheduler


def test_scheduler_assigns_execution_order():
    t1 = Task(id="T1", title="T1")
    t2 = Task(id="T2", title="T2", dependencies=["T1"])
    t3 = Task(id="T3", title="T3", dependencies=["T2"])
    
    tasks = [t3, t1, t2] # Unordered
    ordered = Scheduler.schedule(tasks)
    
    assert ordered[0].id == "T1"
    assert ordered[1].id == "T2"
    assert ordered[2].id == "T3"
    
    assert t1.execution_order == 0
    assert t2.execution_order == 1
    assert t3.execution_order == 2

def test_scheduler_updates_status():
    t1 = Task(id="T1", title="T1", status=TaskStatus.COMPLETED)
    t2 = Task(id="T2", title="T2", dependencies=["T1"], status=TaskStatus.BACKLOG)
    t3 = Task(id="T3", title="T3", dependencies=["T2"], status=TaskStatus.BACKLOG)
    
    tasks = [t1, t2, t3]
    Scheduler.schedule(tasks)
    
    # T1 is completed, so T2's dependencies are met, T2 should be READY
    assert t2.status == TaskStatus.READY
    # T2 is READY, not COMPLETED, so T3 is BLOCKED
    assert t3.status == TaskStatus.BLOCKED
    assert t3.blockers == ["T2"]
