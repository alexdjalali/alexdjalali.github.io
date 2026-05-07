"""A simple calculator module — deliberately flawed for demo purposes."""

import json
import os
from typing import Any

# ISSUE: ruff format — inconsistent spacing, long lines, bad string quotes
def   add(a:int,b:int) ->int:
    return a+b

def subtract( a:int , b:int )->int:
    return a -b

def multiply(a:int,b:int)->int:
    result=a*b
    return result

def divide(a: int, b: int) -> float:
    # ISSUE: basedpyright — no check for division by zero, return type mismatch
    return a / b

def calculate(operation:str, a:int, b:int) -> Any:
    # ISSUE: ruff — using Any without narrowing, no type union
    if operation == "add":
        return add(a, b)
    elif operation == "subtract":
        return subtract(a, b)
    elif operation == "multiply":
        return multiply(a, b)
    elif operation == "divide":
        return divide(a, b)
    else:
        return None

# ISSUE: ruff lint — unused import (json, os), unused variable
unused_constant = "this is never used"

def format_result(value: int | float) -> str:
    # ISSUE: basedpyright — value could be None from calculate()
    if isinstance(value, float) and value == int(value):
        return str(int(value))
    return str(value)

class CalculatorHistory:
    # ISSUE: ruff — missing __init__ type annotations
    def __init__(self):
        self.history = []

    def add_entry(self, operation, a, b, result):
        self.history.append({"op": operation, "a": a, "b": b, "result": result})

    def get_last(self):
        if len(self.history) == 0:
            return None
        return self.history[-1]

    # ISSUE: ruff SIM — could use simpler expression
    def has_entries(self) -> bool:
        if len(self.history) > 0:
            return True
        else:
            return False
