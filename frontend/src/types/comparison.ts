export interface CompareRequest {
  prompt: string
  code_a: string
  code_b: string
  label_a: string
  label_b: string
}

export interface CodeMetrics {
  total_lines: number
  code_lines: number
  blank_lines: number
  comment_lines: number
  functions: number
  async_functions: number
  classes: number
  imports: number
  import_modules: string[]
  decorators: number
  try_blocks: number
  except_handlers: number
  raise_count: number
  await_count: number
  parameter_type_hint_functions: number
  return_type_hint_functions: number
  function_type_hint_ratio: number
  return_type_hint_ratio: number
  module_docstring: boolean
  function_docstrings: number
  class_docstrings: number
  average_function_length: number
  max_function_length: number
  longest_function: string | null
  max_nesting_depth: number
  ruff_issue_count: number
}

export interface CodeResult {
  label: string
  valid_python: boolean
  syntax_error: { message: string; line: number | null; offset: number | null } | null
  metrics: CodeMetrics | null
  ruff_issues: { code: string; message: string; line: number; column: number }[]
  ruff_error: string | null
}

export interface Comparison {
  prompt: string
  code_a: CodeResult
  code_b: CodeResult
  differences: { metric: string; label: string; a: number; b: number; difference: number }[]
  import_comparison: { shared: string[]; only_a: string[]; only_b: string[] }
  summary: string[]
}
