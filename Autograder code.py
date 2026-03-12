import unittest
import io
import sys
import importlib.util
from typing import Callable

# === Interactive Input Section ===
print("AI Code Autograder by Andrew Grappe")
print("Paste the EXACT prompt you gave to the AI below (multi-line OK).")
# Collect multi-line prompt
prompt_lines = []
while True:
    try:
        line = input()
        prompt_lines.append(line)
    except EOFError:
        break

user_prompt = "\n".join(prompt_lines).strip()

if not user_prompt:
    print("No prompt entered. Exiting.")
    sys.exit(1)

print("\nYou entered this prompt:")
print(user_prompt)
print("\nNow paste the AI-generated code below (the full function definition).")
print("Include ONLY the code; no explanations. End with Ctrl+D / Ctrl+Z + Enter.")
print("--------------------------------------------------")

# Collect multi-line code
code_lines = []
while True:
    try:
        line = input()
        code_lines.append(line)
    except EOFError:
        break

student_code = "\n".join(code_lines).strip()

if not student_code:
    print("No code entered. Exiting.")
    sys.exit(1)

# Optional: Problem name for logging
problem_name = input("\nEnter problem name/category (e.g., 'count_vowels - Strings'): ").strip() or "Unknown"

# === Dynamically load the student code ===
# Write to a temp file or use importlib to exec in memory
try:
    # Create a module from string
    spec = importlib.util.spec_from_loader("student_solution", loader=None)
    student_module = importlib.util.module_from_spec(spec)
    exec(student_code, student_module.__dict__)
except Exception as e:
    print(f"Error loading student code: {e}")
    print("Check for syntax errors in the AI output.")
    sys.exit(1)

# Assume the function name is consistent with your tests (e.g., 'count_vowels')
# For flexibility: You could parse the def line, but for now hardcode or ask
function_name = "count_vowels"  # Change per problem; or add input("Function name: ")
try:
    target_func: Callable = getattr(student_module, function_name)
except AttributeError:
    print(f"Function '{function_name}' not found in AI code.")
    sys.exit(1)

# === Your Test Class (adapted to use dynamic func) ===
class BaseCodeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.func = target_func
        cls.func_name = function_name

class TestCountVowels(BaseCodeTest):
    # Your existing tests, updated to use self.func
    def test_basic_lowercase(self):
        self.assertEqual(self.func("hello"), 2)

    def test_basic_uppercase(self):
        self.assertEqual(self.func("HELLO"), 2)

    def test_mixed_case(self):
        self.assertEqual(self.func("AeIoU"), 5)

    def test_empty_string(self):
        self.assertEqual(self.func(""), 0)

    def test_no_vowels(self):
        self.assertEqual(self.func("why"), 0)

    def test_only_vowels(self):
        self.assertEqual(self.func("audio"), 4)

    def test_return_type(self):
        result = self.func("test")
        self.assertIsInstance(result, int, "Return type must be int")

    def test_no_extra_output(self):
        captured = io.StringIO()
        sys.stdout = captured
        self.func("hello")
        sys.stdout = sys.__stdout__
        self.assertEqual(captured.getvalue().strip(), "", "No print statements allowed")

    def test_non_string_input(self):
        with self.assertRaises(TypeError):
            self.func(123)

    # Add more as needed...

# === Run Tests & Summary ===
if __name__ == '__main__':
    print(f"\nRunning autograder for: {problem_name}")
    print(f"Prompt used: {user_prompt[:100]}...")  # Truncated for display

    suite = unittest.TestLoader().loadTestsFromTestCase(TestCountVowels)
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    total = result.testsRun
    passed = total - len(result.failures) - len(result.errors)
    percent = (passed / total * 100) if total > 0 else 0

    print("\n" + "="*50)
    print(f"EXPERIMENT SUMMARY")
    print(f"Problem: {problem_name}")
    print(f"Model: [Enter manually: e.g., Grok trial 1/3]")
    print(f"Passed: {passed}/{total} ({percent:.1f}%)")
    print(f"Failures: {len(result.failures)} | Errors: {len(result.errors)}")
    print("="*50)

    # Optional: Save to log file for your data collection
    with open("autograder_log.txt", "a") as log:
        log.write(f"{problem_name} | Prompt snippet: {user_prompt[:50]}... | Passed: {percent:.1f}%\n")