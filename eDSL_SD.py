import logging
from typing import Callable, Any, Dict, List, Deque, Tuple, Optional
from collections import deque


# ------- Model and Builder -------
class Edge:
    def __init__(self, src: 'Node', dst: 'Node'):
        self.src = src
        self.dst = dst
        self.tokens: Deque[Any] = deque()

    def send(self, value: Any):
        self.tokens.append(value)
        logging.debug(
            f"Edge {self.src.name}->{self.dst.name} received token: {value}"
        )

    def consume(self) -> Any:
        return self.tokens.popleft()

    def has_token(self) -> bool:
        return bool(self.tokens)


class Node:
    def __init__(self, name: str, fn: Optional[Callable[..., Any]] = None):
        self.name = name
        self.fn: Callable[..., Any] = fn if fn is not None else (lambda *args: None)
        self.in_edges: List[Edge] = []
        self.out_edges: List[Edge] = []

    def add_in(self, edge: Edge):
        self.in_edges.append(edge)

    def add_out(self, edge: Edge):
        self.out_edges.append(edge)

    def ready(self) -> bool:
        return all(edge.has_token() for edge in self.in_edges)

    def activate(self) -> Any:
        inputs = [edge.consume() for edge in self.in_edges]
        logging.debug(f"Activating node {self.name} with inputs {inputs}")
        result = self.fn(*inputs)
        for edge in self.out_edges:
            edge.send(result)
        return result


class GraphBuilder:
    def __init__(self):
        self._nodes: Dict[str, Node] = {}
        self._edges: List[Edge] = []

    def add_node(
        self, name: str, fn: Optional[Callable[..., Any]] = None
    ) -> 'GraphBuilder':
        if name in self._nodes:
            raise ValueError(f"Node '{name}' already exists")
        self._nodes[name] = Node(name, fn)
        return self

    def add_edge(self, src_name: str, dst_name: str) -> 'GraphBuilder':
        if src_name not in self._nodes or dst_name not in self._nodes:
            raise KeyError("Source or destination node not found")
        src = self._nodes[src_name]
        dst = self._nodes[dst_name]
        edge = Edge(src, dst)
        src.add_out(edge)
        dst.add_in(edge)
        self._edges.append(edge)
        return self

    def set_node_fn(self, name: str, fn: Callable[..., Any]) -> 'GraphBuilder':
        if name not in self._nodes:
            raise KeyError(f"Node '{name}' not found")
        self._nodes[name].fn = fn
        return self

    def build(self) -> Tuple[Dict[str, Node], List[Edge]]:
        return self._nodes, self._edges


# ------- Input validation decorator -------
def validate_input(schema: Dict[str, type]):
    def decorator(fn: Callable[..., Any]):
        def wrapper(**kwargs):
            for k, t in schema.items():
                if k not in kwargs or not isinstance(kwargs[k], t):
                    raise TypeError(f"Input '{k}' must be {t}")
            return fn(**kwargs)
        return wrapper
    return decorator


# ------- Interpreter -------
class Interpreter:
    def __init__(self, nodes: Dict[str, Node], edges: List[Edge]):
        self.nodes = nodes
        self.edges = edges
        self.trace: List[Tuple[str, List[Any], Any]] = []
        logging.basicConfig(level=logging.DEBUG)

    def run(self, inputs: Dict[str, Any]) -> List[Tuple[str, List[Any], Any]]:
        for name, value in inputs.items():
            node = self.nodes.get(name)
            if node is None:
                raise KeyError(f"Input node '{name}' not found")
            for edge in node.out_edges:
                edge.send(value)

        queue = deque(
            node for node in self.nodes.values()
            if node.ready() and node.in_edges
        )
        while queue:
            node = queue.popleft()
            try:
                result = node.activate()
                self.trace.append((node.name, [], result))
            except Exception as e:
                logging.error(f"Error in node '{node.name}': {e}")
            for edge in node.out_edges:
                downstream = edge.dst
                if downstream.ready():
                    queue.append(downstream)

        return self.trace


# ------- Visualizer -------
class Visualizer:
    def to_dot(
        self,
        nodes: Dict[str, Node],
        edges: List[Edge],
        trace: List[Tuple[str, List[Any], Any]]
    ) -> str:
        lines = ["digraph G {"]
        for node in nodes.values():
            lines.append(f'  "{node.name}";')
        for edge in edges:
            lines.append(f'  "{edge.src.name}" -> "{edge.dst.name}";')
        lines.append("}")
        return "\n".join(lines)
