from collections import defaultdict, deque

from .models import Task


class DependencyGraph:
    def __init__(self):
        self.adj: dict[str, list[str]] = defaultdict(list)
        self.in_degree: dict[str, int] = defaultdict(int)
        self.nodes: set[str] = set()

    def add_node(self, node: str):
        self.nodes.add(node)
        if node not in self.adj:
            self.adj[node] = []
        if node not in self.in_degree:
            self.in_degree[node] = 0

    def add_edge(self, u: str, v: str):
        """Adds a directed edge from u to v (u must complete before v)"""
        self.add_node(u)
        self.add_node(v)
        self.adj[u].append(v)
        self.in_degree[v] += 1

    def has_cycle(self) -> bool:
        visited = set()
        rec_stack = set()

        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            for neighbor in self.adj[node]:
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for node in self.nodes:
            if node not in visited:
                if dfs(node):
                    return True
        return False

    def topological_sort(self) -> list[str]:
        if self.has_cycle():
            raise ValueError("Dependency cycle detected")
            
        queue = deque([node for node in self.nodes if self.in_degree[node] == 0])
        
        # Sort initial queue to make output deterministic
        queue = deque(sorted(queue))
        
        ordered = []
        
        # Create a copy of in_degree
        in_deg = dict(self.in_degree)
        
        while queue:
            # We want to pick the node deterministically. 
            # In a standard queue it's order of entry, but multiple might have in-degree 0 at same time.
            # To be strictly deterministic, let's just pick the smallest string.
            # But sorting the queue at each step is better:
            queue_list = sorted(list(queue))
            u = queue_list[0]
            queue.remove(u)
            
            ordered.append(u)
            for neighbor in sorted(self.adj[u]):
                in_deg[neighbor] -= 1
                if in_deg[neighbor] == 0:
                    queue.append(neighbor)
                    
        if len(ordered) != len(self.nodes):
            raise ValueError("Topological sort failed (missing nodes, likely cycle not caught)")
            
        return ordered

    def get_missing_dependencies(self, declared_dependencies: dict[str, list[str]]) -> list[str]:
        """Detects if a declared dependency is not a known node."""
        missing = []
        for task, deps in declared_dependencies.items():
            for dep in deps:
                if dep not in self.nodes:
                    missing.append(dep)
        return missing

    def build_from_tasks(self, tasks: list[Task]):
        for task in tasks:
            self.add_node(task.id)
            for dep in task.dependencies:
                self.add_edge(dep, task.id)
