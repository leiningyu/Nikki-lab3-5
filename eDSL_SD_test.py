import pytest
import math
from eDSL_SD import GraphBuilder, Interpreter, validate_input, Visualizer


# Simple Addition Test
def test_simple_addition():
    builder = GraphBuilder()
    builder.add_node("in").add_node("add", fn=lambda x: x + 1)
    builder.add_edge("in", "add")
    nodes, edges = builder.build()
    interp = Interpreter(nodes, edges)
    trace = interp.run({"in": 10})

    assert len(trace) == 2
    assert trace[0] == ("in", [], 10)
    # The calculation result of the last node
    assert trace[-1][2] == 11


# Parametric Tests for Binary Addition
@pytest.mark.parametrize(
    "a,b,expected",
    [(1, 2, 3), (5, -5, 0), (0, 0, 0)]
)
def test_binary_operation(a, b, expected):
    builder = GraphBuilder()
    builder.add_node("a").add_node("b")
    builder.add_node("sum", fn=lambda x, y: x + y)
    builder.add_edge("a", "sum").add_edge("b", "sum")
    nodes, edges = builder.build()
    interp = Interpreter(nodes, edges)
    trace = interp.run({"a": a, "b": b})

    assert len(trace) == 3
    assert trace[0] == ("a", [], a)    # input a
    assert trace[1] == ("b", [], b)    # input b
    assert trace[-1][2] == expected    # result


# Quadratic Equation Solving Test
def test_quadratic_solver():
    builder = GraphBuilder()
    builder.add_node("a").add_node("b").add_node("c")
    builder.add_node("b^2", fn=lambda b: b * b)
    builder.add_edge("b", "b^2")
    builder.add_node("4ac", fn=lambda a, c: 4 * a * c)
    builder.add_edge("a", "4ac").add_edge("c", "4ac")
    builder.add_node("delta", fn=lambda x, y: x - y)
    builder.add_edge("b^2", "delta").add_edge("4ac", "delta")
    builder.add_node("-b", fn=lambda b: -b)
    builder.add_node("sqrt_delta", fn=lambda d: math.sqrt(d))
    builder.add_node("2a", fn=lambda a: 2 * a)
    builder.add_node("root_plus", fn=lambda n, s, d: (n + s) / d)
    builder.add_node("root_minus", fn=lambda n, s, d: (n - s) / d)
    builder.add_edge("b", "-b")
    builder.add_edge("delta", "sqrt_delta")
    builder.add_edge("a", "2a")
    builder.add_edge("-b", "root_plus")
    builder.add_edge("sqrt_delta", "root_plus")
    builder.add_edge("2a", "root_plus")
    builder.add_edge("-b", "root_minus")
    builder.add_edge("sqrt_delta", "root_minus")
    builder.add_edge("2a", "root_minus")

    nodes, edges = builder.build()
    interp = Interpreter(nodes, edges)
    trace = interp.run({"a": 1, "b": 0, "c": -1})

    results = {name: res for name, _, res in trace}
    assert results["delta"] == 4
    assert results["sqrt_delta"] == 2
    assert results["-b"] == 0
    assert results["2a"] == 2
    assert results["root_plus"] == 1    # (0+2)/2=1
    assert results["root_minus"] == -1  # (0-2)/2=-1


# Boundary test
def test_empty_graph():
    builder = GraphBuilder()
    nodes, edges = builder.build()
    interp = Interpreter(nodes, edges)
    trace = interp.run({})
    assert trace == []


# Cyclic dependency test
def test_cycle_graph():
    builder = GraphBuilder()
    builder.add_node("A").add_node("B")
    builder.add_edge("A", "B").add_edge("B", "A")
    nodes, edges = builder.build()
    interp = Interpreter(nodes, edges)
    trace = interp.run({})
    assert trace == []


# Missing input nodes test
def test_missing_input_node():
    builder = GraphBuilder()
    builder.add_node("X")
    nodes, edges = builder.build()
    interp = Interpreter(nodes, edges)
    with pytest.raises(KeyError):
        interp.run({"Y": 1})


# Input Validation Decorator Test
def test_validate_input_decorator():
    @validate_input({
        "x": (int, lambda x: x > 0),
        "y": float
    })
    def add_positive_and_float(**kwargs):
        return kwargs["x"] + kwargs["y"]

    assert add_positive_and_float(x=5, y=2.0) == 7.0

    with pytest.raises(TypeError):
        add_positive_and_float(x="5", y=2.0)

    with pytest.raises(ValueError):
        add_positive_and_float(x=0, y=2.0)

    with pytest.raises(TypeError):
        add_positive_and_float(y=2.0)


# Visualizer Test
# Simple example
def test_simple_example_visualizer():
    builder = GraphBuilder()
    builder.add_node("input").add_node("add1", fn=lambda x: x + 1)
    builder.add_node("double", fn=lambda x: x * 2)
    builder.add_edge("input", "add1").add_edge("add1", "double")
    nodes, edges = builder.build()

    interp = Interpreter(nodes, edges)
    trace = interp.run({"input": 3})

    visualizer = Visualizer()
    dot_output = visualizer.to_dot(nodes, edges, trace)

    with open("simple_example.dot", "w") as f:
        f.write(dot_output)

    # Verify the node label
    assert 'label="input\\nresult: 3"' in dot_output
    assert 'label="add1\\nresult: 4"' in dot_output
    assert 'label="double\\nresult: 8"' in dot_output
    # Verify the edge label
    assert 'input" -> "add1" [label="3"]' in dot_output
    assert 'add1" -> "double" [label="4"]' in dot_output


def test_quadratic_formula_visualizer():
    builder = GraphBuilder()
    builder.add_node("a").add_node("b").add_node("c")
    builder.add_node("b^2", fn=lambda b: b * b)
    builder.add_edge("b", "b^2")
    builder.add_node("4ac", fn=lambda a, c: 4 * a * c)
    builder.add_edge("a", "4ac").add_edge("c", "4ac")
    builder.add_node("delta", fn=lambda x, y: x - y)
    builder.add_edge("b^2", "delta").add_edge("4ac", "delta")
    builder.add_node("-b", fn=lambda b: -b)
    builder.add_node("sqrt_delta", fn=lambda d: math.sqrt(d))
    builder.add_node("2a", fn=lambda a: 2 * a)
    builder.add_node("root_plus", fn=lambda n, s, d: (n + s) / d)
    builder.add_node("root_minus", fn=lambda n, s, d: (n - s) / d)
    builder.add_edge("b", "-b")
    builder.add_edge("delta", "sqrt_delta")
    builder.add_edge("a", "2a")
    builder.add_edge("-b", "root_plus")
    builder.add_edge("sqrt_delta", "root_plus")
    builder.add_edge("2a", "root_plus")
    builder.add_edge("-b", "root_minus")
    builder.add_edge("sqrt_delta", "root_minus")
    builder.add_edge("2a", "root_minus")
    nodes, edges = builder.build()

    interp = Interpreter(nodes, edges)
    trace = interp.run({"a": 1, "b": 0, "c": -1})

    visualizer = Visualizer()
    dot_output = visualizer.to_dot(nodes, edges, trace)

    with open("quadratic_formula.dot", "w") as f:
        f.write(dot_output)

    assert 'label="-b\\nresult: 0"' in dot_output
    assert 'label="2a\\nresult: 2"' in dot_output
    assert 'label="root_plus\\nresult: 1.0"' in dot_output
    assert 'label="root_minus\\nresult: -1.0"' in dot_output
    assert '2a" -> "root_plus" [label="2"]' in dot_output
    assert 'sqrt_delta" -> "root_plus" [label="2.0"]' in dot_output
    assert '-b" -> "root_plus" [label="0"]' in dot_output
    assert '-b" -> "root_minus" [label="0"]' in dot_output
