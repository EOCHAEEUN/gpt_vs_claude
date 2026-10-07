import Editor from '@monaco-editor/react'

interface Props {
  value: string
  onChange: (value: string) => void
  ariaLabel: string
}

export function CodeEditor({ value, onChange, ariaLabel }: Props) {
  return <div className="editor-shell" aria-label={ariaLabel}>
    <Editor
      height="450px"
      language="python"
      theme="vs-light"
      value={value}
      onChange={(next) => onChange(next ?? '')}
      options={{
        minimap: { enabled: false }, fontSize: 13, lineHeight: 21,
        fontFamily: 'Consolas, "Courier New", monospace',
        scrollBeyondLastLine: false, automaticLayout: true,
        tabSize: 4, wordWrap: 'on', padding: { top: 16, bottom: 16 },
        ariaLabel,
      }}
    />
  </div>
}
