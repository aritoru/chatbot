export interface ChatMessage {
  role: 'customer' | 'agent';
  content: string;
}

export interface Intake {
  issue_reference_number: string;
  created_at: string;
  game_system: string;
  problem_category: string;
  problem_description: string;
  urgency_level: string;
  summary: string;
  conversation_transcript: ChatMessage[];
}

export type InterviewStatus = 'in_progress' | 'awaiting_confirmation' | 'completed';
