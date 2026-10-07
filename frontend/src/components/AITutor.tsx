import { useEffect, useState } from 'react'
import { ApiError, explainCodes, explainConcept, getOllamaStatus } from '../api/ai'
import type { CompareRequest, Comparison } from '../types/comparison'
import type { AIExplanation, ConceptExplanation, LearningPoint, OllamaStatus } from '../types/explanation'

type TutorState = 'idle' | 'loading' | 'success' | 'error' | 'ollamaOffline'
type ConceptState = { status: 'loading' | 'success' | 'error'; result?: ConceptExplanation; error?: string }

interface Props {
  comparison: Comparison
  codeA: string
  codeB: string
}

export function AITutor({ comparison, codeA, codeB }: Props) {
  const [status, setStatus] = useState<OllamaStatus | null>(null)
  const [state, setState] = useState<TutorState>('idle')
  const [result, setResult] = useState<AIExplanation | null>(null)
  const [error, setError] = useState('')
  const [concepts, setConcepts] = useState<Record<number, ConceptState>>({})
  const [openConcept, setOpenConcept] = useState<number | null>(null)

  async function refreshStatus() {
    try {
      const next = await getOllamaStatus()
      setStatus(next)
      setState((current) => next.available ? current === 'ollamaOffline' ? 'idle' : current : 'ollamaOffline')
    } catch {
      setStatus({ available: false, model: null, message: 'Ollama 상태를 확인할 수 없습니다.' })
      setState('ollamaOffline')
    }
  }

  useEffect(() => { void refreshStatus() }, [])

  const input: CompareRequest = {
    prompt: comparison.prompt, code_a: codeA, code_b: codeB,
    label_a: comparison.code_a.label, label_b: comparison.code_b.label,
  }
  const syntaxInvalid = !comparison.code_a.valid_python || !comparison.code_b.valid_python
  const tooLong = codeA.length > 12_000 || codeB.length > 12_000 || comparison.prompt.length > 2_000

  async function handleExplain() {
    setState('loading')
    setResult(null)
    setConcepts({})
    setOpenConcept(null)
    setError('')
    try {
      setResult(await explainCodes(input))
      setState('success')
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : 'AI 해설을 가져오지 못했습니다.'
      setError(message)
      setState(cause instanceof ApiError && cause.code === 'offline' ? 'ollamaOffline' : 'error')
    }
  }

  async function handleConcept(point: LearningPoint, index: number) {
    if (openConcept === index && concepts[index]?.status === 'success') { setOpenConcept(null); return }
    setOpenConcept(index)
    if (concepts[index]?.status === 'success') return
    setConcepts((current) => ({ ...current, [index]: { status: 'loading' } }))
    try {
      const explanation = await explainConcept({ concept: point.concept, prompt: comparison.prompt, code_a: codeA, code_b: codeB, context: point.reason })
      setConcepts((current) => ({ ...current, [index]: { status: 'success', result: explanation } }))
    } catch (cause) {
      setConcepts((current) => ({ ...current, [index]: { status: 'error', error: cause instanceof Error ? cause.message : '설명을 가져오지 못했습니다.' } }))
    }
  }

  return <section className="result-section ai-tutor">
    <div className="section-heading"><div><span className="eyebrow">06 / AI CODE TUTOR</span><h2>구현 방식 이해하기</h2></div><span className={`ai-status ${status?.available ? 'online' : 'offline'}`}><span className="status-dot" />{status?.available ? `Ollama 연결됨 · ${status.model}` : 'Ollama 연결 안 됨'}</span></div>
    <p className="tutor-intro">정적 분석 결과와 실제 코드를 바탕으로 구조, 선택의 이유와 학습할 개념을 살펴봅니다.</p>
    {!status?.available && <div className="ai-notice" role="status"><p>{status?.message ?? 'Ollama 상태를 확인하고 있습니다.'}</p><small>Ollama를 실행하고 backend/.env의 OLLAMA_MODEL을 확인하세요. 위의 정적 분석 결과는 계속 사용할 수 있습니다.</small><button className="text-button" onClick={() => void refreshStatus()}>연결 다시 확인</button></div>}
    {syntaxInvalid && <p className="ai-notice">AI 해설을 시작하려면 두 코드의 Python 문법 오류를 먼저 수정해 주세요.</p>}
    {tooLong && <p className="ai-notice">AI 해설은 코드당 12,000자, 원래 프롬프트 2,000자 이하에서 사용할 수 있습니다. 정적 비교는 계속 이용할 수 있습니다.</p>}
    <button className="compare-button ai-button" onClick={() => void handleExplain()} disabled={!status?.available || syntaxInvalid || tooLong || state === 'loading'}>{state === 'loading' ? '두 코드의 구현 방식을 살펴보고 있습니다…' : 'AI로 차이 이해하기'}</button>
    {state === 'loading' && <div className="ai-loading" role="status"><span className="loading-dot" />Local AI가 코드를 분석하고 있습니다. 모델에 따라 시간이 걸릴 수 있습니다.</div>}
    {state === 'error' && <div className="form-error ai-error" role="alert">{error} 다시 시도해 주세요.</div>}
    {state === 'ollamaOffline' && error && <div className="form-error ai-error" role="alert">{error}</div>}
    {result && state === 'success' && <div className="ai-result">
      <div className="ai-summary"><span className="eyebrow">SUMMARY</span><p>{result.summary}</p></div>
      <div className="ai-block"><h3>01. 구조적 차이</h3>{result.architecture.length ? result.architecture.map((item, index) => <div className="architecture-item" key={index}><h4>{item.title}</h4><p>{item.explanation}</p>{item.evidence.length > 0 && <ul className="evidence-list">{item.evidence.map((evidence, evidenceIndex) => <li key={evidenceIndex}>{evidence}</li>)}</ul>}</div>) : <p className="muted">현재 코드만으로 뚜렷한 구조 차이를 확인하기 어렵습니다.</p>}</div>
      <div className="ai-block"><h3>02. Trade-offs</h3>{result.tradeoffs.length ? result.tradeoffs.map((item, index) => <div className="tradeoff-item" key={index}><h4>{item.topic}</h4><div className="tradeoff-columns"><p><strong>CODE A</strong>{item.code_a}</p><p><strong>CODE B</strong>{item.code_b}</p></div><p className="tradeoff-explanation">{item.explanation}</p></div>) : <p className="muted">현재 코드에서 설명할 뚜렷한 선택 차이가 없습니다.</p>}</div>
      <div className="ai-block"><h3>03. 이 코드에서 공부할 것</h3>{result.learning_points.length ? result.learning_points.slice(0, 3).map((point, index) => <div className="learning-item" key={`${point.concept}-${index}`}><div className="learning-top"><span className="learning-number">{String(index + 1).padStart(2, '0')}</span><div><h4>{point.concept}</h4><p>{point.reason}</p><small>{point.related_code === 'both' ? 'CODE A · CODE B' : point.related_code ? `CODE ${point.related_code}` : '관련 코드'} · {point.difficulty}</small></div><button className="secondary-button" onClick={() => void handleConcept(point, index)}>{openConcept === index && concepts[index]?.status === 'success' ? '접기' : '쉽게 설명해줘'}</button></div>
        {openConcept === index && <ConceptDetail state={concepts[index]} />}
      </div>) : <p className="muted">이 코드만으로 추천할 학습 개념이 없습니다.</p>}</div>
      <div className="ai-context"><strong>어떤 상황에 맞을까요?</strong><p>{result.recommendation_context}</p></div>
      <p className="ai-disclaimer">AI 해설은 학습을 돕는 설명입니다. 위의 코드와 분석 지표를 함께 확인해 주세요.</p>
    </div>}
  </section>
}

function ConceptDetail({ state }: { state?: ConceptState }) {
  if (!state || state.status === 'loading') return <div className="concept-detail" role="status">개념을 쉽게 풀어 설명하고 있습니다…</div>
  if (state.status === 'error') return <div className="concept-detail error-text" role="alert">{state.error}</div>
  const detail = state.result
  if (!detail) return null
  return <div className="concept-detail"><h5>한 줄로 말하면</h5><p>{detail.simple_explanation}</p><h5>쉽게 생각하면</h5><p>{detail.analogy}</p><h5>현재 코드에서는</h5><p>{detail.in_this_code}</p><h5>작은 예</h5><pre><code>{detail.simple_example}</code></pre><h5>언제 사용할까요?</h5><p>{detail.when_to_use}</p><h5>지금 꼭 필요한가요?</h5><p>{detail.necessity}</p></div>
}
