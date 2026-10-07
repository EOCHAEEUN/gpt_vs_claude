export interface OllamaStatus {
  available: boolean
  model: string | null
  message: string
}

export interface ArchitectureAnalysis {
  title: string
  explanation: string
  evidence: string[]
}

export interface Tradeoff {
  topic: string
  code_a: string
  code_b: string
  explanation: string
}

export interface LearningPoint {
  concept: string
  reason: string
  related_code: 'A' | 'B' | 'both' | null
  difficulty: 'beginner' | 'intermediate' | 'advanced'
}

export interface AIExplanation {
  summary: string
  architecture: ArchitectureAnalysis[]
  tradeoffs: Tradeoff[]
  learning_points: LearningPoint[]
  recommendation_context: string
}

export interface ConceptRequest {
  concept: string
  prompt: string
  code_a: string
  code_b: string
  context: string
}

export interface ConceptExplanation {
  concept: string
  simple_explanation: string
  analogy: string
  in_this_code: string
  simple_example: string
  when_to_use: string
  necessity: string
}
