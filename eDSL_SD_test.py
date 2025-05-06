import pytest
import math
from eDSL_SD import GraphBuilder, Interpreter, validate_input

# Simple Addition Test
def test_simple_addition():
    builder = GraphBuilder()
    builder.add_node("in").add_node("add", fn=lambda x: x + 1).add_edge("in", "add")
    nodes, edges = builder.build()
    interp = Interpreter(nodes, edges)
    trace = interp.run({"in": 10})
    assert trace[-1][2] == 11

# Parametric Tests for Binary Addition
@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3), (5, -5, 0), (0, 0, 0)
])
def test_binary_operation(a, b, expected):
    builder = GraphBuilder()
    builder.add_node("a").add_node("b").add_node("sum", fn=lambda x, y: x + y)
    builder.add_edge("a", "sum").add_edge("b", "sum")
    nodes, edges = builder.build()
    interp = Interpreter(nodes, edges)
    trace = interp.run({"a": a, "b": b})
    assert trace[-1][2] == expected

# Quadratic Equation Solving Test
def test_quadratic_solver():
    builder = GraphBuilder()
    builder.add_node("a").add_node("b").add_node("c")
    builder.add_node("b2", fn=lambda b: b * b).add_edge("b", "b2")
    builder.add_node("ac4", fn=lambda a, c: 4 * a * c).add_edge("a", "ac4").add_edge("c", "ac4")
    builder.add_node("delta", fn=lambda x, y: x - y).add_edge("b2", "delta").add_edge("ac4", "delta")
    builder.add_node("root", fn=lambda d: math.sqrt(d)).add_edge("delta", "root")
    nodes, edges = builder.build()
    interp = Interpreter(nodes, edges)
    trace = interp.run({"a": 1, "b": 0, "c": -1})
    assert any(step[0] == "root" and abs(step[2] - 2) < 1e-6 for step in trace)

# RS Trigger Test
def test_rs_flipflop():
    builder = GraphBuilder()
    builder.add_node("S").add_node("R")
    builder.add_node("Q", fn=lambda s, prev_q: s and not prev_q)
    builder.add_edge("S", "Q").add_edge("R", "Q")
    nodes, edges = builder.build()
    interp = Interpreter(nodes, edges)
    for val in [(True, False), (False, True)]:
        trace = interp.run({"S": val[0], "R": val[1]})
        assert isinstance(trace[-1][2], bool)

# Boundary test
# Empty graph execution should return empty trajectories
def test_empty_graph():
    builder = GraphBuilder()
    nodes, edges = builder.build()
    interp = Interpreter(nodes, edges)
    trace = interp.run({})
    assert trace == []

# Cyclic dependency graphs should not loop infinitely and return empty trajectories
def test_cycle_graph():
    builder = GraphBuilder()
    builder.add_node("A").add_node("B")
    builder.add_edge("A", "B").add_edge("B", "A")
    nodes, edges = builder.build()
    interp = Interpreter(nodes, edges)
    trace = interp.run({})
    assert trace == []

# Missing input nodes should throw a KeyError
def test_missing_input_node():
    builder = GraphBuilder()
    builder.add_node("X")
    nodes, edges = builder.build()
    interp = Interpreter(nodes, edges)
    with pytest.raises(KeyError):
        interp.run({"Y": 1})

# Input Validation Decorator Test
def test_validate_input_decorator():
    @validate_input({"x": int, "y": float})
    def func(**kwargs):
        return kwargs["x"] + kwargs["y"]
    assert func(x=1, y=2.5) == 3.5
    with pytest.raises(TypeError):
        func(x="a", y=2.5)
