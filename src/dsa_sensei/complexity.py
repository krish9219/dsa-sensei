"""AST heuristics for time and space complexity.

The checker does not execute code and it does not prove a bound. It looks at
loop nesting, recursion shape, sorting, and a handful of common container
operations, then reports the pattern it recognized.
"""

from __future__ import annotations

import ast
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

from dsa_sensei.errors import CodeRejected

MAX_CODE_CHARS = 100_000
DISCLAIMER = (
    "These are AST heuristics, not a proof. They look at loop nesting, recursion "
    "shape, sorting, and common container operations. They miss data-dependent "
    "control flow and do not inline functions they cannot see."
)

_CHILD_ATTRS = frozenset({"left", "right", "next", "prev", "parent"})
_LOG_NAMES = frozenset({"lo", "hi", "low", "high", "left", "right", "start", "end"})
_MEMO_DECORATORS = frozenset({"lru_cache", "cache"})
_LINEAR_AGGREGATES = frozenset({"sum", "any", "all"})
_CONTAINER_CTORS = frozenset({"list", "tuple", "set", "dict"})
_BISECT = frozenset({"bisect", "bisect_left", "bisect_right"})
_HEAP_LOG = frozenset({"heappush", "heappop"})

_RANK_SPECIAL = {
    "O(1)": (0, 0, 0),
    "O(log n)": (0, 0, 1),
    "O(n)": (0, 1, 0),
    "O(n + e)": (0, 1, 0),
    "O(n log n)": (0, 1, 1),
}


@dataclass(frozen=True, slots=True)
class Cost:
    poly: int = 0
    log: int = 0
    exp: int = 0

    def key(self) -> tuple[int, int, int]:
        return (self.exp, self.poly, self.log)

    def max(self, other: Cost) -> Cost:
        return self if self.key() >= other.key() else other

    def loop_linear(self) -> Cost:
        if self.exp:
            return self
        return Cost(self.poly + 1, self.log, 0)

    def loop_log(self) -> Cost:
        if self.exp:
            return self
        return Cost(self.poly, self.log + 1, 0)


ZERO = Cost()


@dataclass
class Findings:
    owned: set[str] = field(default_factory=set)
    string_names: set[str] = field(default_factory=set)
    subscript_loads: set[str] = field(default_factory=set)
    subscript_stores: set[str] = field(default_factory=set)
    membership_checks: set[str] = field(default_factory=set)
    alloc: bool = False
    slice_copies: int = 0
    used_sort: bool = False
    assumed_linear_while: bool = False
    string_concat_in_loop: bool = False
    pop_front_in_loop: bool = False
    insert_in_loop: bool = False
    mutates_input: bool = False
    marks_visited: bool = False
    calls_local: bool = False
    small_iters: set[str] = field(default_factory=set)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class FunctionComplexity:
    name: str
    time: str
    space: str
    warnings: tuple[str, ...]
    notes: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "time": self.time,
            "space": self.space,
            "warnings": list(self.warnings),
            "notes": list(self.notes),
        }


@dataclass(frozen=True, slots=True)
class ComplexityReport:
    time: str
    space: str
    confidence: str
    disclaimer: str
    warnings: tuple[str, ...]
    notes: tuple[str, ...]
    functions: tuple[FunctionComplexity, ...]
    primary_function: str

    def to_dict(self) -> dict[str, object]:
        return {
            "time": self.time,
            "space": self.space,
            "confidence": self.confidence,
            "disclaimer": self.disclaimer,
            "warnings": list(self.warnings),
            "notes": list(self.notes),
            "functions": [item.to_dict() for item in self.functions],
            "primary_function": self.primary_function,
        }


def analyze_python(code: str) -> ComplexityReport:
    if not isinstance(code, str):
        raise CodeRejected("Code must be a string of Python source.")
    source = code.lstrip("\ufeff")
    if len(source) > MAX_CODE_CHARS:
        raise CodeRejected(f"Code is limited to {MAX_CODE_CHARS} characters.")
    if not source.strip():
        raise CodeRejected("Submit some Python code to analyze.")
    try:
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            line = exc.lineno or 1
            raise CodeRejected(f"Could not parse this as Python (line {line}): {exc.msg}") from exc
        functions = _collect_functions(tree)
        reports: list[tuple[FunctionComplexity, Cost, Cost, str]] = []
        defined = {node.name for _, node in functions}
        module_stmts = _module_statements(tree)
        if module_stmts:
            report, time, space, confidence = _analyze_block("<module>", module_stmts, defined, memo=False)
            reports.append((report, time, space, confidence))
        for name, node in functions:
            memo = _memo_decorator(node)
            report, time, space, confidence = _analyze_block(
                name, list(node.body), defined, memo=memo, fname=node.name
            )
            reports.append((report, time, space, confidence))
        if not reports:
            raise CodeRejected("No executable code found. Submit a function or a snippet.")

        primary = max(reports, key=lambda item: (item[1].key(), item[2].key()))
        warnings = _unique(warning for report, _, _, _ in reports for warning in report.warnings)
        notes = _unique(note for report, _, _, _ in reports for note in report.notes)
        if len(reports) > 1:
            notes.append(
                "Calls between functions in this snippet are not inlined. "
                f"The headline is the most expensive one ({primary[0].name})."
            )
        confidences = [item[3] for item in reports]
        confidence = "low" if "low" in confidences else "medium" if "medium" in confidences else "high"
        if len(reports) > 1 and confidence == "high":
            confidence = "medium"
        return ComplexityReport(
            time=format_cost(primary[1]),
            space=format_cost(primary[2]),
            confidence=confidence,
            disclaimer=DISCLAIMER,
            warnings=tuple(warnings),
            notes=tuple(notes),
            functions=tuple(item[0] for item in reports),
            primary_function=primary[0].name,
        )
    except CodeRejected:
        raise
    except RecursionError as exc:
        raise CodeRejected("This code is nested too deeply to analyze.") from exc
    except MemoryError as exc:
        raise CodeRejected("This code is too large to analyze.") from exc
    except ValueError as exc:
        raise CodeRejected(f"Could not analyze this code: {exc}") from exc


def format_cost(cost: Cost) -> str:
    if cost.exp:
        return f"O({cost.exp}^n)"
    if cost.poly <= 0 and cost.log <= 0:
        return "O(1)"
    if cost.poly <= 0 and cost.log == 1:
        return "O(log n)"
    if cost.poly <= 0:
        return f"O(log^{cost.log} n)"
    if cost.poly == 1 and cost.log == 0:
        return "O(n)"
    if cost.poly == 1 and cost.log == 1:
        return "O(n log n)"
    if cost.log == 0:
        return f"O(n^{cost.poly})"
    if cost.log == 1:
        return f"O(n^{cost.poly} log n)"
    return f"O(n^{cost.poly} log^{cost.log} n)"


def complexity_key(label: str) -> tuple[int, int, int] | None:
    """Sort key for a big-O label. ``None`` means the label is unrecognized."""
    if label in _RANK_SPECIAL:
        return _RANK_SPECIAL[label]
    match = re.fullmatch(r"O\(n\^(\d+)\)$", label)
    if match:
        return (0, int(match.group(1)), 0)
    match = re.fullmatch(r"O\(n\^(\d+) log n\)$", label)
    if match:
        return (0, int(match.group(1)), 1)
    match = re.fullmatch(r"O\((\d+)\^n\)$", label)
    if match:
        return (int(match.group(1)), 0, 0)
    return None


def describe_comparison(
    estimate_time: str,
    target_time: str,
    acceptable: tuple[str, ...],
    *,
    estimate_space: str,
    target_space: str,
    note: str,
) -> str:
    estimate_key = complexity_key(estimate_time)
    allowed = [complexity_key(item) for item in acceptable]
    if estimate_key is None or any(item is None for item in allowed):
        return (
            f"Catalog target is {target_time} time and {target_space} extra space. "
            "This estimate could not be compared automatically."
        )
    best = min(key for key in allowed if key is not None)
    if estimate_key in allowed or estimate_key == best:
        relation = f"matches a bound the catalog accepts ({', '.join(acceptable)})"
    elif estimate_key < best:
        relation = (
            f"looks better than the catalog target of {target_time}. "
            "Heuristics under-count sometimes, so check the code before trusting it"
        )
    else:
        relation = (
            f"looks slower than the catalog target of {target_time} "
            f"(accepted bounds: {', '.join(acceptable)})"
        )
    space_bit = f" Estimated extra space is {estimate_space}; the catalog lists {target_space}."
    suffix = f" {note}" if note else ""
    return f"Time estimate {relation}.{space_bit}{suffix}"


def _analyze_block(
    name: str,
    body: list[ast.stmt],
    defined: set[str],
    *,
    memo: bool,
    fname: str = "",
) -> tuple[FunctionComplexity, Cost, Cost, str]:
    findings = Findings()
    findings.calls_local = False
    body_cost = _block_cost(body, LoopContext(), findings, defined)
    calls, kinds, in_loop = _recursion_shape(body, fname) if fname else (0, set(), False)
    halving = _halves(body)
    manual_memo = bool(
        (findings.subscript_loads & findings.subscript_stores)
        or (findings.membership_checks & findings.subscript_stores)
    )
    memoized = memo or (manual_memo and calls > 0)
    time, stack, confidence = _combine(
        body_cost,
        calls=calls,
        kinds=kinds,
        in_loop=in_loop,
        halving=halving,
        memoized=memoized,
        mutates=findings.mutates_input or findings.marks_visited,
    )
    if findings.string_concat_in_loop or findings.pop_front_in_loop or findings.insert_in_loop:
        time = time.max(Cost(2, 0, 0))
        confidence = "medium"
    if findings.string_concat_in_loop:
        findings.warnings.append("Building a string with += inside a loop is often quadratic.")
    if findings.pop_front_in_loop:
        findings.warnings.append("list.pop(0) shifts every later item and is linear per call.")
    if findings.insert_in_loop:
        findings.warnings.append("Inserting into a list inside a loop can make the pass quadratic.")
    if findings.assumed_linear_while:
        findings.notes.append(
            "A while loop was counted as linear. It may be logarithmic if the "
            "stopping condition shrinks the input in a way this checker missed."
        )
        confidence = "medium"
    if findings.used_sort:
        findings.notes.append("A sort was treated as O(n log n) in the size of its collection.")
    if findings.slice_copies:
        findings.notes.append("Slicing was counted as a linear copy.")
    if calls >= 2 and time.exp:
        findings.warnings.append(
            "Branching recursion without memoization or a visited set looks exponential."
        )
    space = ZERO
    if findings.alloc or findings.slice_copies:
        space = Cost(1, 0, 0)
    if stack == "linear":
        space = space.max(Cost(1, 0, 0))
    elif stack == "log":
        space = space.max(Cost(0, 1, 0))
    if time.exp and confidence == "high":
        confidence = "medium"
    report = FunctionComplexity(
        name=name,
        time=format_cost(time),
        space=format_cost(space),
        warnings=tuple(_unique(findings.warnings)),
        notes=tuple(_unique(findings.notes)),
    )
    return report, time, space, confidence


def _combine(
    body: Cost,
    *,
    calls: int,
    kinds: set[str],
    in_loop: bool,
    halving: bool,
    memoized: bool,
    mutates: bool,
) -> tuple[Cost, str, str]:
    if calls == 0:
        return body, "none", "high"
    if memoized:
        time = Cost(1, 0, 0) if body.key() == ZERO.key() else body.loop_linear()
        return time, "linear", "medium"
    if "child" in kinds:
        time = body if body.poly >= 1 else Cost(1, 0, 0)
        return time, "linear", "medium"
    if calls >= 2 and ("slice" in kinds or halving) and "sub" not in kinds:
        base = body if body.poly >= 1 else Cost(1, 0, 0)
        return base.loop_log(), "log", "medium"
    if calls >= 2 and (mutates or "index" in kinds):
        time = body if body.poly >= 1 else Cost(1, 0, 0)
        return time, "linear", "medium"
    if calls >= 2:
        return Cost(exp=2), "linear", "medium"
    if halving:
        time = body.loop_log() if body.poly or body.log else Cost(0, 1, 0)
        return time, "log", "medium"
    if in_loop:
        time = body if body.poly >= 1 else Cost(1, 0, 0)
        return time, "linear", "medium"
    return body.loop_linear(), "linear", "medium"


@dataclass(frozen=True, slots=True)
class LoopContext:
    """Where a statement sits relative to the loops that enclose it."""

    depth: int = 0
    targets: tuple[str, ...] = ()
    reset_names: frozenset[str] = frozenset()
    inside_pop_while: bool = False
    inside_while: bool = False


def _block_cost(stmts: list[ast.stmt], ctx: LoopContext, findings: Findings, defined: set[str]) -> Cost:
    cost = ZERO
    for stmt in stmts:
        cost = cost.max(_stmt_cost(stmt, ctx, findings, defined))
    return cost


def _stmt_cost(stmt: ast.stmt, ctx: LoopContext, findings: Findings, defined: set[str]) -> Cost:
    depth = ctx.depth
    if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return ZERO
    if isinstance(stmt, (ast.For, ast.AsyncFor)):
        iter_cost = _expr_cost(stmt.iter, depth, findings, defined)
        child = LoopContext(
            depth=depth + 1,
            targets=ctx.targets + _target_names(stmt.target),
            reset_names=frozenset(_assigned_outside_whiles(list(stmt.body))),
            inside_pop_while=ctx.inside_pop_while,
            inside_while=ctx.inside_while,
        )
        inner = _block_cost(list(stmt.body), child, findings, defined)
        other = _block_cost(list(stmt.orelse), ctx, findings, defined)
        if _for_adds_factor(stmt, ctx, findings):
            return iter_cost.max(inner.loop_linear()).max(other)
        return iter_cost.max(inner).max(other)
    if isinstance(stmt, ast.While):
        test_cost = _expr_cost(stmt.test, depth, findings, defined)
        child = LoopContext(
            depth=depth + 1,
            targets=ctx.targets,
            reset_names=ctx.reset_names,
            inside_pop_while=ctx.inside_pop_while or _contains_pop(stmt),
            inside_while=True,
        )
        inner = _block_cost(list(stmt.body), child, findings, defined)
        other = _block_cost(list(stmt.orelse), ctx, findings, defined)
        if _while_is_log(stmt):
            return test_cost.max(inner.loop_log()).max(other)
        if ctx.depth > 0 and _while_is_amortized(stmt, ctx):
            return test_cost.max(inner).max(other)
        findings.assumed_linear_while = True
        return test_cost.max(inner.loop_linear()).max(other)
    if isinstance(stmt, ast.If):
        _note_membership(stmt.test, findings)
        cost = _expr_cost(stmt.test, depth, findings, defined)
        cost = cost.max(_block_cost(list(stmt.body), ctx, findings, defined))
        return cost.max(_block_cost(list(stmt.orelse), ctx, findings, defined))
    try_parts = _try_parts(stmt)
    if try_parts is not None:
        body, handlers, orelse, finalbody = try_parts
        cost = _block_cost(list(body), ctx, findings, defined)
        for handler in handlers:
            cost = cost.max(_block_cost(list(handler.body), ctx, findings, defined))
        cost = cost.max(_block_cost(list(orelse), ctx, findings, defined))
        return cost.max(_block_cost(list(finalbody), ctx, findings, defined))
    if isinstance(stmt, (ast.With, ast.AsyncWith)):
        return _block_cost(list(stmt.body), ctx, findings, defined)
    if isinstance(stmt, ast.Match):
        cost = ZERO
        for case in stmt.cases:
            cost = cost.max(_block_cost(list(case.body), ctx, findings, defined))
        return cost
    if isinstance(stmt, ast.Assign):
        return _assign_cost(stmt, depth, findings, defined)
    if isinstance(stmt, ast.AnnAssign):
        value_cost = _expr_cost(stmt.value, depth, findings, defined)
        if stmt.value is not None:
            _track_target(stmt.target, stmt.value, findings)
        return value_cost
    if isinstance(stmt, ast.AugAssign) and isinstance(stmt.target, ast.Name):
        if isinstance(stmt.op, ast.Add) and stmt.target.id in findings.string_names and depth > 0:
            findings.string_concat_in_loop = True
        return _expr_cost(stmt.value, depth, findings, defined)
    if isinstance(stmt, ast.Return):
        return _expr_cost(stmt.value, depth, findings, defined)
    if isinstance(stmt, ast.Expr):
        return _expr_cost(stmt.value, depth, findings, defined)
    if isinstance(stmt, ast.Delete):
        return ZERO
    return ZERO


def _target_names(target: ast.expr) -> tuple[str, ...]:
    if isinstance(target, ast.Name):
        return (target.id,)
    if isinstance(target, (ast.Tuple, ast.List)):
        names: list[str] = []
        for elt in target.elts:
            names.extend(_target_names(elt))
        return tuple(names)
    return ()


def _direct_assign_names(stmt: ast.stmt) -> set[str]:
    if isinstance(stmt, ast.Assign):
        names: set[str] = set()
        for target in stmt.targets:
            names.update(_target_names(target))
        return names
    if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
        return {stmt.target.id}
    if isinstance(stmt, ast.AugAssign) and isinstance(stmt.target, ast.Name):
        return {stmt.target.id}
    return set()


def _assigned_skip_while(stmt: ast.stmt) -> set[str]:
    if isinstance(stmt, (ast.While, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return set()
    found = _direct_assign_names(stmt)
    for child in ast.iter_child_nodes(stmt):
        if isinstance(child, ast.stmt):
            found |= _assigned_skip_while(child)
    return found


def _assigned_outside_whiles(stmts: list[ast.stmt]) -> set[str]:
    found: set[str] = set()
    for stmt in stmts:
        found |= _assigned_skip_while(stmt)
    return found


def _is_constant_iter(node: ast.expr) -> bool:
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)) and len(node.elts) <= 12:
        return True
    if isinstance(node, ast.Call) and _call_name(node.func) == "range":
        values: list[int] = []
        for arg in node.args[:2]:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, int):
                values.append(arg.value)
        if len(node.args) == 1 and len(values) == 1:
            return abs(values[0]) <= 16
        if len(node.args) >= 2 and len(values) == 2:
            return abs(values[1] - values[0]) <= 16
    return False


def _is_child_or_flatten(node: ast.expr, ctx: LoopContext) -> bool:
    """True when this loop walks the current row, a neighbor list, or a fixed tuple."""
    if isinstance(node, ast.Name) and node.id in ctx.targets:
        return True
    if ctx.depth > 0 and isinstance(node, (ast.Subscript, ast.Attribute)):
        return True
    if isinstance(node, ast.Call) and _call_name(node.func) == "range" and node.args:
        arg = node.args[0]
        if isinstance(arg, ast.Name) and arg.id in ctx.targets:
            return True
        if isinstance(arg, ast.Call) and _call_name(arg.func) == "len" and arg.args:
            subject = arg.args[0]
            if isinstance(subject, ast.Name) and subject.id in ctx.targets:
                return True
            if isinstance(subject, ast.Subscript) and ctx.depth > 0:
                return True
    return False


def _for_adds_factor(stmt: ast.For | ast.AsyncFor, ctx: LoopContext, findings: Findings) -> bool:
    if _is_constant_iter(stmt.iter):
        return False
    if isinstance(stmt.iter, ast.Name) and stmt.iter.id in findings.small_iters:
        return False
    if ctx.depth > 0 and _is_child_or_flatten(stmt.iter, ctx):
        return False
    scanning_a_layer = (
        ctx.inside_pop_while and isinstance(stmt.iter, ast.Call) and _call_name(stmt.iter.func) == "range"
    )
    return not scanning_a_layer


def _contains_pop(node: ast.AST) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Call) and _call_name(child.func) in {"pop", "popleft"}:
            return True
    return False


def _contains_full_scan(node: ast.AST) -> bool:
    for child in ast.walk(node):
        if isinstance(child, (ast.For, ast.AsyncFor)) and not _is_constant_iter(child.iter):
            if isinstance(child.iter, (ast.Subscript, ast.Attribute)):
                continue
            if isinstance(child.iter, ast.Call) and _call_name(child.iter.func) == "range":
                continue
            return True
    return False


def _advanced_names(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.AugAssign) and isinstance(child.target, ast.Name):
            if isinstance(child.op, (ast.Add, ast.Sub)):
                names.add(child.target.id)
        elif isinstance(child, ast.Assign) and len(child.targets) == 1:
            target = child.targets[0]
            if (
                isinstance(target, ast.Name)
                and isinstance(child.value, ast.BinOp)
                and isinstance(child.value.left, ast.Name)
                and child.value.left.id == target.id
                and isinstance(child.value.op, (ast.Add, ast.Sub))
            ):
                names.add(target.id)
    return names


def _names_used_as_subscript(node: ast.AST, names: set[str]) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Subscript) and isinstance(child.slice, ast.Name) and child.slice.id in names:
            return True
    return False


def _has_membership_test(node: ast.AST) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Compare) and any(isinstance(op, (ast.In, ast.NotIn)) for op in child.ops):
            return True
    return False


def _while_is_amortized(stmt: ast.While, ctx: LoopContext) -> bool:
    """An inner while that only drains a stack or walks a pointer forward once."""
    if _contains_full_scan(stmt):
        return False
    if ctx.inside_while:
        return True
    advanced = _advanced_names(stmt)
    pops = _contains_pop(stmt)
    reset = advanced & set(ctx.reset_names)
    indexed = reset if _names_used_as_subscript(stmt, reset) else set()
    if indexed:
        return False
    if pops or (advanced - reset):
        return True
    return bool(reset and _has_membership_test(stmt))


def _try_parts(
    stmt: ast.stmt,
) -> tuple[list[ast.stmt], list[ast.ExceptHandler], list[ast.stmt], list[ast.stmt]] | None:
    if isinstance(stmt, ast.Try):
        return list(stmt.body), list(stmt.handlers), list(stmt.orelse), list(stmt.finalbody)
    try_star = getattr(ast, "TryStar", None)
    if try_star is not None and isinstance(stmt, try_star):
        body = list(getattr(stmt, "body", []))
        handlers = list(getattr(stmt, "handlers", []))
        orelse = list(getattr(stmt, "orelse", []))
        finalbody = list(getattr(stmt, "finalbody", []))
        return body, handlers, orelse, finalbody
    return None


def _assign_cost(stmt: ast.Assign, depth: int, findings: Findings, defined: set[str]) -> Cost:
    cost = _expr_cost(stmt.value, depth, findings, defined)
    for target in stmt.targets:
        if isinstance(target, ast.Subscript):
            root = _root_name(target)
            if root is not None:
                findings.subscript_stores.add(root)
                if root in findings.owned and depth > 0:
                    findings.alloc = True
                elif root not in findings.owned:
                    findings.mutates_input = True
        else:
            _track_target(target, stmt.value, findings)
    return cost


def _expr_cost(expr: ast.expr | None, depth: int, findings: Findings, defined: set[str]) -> Cost:
    if expr is None:
        return ZERO
    if isinstance(expr, ast.Call):
        return _call_cost(expr, depth, findings, defined)
    if isinstance(expr, ast.IfExp):
        return (
            _expr_cost(expr.test, depth, findings, defined)
            .max(_expr_cost(expr.body, depth, findings, defined))
            .max(_expr_cost(expr.orelse, depth, findings, defined))
        )
    if isinstance(expr, ast.BoolOp):
        cost = ZERO
        for value in expr.values:
            cost = cost.max(_expr_cost(value, depth, findings, defined))
        return cost
    if isinstance(expr, ast.Compare):
        _note_membership(expr, findings)
        cost = _expr_cost(expr.left, depth, findings, defined)
        for comparator in expr.comparators:
            cost = cost.max(_expr_cost(comparator, depth, findings, defined))
        return cost
    if isinstance(expr, (ast.ListComp, ast.SetComp)):
        findings.alloc = True
        return _comp_cost(list(expr.generators), expr.elt, depth, findings, defined)
    if isinstance(expr, ast.GeneratorExp):
        return _comp_cost(list(expr.generators), expr.elt, depth, findings, defined)
    if isinstance(expr, ast.DictComp):
        findings.alloc = True
        return _comp_cost(list(expr.generators), expr.key, depth, findings, defined).max(
            _comp_cost(list(expr.generators), expr.value, depth, findings, defined)
        )
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Mult) and _is_sequence(expr.left, expr.right):
        if not _is_small_repeat(expr):
            findings.alloc = True
            return (
                Cost(1, 0, 0)
                .max(_expr_cost(expr.left, depth, findings, defined))
                .max(_expr_cost(expr.right, depth, findings, defined))
            )
        return _expr_cost(expr.left, depth, findings, defined).max(
            _expr_cost(expr.right, depth, findings, defined)
        )
    if isinstance(expr, ast.Subscript) and isinstance(expr.slice, ast.Slice):
        findings.slice_copies += 1
        return Cost(1, 0, 0).max(_expr_cost(expr.value, depth, findings, defined))
    if isinstance(expr, ast.Subscript):
        root = _root_name(expr)
        if root is not None:
            findings.subscript_loads.add(root)
        return _expr_cost(expr.value, depth, findings, defined).max(
            _expr_cost(expr.slice, depth, findings, defined) if isinstance(expr.slice, ast.expr) else ZERO
        )
    if isinstance(expr, ast.Attribute):
        return _expr_cost(expr.value, depth, findings, defined)
    if isinstance(expr, (ast.List, ast.Tuple, ast.Set)):
        return _max_exprs(list(expr.elts), depth, findings, defined)
    if isinstance(expr, ast.Dict):
        cost = _max_exprs(list(expr.keys), depth, findings, defined)
        return cost.max(_max_exprs(list(expr.values), depth, findings, defined))
    if isinstance(expr, ast.BinOp):
        return _expr_cost(expr.left, depth, findings, defined).max(
            _expr_cost(expr.right, depth, findings, defined)
        )
    if isinstance(expr, ast.UnaryOp):
        return _expr_cost(expr.operand, depth, findings, defined)
    if isinstance(expr, ast.NamedExpr):
        _track_target(expr.target, expr.value, findings)
        return _expr_cost(expr.value, depth, findings, defined)
    return ZERO


def _call_cost(call: ast.Call, depth: int, findings: Findings, defined: set[str]) -> Cost:
    name = _call_name(call.func)
    args = list(call.args)
    cost = _max_exprs(args, depth, findings, defined)
    for keyword in call.keywords:
        cost = cost.max(_expr_cost(keyword.value, depth, findings, defined))
    if isinstance(call.func, ast.Name) and call.func.id in defined and call.func.id != name:
        findings.calls_local = True
    if isinstance(call.func, ast.Name) and call.func.id in defined:
        findings.calls_local = True
    if name == "sorted":
        findings.alloc = True
        findings.used_sort = True
        cost = cost.max(Cost(1, 1, 0))
    elif name == "sort":
        findings.used_sort = True
        cost = cost.max(Cost(1, 1, 0))
    elif name in _BISECT or name in _HEAP_LOG:
        cost = cost.max(Cost(0, 1, 0))
    elif name == "heapify":
        findings.used_sort = True
        cost = cost.max(Cost(1, 1, 0))
    elif name in _LINEAR_AGGREGATES or (name in {"min", "max"} and len(args) <= 1):
        cost = cost.max(Cost(1, 0, 0))
    elif (name in _CONTAINER_CTORS and args) or name == "join":
        if not _args_are_small(call, findings):
            findings.alloc = True
            cost = cost.max(Cost(1, 0, 0))
    elif name == "insert" and depth > 0:
        findings.insert_in_loop = True
    elif name == "pop" and depth > 0 and args and _is_zero(args[0]):
        findings.pop_front_in_loop = True
    elif name in {"append", "extend"} and depth > 0 and _receiver_owned(call.func, findings):
        findings.alloc = True
    elif name == "add":
        findings.marks_visited = True
        if depth > 0 and _receiver_owned(call.func, findings):
            findings.alloc = True
    return cost


def _comp_cost(
    generators: list[ast.comprehension],
    inner: ast.expr,
    depth: int,
    findings: Findings,
    defined: set[str],
) -> Cost:
    if not generators:
        return _expr_cost(inner, depth, findings, defined)
    head, *rest = generators
    inner_cost = _comp_cost(rest, inner, depth + 1, findings, defined)
    iter_cost = _expr_cost(head.iter, depth, findings, defined)
    for test in head.ifs:
        iter_cost = iter_cost.max(_expr_cost(test, depth, findings, defined))
    return iter_cost.max(inner_cost.loop_linear())


def _max_exprs(
    exprs: Sequence[ast.expr | None],
    depth: int,
    findings: Findings,
    defined: set[str],
) -> Cost:
    cost = ZERO
    for expr in exprs:
        if expr is not None:
            cost = cost.max(_expr_cost(expr, depth, findings, defined))
    return cost


def _recursion_shape(body: list[ast.stmt], fname: str) -> tuple[int, set[str], bool]:
    counter = _PathCounter(fname)
    calls = counter.suite(body)
    return calls, counter.kinds, counter.in_loop


class _PathCounter:
    """Self-calls along one execution path, plus how the arguments look.

    Statements that all run are added. An ``if`` that returns takes the maximum
    of that branch and the statements after it, so ``if cond: return f()``
    followed by ``return f()`` stays a single recursive call.
    """

    def __init__(self, fname: str) -> None:
        self.fname = fname
        self.kinds: set[str] = set()
        self.in_loop = False
        self._loop_depth = 0

    def suite(self, stmts: list[ast.stmt]) -> int:
        total = 0
        for index, stmt in enumerate(stmts):
            head = self.count(stmt)
            if isinstance(stmt, ast.If) and not stmt.orelse and _suite_returns(list(stmt.body)):
                return total + max(head, self.suite(stmts[index + 1 :]))
            total += head
            if _returns(stmt):
                break
        return total

    def count(self, node: ast.AST) -> int:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            return 0
        if isinstance(node, ast.If):
            return self.count(node.test) + max(self.suite(list(node.body)), self.suite(list(node.orelse)))
        if isinstance(node, ast.IfExp):
            return self.count(node.test) + max(self.count(node.body), self.count(node.orelse))
        if isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
            self._loop_depth += 1
            body = self.suite(list(node.body))
            self._loop_depth -= 1
            test = node.iter if isinstance(node, (ast.For, ast.AsyncFor)) else node.test
            return self.count(test) + body
        if isinstance(node, ast.BoolOp):
            return max((self.count(value) for value in node.values), default=0)
        if isinstance(node, ast.Try):
            branches = [
                self.suite(list(node.body)),
                self.suite(list(node.orelse)),
                self.suite(list(node.finalbody)),
            ]
            branches.extend(self.suite(list(handler.body)) for handler in node.handlers)
            return max(branches, default=0)
        if isinstance(node, ast.Match):
            return max((self.suite(list(case.body)) for case in node.cases), default=0)
        if isinstance(node, ast.Call) and _is_self_call(node, self.fname):
            if self._loop_depth > 0:
                self.in_loop = True
            self.kinds |= _arg_kinds(node)
            return 1 + sum(self.count(arg) for arg in node.args)
        total = 0
        for child in ast.iter_child_nodes(node):
            total += self.count(child)
        return total


def _returns(stmt: ast.stmt) -> bool:
    if isinstance(stmt, (ast.Return, ast.Raise)):
        return True
    if isinstance(stmt, ast.If) and stmt.orelse:
        return _suite_returns(list(stmt.body)) and _suite_returns(list(stmt.orelse))
    return False


def _suite_returns(stmts: list[ast.stmt]) -> bool:
    return any(_returns(stmt) for stmt in stmts)


def _is_self_call(call: ast.Call, fname: str) -> bool:
    func = call.func
    if isinstance(func, ast.Name):
        return func.id == fname
    if isinstance(func, ast.Attribute) and func.attr == fname and isinstance(func.value, ast.Name):
        return func.value.id in {"self", "cls"}
    return False


def _arg_kinds(call: ast.Call) -> set[str]:
    kinds: set[str] = set()
    for arg in call.args:
        if isinstance(arg, ast.Attribute) and arg.attr in _CHILD_ATTRS:
            kinds.add("child")
        elif isinstance(arg, ast.Subscript) and isinstance(arg.slice, ast.Slice):
            kinds.add("slice")
        elif isinstance(arg, ast.Subscript):
            kinds.add("index")
        elif isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Sub):
            kinds.add("sub")
        elif isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add):
            kinds.add("add")
    return kinds


def _halves(body: list[ast.stmt]) -> bool:
    for node in ast.walk(ast.Module(body=body, type_ignores=[])):
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.FloorDiv, ast.RShift)):
            return True
        if isinstance(node, ast.AugAssign) and isinstance(node.op, (ast.FloorDiv, ast.RShift)):
            return True
    return False


def _while_is_log(stmt: ast.While) -> bool:
    if not _halves([stmt]):
        return False
    names = {node.id for node in ast.walk(stmt) if isinstance(node, ast.Name)}
    if names & _LOG_NAMES:
        return True
    for node in ast.walk(stmt):
        if isinstance(node, ast.AugAssign) and isinstance(node.op, (ast.FloorDiv, ast.RShift)):
            return True
    return False


def _memo_decorator(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for decorator in fn.decorator_list:
        target: ast.expr = decorator.func if isinstance(decorator, ast.Call) else decorator
        if isinstance(target, ast.Name) and target.id in _MEMO_DECORATORS:
            return True
        if isinstance(target, ast.Attribute) and target.attr in _MEMO_DECORATORS:
            return True
    return False


def _collect_functions(tree: ast.Module) -> list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]]:
    found: list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]] = []

    def walk(nodes: list[ast.stmt], prefix: str) -> None:
        for node in nodes:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qual = f"{prefix}.{node.name}" if prefix else node.name
                found.append((qual, node))
                walk(list(node.body), qual)
            elif isinstance(node, ast.ClassDef):
                qual = f"{prefix}.{node.name}" if prefix else node.name
                walk(list(node.body), qual)

    walk(list(tree.body), "")
    return found


def _module_statements(tree: ast.Module) -> list[ast.stmt]:
    statements: list[ast.stmt] = []
    for index, stmt in enumerate(tree.body):
        if isinstance(
            stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom)
        ):
            continue
        if (
            index == 0
            and isinstance(stmt, ast.Expr)
            and isinstance(stmt.value, ast.Constant)
            and isinstance(stmt.value.value, str)
        ):
            continue
        statements.append(stmt)
    return statements


def _track_target(target: ast.expr, value: ast.expr, findings: Findings) -> None:
    if isinstance(target, ast.Name):
        if _is_fresh_container(value):
            findings.owned.add(target.id)
            if isinstance(value, ast.BinOp) and not _is_small_repeat(value):
                findings.alloc = True
        if _is_small_container(value):
            findings.small_iters.add(target.id)
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            findings.string_names.add(target.id)
        return
    if isinstance(target, (ast.Tuple, ast.List)) and isinstance(value, (ast.Tuple, ast.List)):
        if len(target.elts) != len(value.elts):
            return
        for inner_target, inner_value in zip(target.elts, value.elts, strict=True):
            _track_target(inner_target, inner_value, findings)


def _is_fresh_container(expr: ast.expr) -> bool:
    if isinstance(expr, (ast.List, ast.Dict, ast.Set)):
        return True
    if isinstance(expr, ast.Call) and _call_name(expr.func) in {"list", "dict", "set"}:
        return True
    return (
        isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Mult) and _is_sequence(expr.left, expr.right)
    )


def _is_small_container(expr: ast.expr) -> bool:
    if isinstance(expr, (ast.List, ast.Tuple, ast.Set)) and len(expr.elts) <= 12:
        return True
    return isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Mult) and _is_small_repeat(expr)


def _args_are_small(call: ast.Call, findings: Findings) -> bool:
    if len(call.args) != 1:
        return False
    arg = call.args[0]
    if isinstance(arg, ast.Name) and arg.id in findings.small_iters:
        return True
    return _is_small_container(arg)


def _is_small_repeat(expr: ast.BinOp) -> bool:
    constant = expr.right if isinstance(expr.right, ast.Constant) else expr.left
    if not isinstance(constant, ast.Constant) or not isinstance(constant.value, int):
        return False
    return abs(constant.value) <= 64


def _is_sequence(left: ast.expr, right: ast.expr) -> bool:
    sequences = (ast.List, ast.Tuple, ast.Set)
    return isinstance(left, sequences) or isinstance(right, sequences)


def _note_membership(expr: ast.expr, findings: Findings) -> None:
    for node in ast.walk(expr):
        if isinstance(node, ast.Compare):
            for op, comparator in zip(node.ops, node.comparators, strict=True):
                if isinstance(op, (ast.In, ast.NotIn)) and isinstance(comparator, ast.Name):
                    findings.membership_checks.add(comparator.id)


def _call_name(func: ast.expr) -> str | None:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _root_name(expr: ast.expr) -> str | None:
    current: ast.expr = expr
    while isinstance(current, (ast.Subscript, ast.Attribute)):
        current = current.value
    if isinstance(current, ast.Name):
        return current.id
    return None


def _receiver_owned(func: ast.expr, findings: Findings) -> bool:
    if isinstance(func, ast.Attribute):
        root = _root_name(func.value)
        return root in findings.owned if root is not None else False
    return False


def _is_zero(expr: ast.expr) -> bool:
    return isinstance(expr, ast.Constant) and expr.value == 0


def _unique(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered
