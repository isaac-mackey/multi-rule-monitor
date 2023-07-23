# Rule Monitor

## Description

A Python implementation of algorithms for monitoring Datalog-like rules as constraints on event logs

## Dependencies

The following dependencies are required to run this project:

- [z3-solver](https://pypi.org/project/z3-solver/): A Python package for working with the Z3 theorem prover. It provides a high-level API to construct formulas and check satisfiability.

```shell
pip install z3-solver
```

- [pandas](https://pypi.org/project/pandas/): A data manipulation and analysis library for Python. It provides neat data structures for organizing experimental results.

```shell
pip install pandas
```

## Usage

```shell
python3 start.py log_file rule_file
```

For example:

```shell
python3 start.py example_logs/small-log-975-events.txt rules/small-rule-1.txt
```

See rules folder for examples of rule syntax.

See logs folder for examples of log format.

## Contact

email: imackey1415@gmail.com