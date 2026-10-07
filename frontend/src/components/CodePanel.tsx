import { CodeEditor } from './CodeEditor'

const choices = ['GPT', 'Claude', 'Gemini', 'Copilot', 'Other']

interface Props {
  side: 'A' | 'B'
  code: string
  setCode: (value: string) => void
  model: string
  setModel: (value: string) => void
  other: string
  setOther: (value: string) => void
}

export function CodePanel({ side, code, setCode, model, setModel, other, setOther }: Props) {
  return <section className="code-panel">
    <div className="panel-top">
      <div className="panel-heading"><span className={`code-badge ${side.toLowerCase()}`}>{side}</span><div><h3>CODE {side}</h3><p>Python source</p></div></div>
      <div className="model-picker">
        <label htmlFor={`model-${side}`}>모델</label>
        <select id={`model-${side}`} value={model} onChange={(event) => setModel(event.target.value)}>
          {choices.map((choice) => <option key={choice}>{choice}</option>)}
        </select>
      </div>
    </div>
    {model === 'Other' && <input className="other-input" aria-label={`CODE ${side} 모델 이름`} placeholder="모델 이름 입력" value={other} onChange={(event) => setOther(event.target.value)} maxLength={80} />}
    <CodeEditor value={code} onChange={setCode} ariaLabel={`CODE ${side} Python 코드`} />
    <div className="panel-foot"><span>PYTHON</span><span>{code ? `${code.split(/\r\n|\r|\n/).length} lines` : '코드를 붙여넣으세요'}</span></div>
  </section>
}
