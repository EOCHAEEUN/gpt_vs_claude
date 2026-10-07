import type { CodeResult } from '../types/comparison'

export function RuffIssues({ a, b }: { a: CodeResult; b: CodeResult }) {
  return <section className="result-section">
    <div className="section-heading"><div><span className="eyebrow">04 / STATIC CHECK</span><h2>Ruff 검사 결과</h2></div></div>
    <div className="issues-grid"><IssueList title="CODE A" result={a} /><IssueList title="CODE B" result={b} /></div>
  </section>
}

function IssueList({ title, result }: { title: string; result: CodeResult }) {
  return <div className="issue-panel"><h3>{title} <span>{result.ruff_issues.length}</span></h3>
    {result.ruff_error && <p className="error-text">{result.ruff_error}</p>}
    {!result.valid_python ? <p className="muted">문법 오류가 있어 Ruff 결과를 표시할 수 없습니다.</p>
      : !result.ruff_error && result.ruff_issues.length === 0 ? <p className="muted">Ruff 문제가 발견되지 않았습니다.</p>
      : <ul className="issues-list">{result.ruff_issues.map((issue, index) => <li key={`${issue.code}-${issue.line}-${index}`}><span className="issue-code">{issue.code}</span><span>{issue.message}<small>Line {issue.line}, Column {issue.column}</small></span></li>)}</ul>}
  </div>
}
