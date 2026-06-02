"""
IS 303 Autograder - A05: Modeling the World (OOP)

This autograder checks student Python files against a rubric JSON file.
Students can run this locally before submitting to verify their work meets
the basic requirements.

Usage:
    python a05_autograder.py

    By default, the autograder looks for .py files in the current directory
    and uses a05_rubric.json for grading instructions. You can also pass
    a folder path as an argument to grade a specific folder.

    python a05_autograder.py /path/to/student/folder

Checks performed:
    1. File identification: matches file names to known problem contexts
    2. Content checks: verifies the I/P/O comment block exists
    3. Structural warnings: checks for class definitions, __init__, __str__,
       composition (list + append), and return inside __str__
    4. Output tests: runs the program with sample inputs and checks
       that output includes expected patterns
"""

import json
import os
import re
import subprocess
import sys


def load_rubric(rubric_path):
    """Load and return the rubric from a JSON file."""
    with open(rubric_path, "r", encoding="utf-8") as f:
        return json.load(f)


def identify_problem(file_name, rubric):
    """
    Match a file name to a problem context using the rubric's naming dictionary.
    Returns the problem name if matched, or None if no match is found.
    """
    file_lower = file_name.lower()
    for problem_name, possible_names in rubric["problem_naming"].items():
        for name in possible_names:
            if name.lower() == file_lower:
                return problem_name
    return None


def check_file_contents(file_path, problem_rubric):
    """
    Check the file contents against the rubric's content checks.
    Returns a tuple of (points_earned, list_of_notes).

    Content checks can be point-bearing (like I/P/O block) or warn-only
    (like checking for class definitions, which earns no points but warns
    if missing or insufficient).

    Supports min_count: if a check has min_count > 1, the autograder
    counts how many matches exist and warns if fewer than required.
    """
    points = 0
    notes = []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    for check in problem_rubric["content_checks"]:
        field = check["field"]
        regexes = check["regexes"]
        check_points = check.get("points", 0)
        warn_only = check.get("warn_only", False)
        warn_message = check.get("warn_message", "")
        min_count = check.get("min_count", 1)
        found = False

        if min_count > 1:
            # Count total matches across all regex patterns
            total_matches = 0
            for regex in regexes:
                matches = re.findall(regex, content, re.IGNORECASE | re.DOTALL)
                total_matches += len(matches)

            if total_matches >= min_count:
                found = True
                points += check_points
            else:
                if warn_only:
                    notes.append(f"  WARNING: {warn_message}")
                    if total_matches > 0:
                        notes.append(
                            f"    Found {total_matches}, need at least "
                            f"{min_count}."
                        )
                else:
                    notes.append(f"  MISSING: {field}")
        else:
            for regex in regexes:
                if re.search(regex, content, re.IGNORECASE | re.DOTALL):
                    found = True
                    break

            if found:
                points += check_points
            else:
                if warn_only:
                    notes.append(f"  WARNING: {warn_message}")
                else:
                    notes.append(f"  MISSING: {field}")

    return points, notes


def run_single_test(file_path, sim_input, timeout=15):
    """
    Run a student file with the given simulated input.
    Returns (exit_code, stdout, stderr) or raises on timeout.
    """
    result = subprocess.run(
        [sys.executable, os.path.abspath(file_path)],
        input=sim_input,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.returncode, result.stdout, result.stderr


def run_test_cases(file_path, problem_rubric, timeout=15):
    """
    Run all test cases for a problem.
    Returns (points_earned, list_of_notes).

    A05 test cases are "output_check" type: they send sample inputs
    and check that the output contains expected patterns (like class
    names, domain keywords, or computed values).
    """
    points = 0
    notes = []
    test_cases = problem_rubric["test_cases"]

    for tc in test_cases:
        label = tc["label"]
        sim_input = tc["inputs"]
        expected = tc["expected_output"]
        tc_points = tc["points"]

        try:
            exit_code, stdout, stderr = run_single_test(
                file_path, sim_input, timeout
            )

            # Handle program crashes
            if exit_code != 0:
                notes.append(f"  ERROR [{label}]: Program crashed")
                if stderr:
                    error_lines = stderr.strip().split("\n")
                    last_line = error_lines[-1]
                    if "EOFError" in last_line:
                        notes.append(
                            f"    Program asked for more input than expected."
                        )
                        notes.append(
                            f"    Your input() calls may not match the "
                            f"expected pattern."
                        )
                        notes.append(
                            f"    The autograder sends: item data "
                            f"(name, details, etc.) then 'done' to stop."
                        )
                    else:
                        notes.append(f"    {last_line}")
                continue

            output = stdout

            # Check output against expected pattern
            if re.search(expected, output, re.DOTALL | re.IGNORECASE):
                points += tc_points
            else:
                notes.append(f"  OUTPUT CHECK [{label}]:")
                notes.append(f"    Expected to find pattern: {expected}")
                if output.strip():
                    # Show last 300 chars of output (the summary part)
                    summary = output.strip()[-300:]
                    notes.append(f"    Output (last 300 chars): {summary}")
                else:
                    notes.append(f"    Got: (no output)")
                notes.append(
                    f"    Note: The autograder looks for domain keywords "
                    f"in your output."
                )
                notes.append(
                    f"    If your wording is different, this may be a "
                    f"false negative. Your instructor will check manually."
                )

        except subprocess.TimeoutExpired:
            notes.append(
                f"  TIMEOUT [{label}]: Program took more than {timeout} "
                f"seconds. Check for infinite loops."
            )
        except Exception as e:
            notes.append(f"  ERROR [{label}]: {str(e)}")

    return points, notes


def grade_file(file_path, problem_name, problem_rubric):
    """
    Grade a single file. Returns (points_earned, list_of_notes).
    """
    total_points = 0
    all_notes = []

    # Check file contents (I/P/O block + structural warnings)
    pts, notes = check_file_contents(file_path, problem_rubric)
    total_points += pts
    all_notes.extend(notes)

    # Run test cases (output checks)
    pts, notes = run_test_cases(file_path, problem_rubric)
    total_points += pts
    all_notes.extend(notes)

    return total_points, all_notes


def find_student_files(folder_path, rubric):
    """
    Scan a folder for .py files that match known problem contexts.
    Returns a list of (file_path, problem_name) tuples.
    Ignores the autograder file itself.
    """
    matches = []
    autograder_name = os.path.basename(__file__).lower()

    for file_name in sorted(os.listdir(folder_path)):
        if not file_name.endswith(".py"):
            continue
        if file_name.lower() == autograder_name:
            continue

        problem_name = identify_problem(file_name, rubric)
        if problem_name:
            matches.append((os.path.join(folder_path, file_name), problem_name))
        else:
            print(f"  [?] {file_name}: not recognized as a known context (skipped)")

    return matches


def print_separator():
    """Print a visual separator line."""
    print("-" * 60)


def main():
    # Determine folder and rubric paths
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
    else:
        folder_path = os.path.dirname(os.path.abspath(__file__))

    rubric_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "a05_rubric.json"
    )

    if not os.path.exists(rubric_path):
        print(f"Error: Cannot find a05_rubric.json at {rubric_path}")
        print("Make sure the rubric file is in the same folder as this autograder.")
        sys.exit(1)

    rubric = load_rubric(rubric_path)

    print()
    print("=" * 60)
    print("  IS 303 Autograder: A05 - Modeling the World (OOP)")
    print("=" * 60)
    print(f"  Scanning: {folder_path}")
    print()

    # Find matching files
    matches = find_student_files(folder_path, rubric)

    if not matches:
        print("  No recognized Python files found.")
        print()
        print("  Make sure your file names match one of these patterns:")
        for problem, names in rubric["problem_naming"].items():
            print(f"    {problem}: {', '.join(names[:3])}")
        print()
        sys.exit(1)

    # Grade each file
    total_score = 0
    problems_found = []

    for file_path, problem_name in matches:
        file_name = os.path.basename(file_path)
        problem_rubric = rubric["problem_rubrics"][problem_name]

        print_separator()
        print(f"  File: {file_name}")
        print(f"  Context: {problem_name}")
        print()

        pts, notes = grade_file(file_path, problem_name, problem_rubric)
        total_score += pts
        problems_found.append(problem_name)

        # Calculate max possible for this problem
        max_content = sum(
            c["points"] for c in problem_rubric["content_checks"]
            if not c.get("warn_only", False)
        )
        max_tests = sum(tc["points"] for tc in problem_rubric["test_cases"])
        max_possible = max_content + max_tests

        print(f"  Score: {pts}/{max_possible}")

        if notes:
            print()
            print("  Issues found:")
            for note in notes:
                print(f"    {note}")
        else:
            print("  All checks passed!")

        print()

    # Summary
    print_separator()
    print()
    print("  SUMMARY")
    print()
    print(f"  Program found: {len(matches)}")
    for pname in problems_found:
        print(f"    - {pname}")
    print()

    if len(matches) > 1:
        print("  NOTE: A05 requires ONE program with two classes.")
        print("  Multiple files were found. Only one will be graded.")
        print()

    print(f"  Autograder score: {total_score} (content + output checks only)")
    print()
    print("  Note: This score does NOT include points for:")
    print("    - Class design quality (attributes, methods, composition)")
    print("    - CRC cards (15 points, graded by instructor)")
    print("    - Code organization and __str__ formatting")
    print("    - Commit messages or GitHub submission (15 points)")
    print()
    print("  The autograder checks structure (classes, __init__, __str__,")
    print("  composition) as warnings. If you see warnings above, fix them")
    print("  before submitting. Your instructor grades these for full points.")
    print()
    print("  Because A05 programs have varied input structures, some output")
    print("  tests may produce false negatives. If your program runs correctly")
    print("  but the autograder does not find the expected keywords, your")
    print("  instructor will test your program manually.")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
