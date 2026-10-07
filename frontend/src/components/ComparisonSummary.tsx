import type { Comparison } from '../types/comparison'

export function ComparisonSummary({ comparison }: { comparison: Comparison }) {
  const imports = comparison.import_comparison
  return <>
    <section className="result-section">
      <div className="section-heading"><div><span className="eyebrow">02 / STRUCTURE</span><h2>구조 차이 요약</h2></div></div>
      <ul className="summary-list">{comparison.summary.map((line, index) => <li key={index}>{line}</li>)}</ul>
    </section>
    <section className="result-section">
      <div className="section-heading"><div><span className="eyebrow">03 / IMPORTS</span><h2>Import 비교</h2></div></div>
      <div className="import-grid">
        <ImportGroup title="공통" items={imports.shared} />
        <ImportGroup title="CODE A에만" items={imports.only_a} />
        <ImportGroup title="CODE B에만" items={imports.only_b} />
      </div>
    </section>
  </>
}

function ImportGroup({ title, items }: { title: string; items: string[] }) {
  return <div className="import-group"><h3>{title}</h3><div className="tag-list">{items.length ? items.map((item) => <code key={item}>{item}</code>) : <span className="muted">없음</span>}</div></div>
}
