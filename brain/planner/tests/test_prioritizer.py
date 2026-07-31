import pytest
from brain.planner.prioritizer import Prioritizer
from brain.planner.models import Task

def test_prioritizer():
    # T1 has 2 tasks depending on it
    # T2 has 1 task depending on it
    # T3 has 0
    t1 = Task(id="T1", title="T1")
    t2 = Task(id="T2", title="T2", dependencies=["T1"])
    t3 = Task(id="T3", title="T3", dependencies=["T1", "T2"])
    
    tasks = [t1, t2, t3]
    Prioritizer.calculate_priorities(tasks)
    
    # T1 out_degree = 2 (T2, T3)
    # T2 out_degree = 1 (T3)
    # T3 out_degree = 0
    
    # Base 10 + (2 * 5) + (1 * 0.1) = 20.1
    assert t1.priority_score > t2.priority_score
    assert t2.priority_score > t3.priority_score
