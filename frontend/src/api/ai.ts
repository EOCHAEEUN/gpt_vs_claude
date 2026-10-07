import { apiBaseUrl } from './compare'
import type { CompareRequest } from '../types/comparison'
import type { AIExplanation, ConceptExplanation, ConceptRequest, OllamaStatus } from '../types/explanation'

export class ApiError extends Error {
  constructor(message: string, public code: string) { super(message) }
}

async function checkedJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body: unknown = await response.json().catch(() => null)
    const detail = typeof body === 'object' && body !== null && 'detail' in body ? body.detail : null
    if (typeof detail === 'object' && detail !== null && 'message' in detail && typeof detail.message === 'string') {
      const code = 'code' in detail && typeof detail.code === 'string' ? detail.code : 'request_failed'
      throw new ApiError(detail.message, code)
    }
    if (response.status === 422) throw new ApiError('입력 코드를 확인해 주세요. AI 해설은 코드당 12,000자 이하를 지원합니다.', 'validation')
    throw new ApiError(`AI 요청에 실패했습니다. (${response.status})`, 'request_failed')
  }
  return response.json() as Promise<T>
}

export async function getOllamaStatus(): Promise<OllamaStatus> {
  return checkedJson<OllamaStatus>(await fetch(`${apiBaseUrl}/api/ai/status`))
}

export async function explainCodes(input: CompareRequest): Promise<AIExplanation> {
  return checkedJson<AIExplanation>(await fetch(`${apiBaseUrl}/api/explain`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(input),
  }))
}

export async function explainConcept(input: ConceptRequest): Promise<ConceptExplanation> {
  return checkedJson<ConceptExplanation>(await fetch(`${apiBaseUrl}/api/explain/concept`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(input),
  }))
}
