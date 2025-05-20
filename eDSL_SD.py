import logging
from typing import Callable, Any, Dict, List, Deque, Tuple, Optional, Union
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
        self.fn = fn if fn is not None else (lambda *args: None)
        self.in_edges: List[Edge] = []
        self.out_edges: List[Edge] = []

    def add_in(self, edge: Edge):
        self.in_edges.append(edge)

    def add_out(self, edge: Edge):
        self.out_edges.append(edge)

    def ready(self) -> bool:
        return all(edge.has_token() for edge in self.in_edges)

    def activate(self) -> Tuple[List[Any], Any]:
        inputs = [edge.consume() for edge in self.in_edges]
        logging.debug(f"Activating node {self.name} with inputs {inputs}")
        result = self.fn(*inputs)
        for edge in self.out_edges:
            edge.send(result)
        return inputs, result


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
def validate_input(
        schema: Dict[str, Union[type, Tuple[type, Callable[[Any], bool]]]]):
    def decorator(fn: Callable[..., Any]):
        def wrapper(**kwargs):
            for k, rule in schema.items():
                if k not in kwargs:
                    raise TypeError(f"Missing input '{k}'")
                val = kwargs[k]
                if isinstance(rule, tuple):
                    typ, cond = rule
                    if not isinstance(val, typ):
                        raise TypeError(f"Input '{k}' must be of type {typ}")
                    if not cond(val):
                        raise ValueError(f"Input '{k}' wrong value range")
                else:
                    if not isinstance(val, rule):
                        raise TypeError(f"Input '{k}' must be of type {rule}")
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
        # 注入输入数据并记录输入节点的输出
        for name, value in inputs.items():
            node = self.nodes.get(name)
            if node is None:
                raise KeyError(f"Input node '{name}' not found")
            for edge in node.out_edges:
                edge.send(value)
            self.trace.append((node.name, [], value))  # 输入节点输出记录

        # 处理就绪节点
        queue = deque(
            node for node in self.nodes.values()
            if node.ready() and node.in_edges
        )
        while queue:
            node = queue.popleft()
            try:
                inputs_consumed, result = node.activate()
                self.trace.append((node.name, inputs_consumed, result))
            except Exception as e:
                logging.error(f"Error in node '{node.name}': {e}")
            # 触发下游节点
            for edge in node.out_edges:
                downstream = edge.dst
                if downstream.ready() and downstream not in queue:
                    queue.append(downstream)
        return self.trace


# ------- Visualizer -------
class Visualizer:
    def to_dot(
        self,
        nodes: Dict[str, Node],
        edges: List[Edge],
        trace: List[Tuple[str, List[Any], Any]] = []
    ) -> str:
        result_map = {name: result for name, _, result in trace}
        lines = ["digraph G {"]
        # 生成节点标签（名称 + 结果）
        for node in nodes.values():
            label = [node.name]
            if node.name in result_map:
                label.append(f"result: {result_map[node.name]}")
            lines.append(f'  "{node.name}" [label="{"\\n".join(label)}"];')
        # 生成边标签（显示源节点的输出值）
        for edge in edges:
            src_name = edge.src.name
            edge_label = result_map.get(src_name, "")
            lines.append(f'  "{src_name}" -> "{edge.dst.name}" [label="{edge_label}"];')
        lines.append("}")
        return "\n".join(lines)
