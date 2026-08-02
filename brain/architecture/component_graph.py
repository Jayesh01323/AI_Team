from collections import defaultdict

from .models import Component, Dependency


class ComponentGraph:
    def __init__(self):
        self.adj: dict[str, list[str]] = defaultdict(list)
        self.nodes: dict[str, Component] = {}

    def add_component(self, comp: Component):
        self.nodes[comp.id] = comp
        if comp.id not in self.adj:
            self.adj[comp.id] = []

    def add_dependency(self, dep: Dependency):
        if dep.source_id in self.nodes and dep.target_id in self.nodes:
            self.adj[dep.source_id].append(dep.target_id)
        else:
            raise ValueError(f"Unknown components in dependency: {dep.source_id} -> {dep.target_id}")

    def build_from_architecture(self, components: list[Component], dependencies: list[Dependency]):
        for comp in components:
            self.add_component(comp)
        for dep in dependencies:
            self.add_dependency(dep)

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

        # Sort for stable traversal
        for node in sorted(self.nodes.keys()):
            if node not in visited:
                if dfs(node):
                    return True
        return False

    def get_dependencies(self, comp_id: str) -> list[str]:
        return self.adj.get(comp_id, [])

    def get_dependents(self, comp_id: str) -> list[str]:
        dependents = []
        for src, targets in self.adj.items():
            if comp_id in targets:
                dependents.append(src)
        return dependents
