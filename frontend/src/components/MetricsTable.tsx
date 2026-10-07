import type { Comparison } from '../types/comparison'

const groups = [
  { title: '기본 지표', keys: ['total_lines', 'code_lines', 'blank_lines', 'comment_lines'] },
  { title: '구조', keys: ['functions', 'async_functions', 'classes', 'imports', 'decorators'] },
  { title: '예외 및 비동기', keys: ['try_blocks', 'except_handlers', 'raise_count', 'await_count'] },
  { title: '타입 및 문서화', keys: ['parameter_type_hint_functions', 'return_type_hint_functions', 'function_type_hint_ratio', 'return_type_hint_ratio', 'function_docstrings', 'class_docstrings'] },
  { title: '함수와 중첩', keys: ['average_function_length', 'max_function_length', 'max_nesting_depth', 'ruff_issue_count'] },
]

export function MetricsTable({ comparison }: { comparison: Comparison }) {
  const lookup = new Map(comparison.differences.map((item) => [item.metric, item]))
  return <section className="result-section">
    <div className="section-heading"><div><span className="eyebrow">01 / OVERVIEW</span><h2>핵심 비교 지표</h2></div><p>수치 차이가 있는 행을 강조했습니다.</p></div>
    <div className="table-scroll"><table className="metrics-table"><thead><tr><th>지표</th><th>CODE A</th><th>CODE B</th></tr></thead><tbody>
      {groups.map((group) => <FragmentRows key={group.title} title={group.title} keys={group.keys} lookup={lookup} />)}
    </tbody></table></div>
  </section>
}

function FragmentRows({ title, keys, lookup }: { title: string; keys: string[]; lookup: Map<string, Comparison['differences'][number]> }) {
  return <><tr className="group-row"><th colSpan={3}>{title}</th></tr>{keys.map((key) => {
    const item = lookup.get(key)
    if (!item) return null
    const ratio = key.endsWith('_ratio')
    const format = (value: number) => ratio ? `${Math.round(value * 100)}%` : value.toLocaleString('ko-KR')
    return <tr key={key} className={item.difference ? 'changed-row' : ''}><th>{item.label}</th><td>{format(item.a)}</td><td>{format(item.b)}</td></tr>
  })}</>
}
