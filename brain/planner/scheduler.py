from typing import List
from .models import Task, TaskStatus
from .dependency_graph import DependencyGraph
from .prioritizer import Prioritizer

class Scheduler:
    @staticmethod
    def schedule(tasks: List[Task]) -> List[Task]:
        """
        Assigns execution order to tasks based on topological sorting.
        Also calculates priorities.
        """
        if not tasks:
            return tasks

        graph = DependencyGraph()
        graph.build_from_tasks(tasks)
        
        ordered_ids = graph.topological_sort()
        
        # Calculate priorities
        Prioritizer.calculate_priorities(tasks)
        
        # We need to sort by topological order, but within the same topological level, 
        # we can sort by priority. To achieve this simply and deterministically, 
        # topological_sort already gives a valid execution order. 
        # Let's map topological order to execution_order.
        
        task_dict = {t.id: t for t in tasks}
        
        for i, task_id in enumerate(ordered_ids):
            if task_id in task_dict:
                task_dict[task_id].execution_order = i
                
        # Also, update task status based on dependencies
        for task in tasks:
            if task.status == TaskStatus.COMPLETED:
                continue
                
            is_blocked = False
            task.blockers = []
            for dep in task.dependencies:
                if dep in task_dict and task_dict[dep].status != TaskStatus.COMPLETED:
                    is_blocked = True
                    task.blockers.append(dep)
            
            if is_blocked:
                task.status = TaskStatus.BLOCKED
            elif task.status == TaskStatus.BLOCKED:
                task.status = TaskStatus.READY
            elif task.status == TaskStatus.BACKLOG:
                task.status = TaskStatus.READY
                
        return sorted(tasks, key=lambda x: x.execution_order)
