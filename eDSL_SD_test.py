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
    
    # 输入节点 "in" 的 trace 条目是第一个，计算结果条目是第二个
    assert len(trace) == 2
    assert trace[0] == ("in", [], 10)   # 输入节点的输出记录
    assert trace[-1][2] == 11          # 计算结果


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
    
    # 输入节点 "a" 和 "b" 的 trace 条目在前，计算结果条目是第三个
    assert len(trace) == 3
    assert trace[0] == ("a", [], a)    # 输入节点 a 的输出
    assert trace[1] == ("b", [], b)    # 输入节点 b 的输出
    assert trace[-1][2] == expected    # 计算结果


# Quadratic Equation Solving Test
def test_quadratic_solver():
    builder = GraphBuilder()
    builder.add_node("a").add_node("b").add_node("c")
    builder.add_node("b2", fn=lambda b: b * b)
    builder.add_edge("b", "b2")
    builder.add_node("ac4", fn=lambda a, c: 4 * a * c)
    builder.add_edge("a", "ac4").add_edge("c", "ac4")
    builder.add_node("delta", fn=lambda x, y: x - y)
    builder.add_edge("b2", "delta").add_edge("ac4", "delta")
    builder.add_node("root", fn=lambda d: math.sqrt(d))
    builder.add_edge("delta", "root")
    nodes, edges = builder.build()
    interp = Interpreter(nodes, edges)
    trace = interp.run({"a": 1, "b": 0, "c": -1})
    
    # 确保 "root" 节点的计算结果存在（可能有多个中间节点记录）
    root_steps = [step for step in trace if step[0] == "root"]
    assert len(root_steps) == 1
    assert abs(root_steps[0][2] - 2) < 1e-6


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


# Visualizer Test（更新断言）
# 简单运算示例的DOT图生成测试
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

    # 验证节点标签
    assert 'label="input\\nresult: 3"' in dot_output
    assert 'label="add1\\nresult: 4"' in dot_output
    assert 'label="double\\nresult: 8"' in dot_output
    # 验证边标签
    assert 'input" -> "add1" [label="3"]' in dot_output
    assert 'add1" -> "double" [label="4"]' in dot_output


# 二次方程求解的DOT图生成测试
def test_quadratic_formula_visualizer():
    builder = GraphBuilder()
    builder.add_node("a").add_node("b").add_node("c")
    builder.add_node("b2", fn=lambda b: b * b)
    builder.add_edge("b", "b2")
    builder.add_node("ac4", fn=lambda a, c: 4 * a * c)
    builder.add_edge("a", "ac4").add_edge("c", "ac4")
    builder.add_node("delta", fn=lambda x, y: x - y)
    builder.add_edge("b2", "delta").add_edge("ac4", "delta")
    builder.add_node("root", fn=lambda d: math.sqrt(d))
    builder.add_edge("delta", "root")
    nodes, edges = builder.build()
    
    interp = Interpreter(nodes, edges)
    trace = interp.run({"a": 1, "b": 0, "c": -1})
    
    visualizer = Visualizer()
    dot_output = visualizer.to_dot(nodes, edges, trace)
    
    with open("quadratic_formula.dot", "w") as f:
        f.write(dot_output)
    
    # 验证关键节点和边
    assert 'label="a\\nresult: 1"' in dot_output
    assert 'label="b\\nresult: 0"' in dot_output
    assert 'label="c\\nresult: -1"' in dot_output
    assert 'label="delta\\nresult: 4"' in dot_output
    assert 'ac4" -> "delta" [label="-4"]' in dot_output
    assert 'delta" -> "root" [label="4"]' in dot_output


# RS触发器的DOT图生成测试
def test_rs_trigger_visualizer():
    builder = GraphBuilder()
    builder.add_node("S").add_node("R")
    builder.add_node("Q", fn=lambda s, r: s and not r)
    builder.add_edge("S", "Q").add_edge("R", "Q")
    nodes, edges = builder.build()
    
    interp = Interpreter(nodes, edges)
    trace = interp.run({"S": True, "R": False})
    
    visualizer = Visualizer()
    dot_output = visualizer.to_dot(nodes, edges, trace)
    
    with open("RS-trigger.dot", "w") as f:
        f.write(dot_output)
    
    # 验证布尔值结果
    assert 'label="S\\nresult: True"' in dot_output
    assert 'label="R\\nresult: False"' in dot_output
    assert 'label="Q\\nresult: True"' in dot_output
    assert 'S" -> "Q" [label="True"]' in dot_output
    assert 'R" -> "Q" [label="False"]' in dot_output
