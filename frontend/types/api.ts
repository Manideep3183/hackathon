export interface QuestionRequest {
  question: string;
}

export interface HackRXRequest {
  document_url: string;
  questions: QuestionRequest[];
}

export interface AnswerResponse {
  question: string;
  answer: string;
  sources: string[];
  confidence?: number;
}

export interface HackRXResponse {
  success: boolean;
  document_url: string;
  answers: AnswerResponse[];
  processing_time_ms?: number;
}

export interface ErrorResponse {
  success: boolean;
  error: string;
  details?: string;
}

export interface ApiConfig {
  baseURL: string;
  bearerToken: string;
}

export interface ProcessingStatus {
  isProcessing: boolean;
  currentStep: string;
  progress: number;
}