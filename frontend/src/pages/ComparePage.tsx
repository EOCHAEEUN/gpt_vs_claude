import { useState } from 'react'
import { DiffEditor } from '@monaco-editor/react'
import { compareCodes } from '../api/compare'
import { CodePanel } from '../components/CodePanel'
import { ComparisonSummary } from '../components/ComparisonSummary'
import { Header } from '../components/Header'
import { MetricsTable } from '../components/MetricsTable'
import { RuffIssues } from '../components/RuffIssues'
import type { Comparison } from '../types/comparison'

export function ComparePage() {
  const [prompt, setPrompt] = useState('')
  const [codeA, setCodeA] = useState('')
  const [codeB, setCodeB] = useState('')
  const [modelA, setModelA] = useState('GPT')
  const [modelB, setModelB] = useState('Claude')
  const [otherA, setOtherA] = useState('')
  const [otherB, setOtherB] = useState('')
  const [comparison, setComparison] = useState<Comparison | null>(null)
  const [comparedCode, setComparedCode] = useState({ a: '', b: '' })
  const [diffOpen, setDiffOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleCompare() {
    if (!codeA.trim() || !codeB.trim()) {
      setError('CODE A와 CODE B에 Python 코드를 모두 입력해 주세요.')
      return
    }
    setLoading(true)
    setError('')
    setComparison(null)
    setDiffOpen(false)
    try {
      const result = await compareCodes({
        prompt, code_a: codeA, code_b: codeB,
        label_a: modelA === 'Other' ? otherA.trim() || 'Other' : modelA,
        label_b: modelB === 'Other' ? otherB.trim() || 'Other' : modelB,
      })
      setComparison(result)
      setComparedCode({ a: codeA, b: codeB })
      window.setTimeout(() => document.getElementById('results')?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 50)
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : '비교 중 오류가 발생했습니다.')
    } finally {
      setLoading(false)
    }
  }

  return <>
    <Header />
    <main className="main-container">
      <div className="hero"><span className="hero-kicker"><span className="kicker-dot" /> PYTHON CODE COMPARISON</span><h1>같은 요구사항,<br /><em>다른 코드.</em></h1><p>두 구현의 구조와 작성 방식의 차이를 객관적인 지표로 비교해 보세요.</p></div>

      <section className="prompt-section"><div className="field-title"><span className="step-number">01</span><div><h2>Original Prompt</h2><p>두 코드를 만들 때 사용한 원래 요구사항을 기록하세요.</p></div></div><textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} placeholder="예: FastAPI로 사용자 로그인 API를 만들어줘." rows={3} /></section>

      <div className="code-heading"><span className="step-number">02</span><div><h2>코드 입력</h2><p>비교할 Python 코드를 각각 붙여넣으세요.</p></div></div>
      <div className="code-grid">
        <CodePanel side="A" code={codeA} setCode={setCodeA} model={modelA} setModel={setModelA} other={otherA} setOther={setOtherA} />
        <CodePanel side="B" code={codeB} setCode={setCodeB} model={modelB} setModel={setModelB} other={otherB} setOther={setOtherB} />
      </div>
      <div className="action-area"><button className="compare-button" onClick={handleCompare} disabled={loading}>{loading ? '분석 중…' : 'Compare Codes'} <span aria-hidden="true">→</span></button><p>코드는 실행되지 않으며 AST와 Ruff로 정적 분석합니다.</p>{error && <div className="form-error" role="alert">{error}</div>}</div>

      {comparison && <div id="results" className="results">
        <div className="results-intro"><span className="step-number">03</span><div><h2>비교 결과</h2><p>{comparison.code_a.label}와 {comparison.code_b.label}의 코드 분석 결과입니다.</p></div></div>
        {(!comparison.code_a.valid_python || !comparison.code_b.valid_python) && <div className="syntax-alert" role="alert">
          {!comparison.code_a.valid_python && <p><strong>CODE A에 Python 문법 오류가 있습니다.</strong> {comparison.code_a.syntax_error?.message} · Line {comparison.code_a.syntax_error?.line}, Column {comparison.code_a.syntax_error?.offset}</p>}
          {!comparison.code_b.valid_python && <p><strong>CODE B에 Python 문법 오류가 있습니다.</strong> {comparison.code_b.syntax_error?.message} · Line {comparison.code_b.syntax_error?.line}, Column {comparison.code_b.syntax_error?.offset}</p>}
          <small>올바른 코드의 분석 결과는 계속 표시됩니다.</small>
        </div>}
        {comparison.code_a.metrics && comparison.code_b.metrics && <><MetricsTable comparison={comparison} /><ComparisonSummary comparison={comparison} /></>}
        <RuffIssues a={comparison.code_a} b={comparison.code_b} />
        <section className="result-section diff-section"><div className="section-heading"><div><span className="eyebrow">05 / SOURCE DIFF</span><h2>텍스트 차이</h2></div><button className="secondary-button" onClick={() => setDiffOpen(!diffOpen)}>{diffOpen ? 'Close Diff View' : 'Open Diff View'}</button></div>
          {diffOpen && <div className="diff-shell"><DiffEditor height="470px" language="python" theme="vs-light" original={comparedCode.a} modified={comparedCode.b} options={{ readOnly: true, renderSideBySide: true, minimap: { enabled: false }, automaticLayout: true, scrollBeyondLastLine: false }} /></div>}
        </section>
      </div>}
      <footer>Code Contrast <span>·</span> V0.1 <span>·</span> Python static analysis</footer>
    </main>
  </>
}
