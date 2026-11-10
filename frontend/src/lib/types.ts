// Shared TypeScript types mirroring the FastAPI (Pydantic) schemas.

export interface UserPublic {
  user_id: string;
  username: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: UserPublic;
}

export interface LegalSource {
  document: string;
  document_id?: string | null;
  page?: number | null;
  chunk_index?: number | null;
  court_type?: string | null;
  court_name?: string | null;
  distance?: number | null;
  source_url?: string | null;
}

export interface ChatResponse {
  conversation_id: string;
  question: string;
  answer: string;
  sources: LegalSource[];
  retrieved_count: number;
  disclaimer: string;
}

export interface MessagePublic {
  message_id: string;
  conversation_id: string;
  role: string;
  content: string;
  sources: LegalSource[];
  created_at?: string | null;
}

export interface ConversationSummary {
  conversation_id: string;
  title: string;
  message_count: number;
  last_message_at?: string | null;
}

export interface SearchResult {
  text: string;
  source: string;
  document_id?: string | null;
  page?: number | null;
  chunk_index?: number | null;
  court_type?: string | null;
  court_name?: string | null;
  acts?: string | null;
  sections?: string | null;
  score?: number | null;
  title?: string | null;
  source_url?: string | null;
}

export interface SearchResponse {
  query: string;
  mode: string;
  total: number;
  results: SearchResult[];
}

export interface DocumentSummary {
  document_id: string;
  file_name: string;
  title: string;
  source_type: string;
  source_url?: string | null;
  legal_category: string;
  court_type: string;
  court_name: string;
  case_name: string;
  case_number: string;
  judgment_date: string;
  acts: string;
  sections: string;
  page_count: number;
  ocr_used: boolean;
  content_hash: string;
  ingested_at?: string | null;
  chunk_count: number;
}

export interface DocumentDetail extends DocumentSummary {
  metadata: Record<string, unknown>;
  extracted_information: Record<string, unknown>;
}

export interface CaseSummary {
  document_id: string;
  case_name: string;
  case_number: string;
  court_type: string;
  court_name: string;
  legal_category: string;
  judgment_date: string;
  acts: string;
  sections: string;
  source_url?: string | null;
  file_name: string;
}

export interface CaseDetail extends CaseSummary {
  important_findings: string[];
  source_references: string[];
  required_documents: string[];
  legal_procedure: string[];
  timeline?: string | null;
  government_forms: string[];
  metadata: Record<string, unknown>;
}

export interface Procedure {
  document_id: string;
  title: string;
  legal_category: string;
  acts: string;
  sections: string;
  court_name: string;
  legal_procedure: string[];
  required_documents: string[];
  government_forms: string[];
  timeline?: string | null;
  source_url?: string | null;
  file_name: string;
}

export interface AdminStats {
  total_users: number;
  active_users: number;
  admin_users: number;
  total_documents: number;
  total_chunks: number;
  total_conversations: number;
  total_messages: number;
  llm_configured: boolean;
  llm_provider: string;
  embedding_model: string;
  llm_model: string;
  collections: { name: string; count: number }[];
}

export interface SystemReport {
  generated_at: string;
  stats: AdminStats;
  documents_by_court_type: Record<string, number>;
  documents_by_category: Record<string, number>;
  users_by_role: Record<string, number>;
  top_acts: { label: string; value: number }[];
}

export interface SystemStats {
  documents: number;
  chunks: number;
  sources: number;
  llm_configured: boolean;
  llm_provider: string;
  embedding_model: string;
}

export interface SearchFilterOptions {
  court_types: string[];
  acts: string[];
  categories: string[];
}

export interface CaseFilterOptions {
  court_types: string[];
  categories: string[];
}

export interface UploadResponse {
  document_id: string;
  file_name: string;
  page_count: number;
  total_chunks: number;
  ocr_used: boolean;
  is_valid: boolean;
  detail: string;
}
