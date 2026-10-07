import type { CompareRequest, Comparison } from '../types/comparison'

const baseUrl = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')

export async function compareCodes(input: CompareRequest): Promise<Comparison> {
  const response = await fetch(`${baseUrl}/api/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  })
  if (!response.ok) {
    if (response.status === 422) throw new Error('두 코드 입력란에 Python 코드를 넣어 주세요.')
    throw new Error(`비교 요청에 실패했습니다. (${response.status})`)
  }
  return response.json() as Promise<Comparison>
}
