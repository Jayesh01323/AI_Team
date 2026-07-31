from typing import List, Dict
from .models import Task
from .dependency_graph import DependencyGraph

class Prioritizer:
    @staticmethod
    def calculate_priorities(tasks: List[Task]) -> None:
        """
        Deterministically calculates and assigns priorities for a list of tasks.
        Uses dependency depth: Tasks that have more tasks depending on them get higher priority.
        """
        if not tasks:
            return
            
        graph = DependencyGraph()
        # Build graph, but we want reverse dependencies to see who depends on who
        task_dict = {t.id: t for t in tasks}
        
        # in_degree here means how many tasks this task depends on
        # we want out_degree: how many tasks depend on this task
        out_degree = {t.id: 0 for t in tasks}
        
        for task in tasks:
            for dep in task.dependencies:
                if dep in out_degree:
                    out_degree[dep] += 1
                    
        # Calculate a deterministic priority score
        # Base priority is 10.0
        # Add 5.0 for each task that directly depends on this task
        # Add complexity factor (higher complexity -> slightly lower priority maybe? Or higher? 
        # Let's say higher complexity adds 0.1 to break ties deterministically)
        
        for task in tasks:
            score = 10.0
            score += out_degree[task.id] * 5.0
            score += task.estimated_complexity * 0.1
            task.priority_score = score

