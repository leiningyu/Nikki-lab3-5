# Nikki - lab 3 - variant 5

A series of functional requirements are realized and tested based on
`Synchronous Dataflow` method.

## Project structure

- `eDSL_SD.py` -- Implementation of Synchronous Dataflow
- `eDSL_SD_test.py` -- Tests for `eDSL_SD`.

## Features

- **Tests**:
   - `test_simple_addition`
   - `test_binary_operation`
   - `test_quadratic_solver`
   - `test_empty_graph`
   - `est_missing_input_node`
   - `test_validate_input_decorator`
   - `test_simple_example_visualizer`
   - `test_quadratic_formula_visualizer`

## Contribution

- **Lei Ningyu** (3232254146@qq.com) -- Implementation and testing.
- **Yi Min** (1757973489@qq.com) -- Implementation and testing.

## Changelog

- **03.05.2025 - v0**
   - Initial version.
- **06.05.2025 - v1**
   - Updated README, `eDSL_SD.py`, and `eDSL_SD_test.py`.
- **20.05.2025 - v2**
   - Updated `eDSL_SD.py`, and `eDSL_SD_test.py`.
- **21.05.2025 - v3**
   - Updated README, `quadratic_formula.dot` and `eDSL_SD_test.py`.

## Design Notes

- **Synchronous Dataflow**:
   - Each node represents an action and edge represents data transfers.
   - A node can be activated when all input edges received tokens.
   - After activation, node provide a single tag on each output.

- **GraphBuilder**:
   - Construct a directed graph consisting of a Node and an Edge.

- **validate_input**:
   - It is a higher-order decorator.
   - it verifies that the function input conforms to a predefined type.

- **Interpreter**:
   - Support manual input of values.
   - Manage the activation sequence of nodes.
   - Logging module make the interpreter work transparent.
