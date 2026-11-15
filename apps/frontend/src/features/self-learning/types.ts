export interface SelfLearningSubject {
  id: string;
  student_id: string;
  name: string;
  code?: string | null;
  department: string;
  description?: string | null;
  color_hex: string;
  icon_name: string;
  materials_count: number;
  created_at: string;
  updated_at: string;
}

export interface SelfLearningMaterial {
  id: string;
  student_id: string;
  subject_id: string;
  title: string;
  file_name: string;
  file_type: string;
  mime_type: string;
  file_size_bytes: number;
  file_hash: string;
  extracted_topics: string[];
  status: string;
  created_at: string;
  chunks_count: number;
}

export interface StorageQuota {
  student_id: string;
  used_bytes: number;
  total_quota_bytes: number;
  used_percentage: number;
  materials_count: number;
}

export interface QuestionOut {
  id: string;
  test_id: string;
  question_number: number;
  question_text: string;
  options: Record<string, string>;
  correct_option: string;
  explanation: string;
  bloom_level: string;
  difficulty: string;
  is_quantitative: boolean;
  formula_latex?: string | null;
  step_by_step_solution: string[];
  topic_tag?: string | null;
  created_at: string;
}

export interface SelfLearningTest {
  id: string;
  student_id: string;
  subject_id: string;
  title: string;
  difficulty: string;
  target_topics: string[];
  total_questions: number;
  status: string;
  created_at: string;
  updated_at: string;
  questions: QuestionOut[];
}

export interface QuestionEvaluationDetail {
  question_id: string;
  question_number: number;
  question_text: string;
  options: Record<string, string>;
  selected_option: string | null;
  correct_option: string;
  is_correct: boolean;
  explanation: string;
  bloom_level: string;
  difficulty: string;
  is_quantitative: boolean;
  formula_latex?: string | null;
  step_by_step_solution: string[];
  topic_tag?: string | null;
}

export interface TopicScore {
  topic: string;
  correct: number;
  total: number;
  percentage: number;
  status: "Strong" | "Moderate" | "Weak";
}

export interface TestResultOut {
  id: string;
  test_id: string;
  student_id: string;
  subject_id: string;
  score: number;
  total_questions: number;
  percentage: number;
  passed: boolean;
  answers: Record<string, string>;
  detailed_results: QuestionEvaluationDetail[];
  topic_breakdown: TopicScore[];
  time_taken_seconds?: number | null;
  created_at: string;
}

export interface TopicMasteryDetail {
  topic: string;
  total_attempted: number;
  total_correct: number;
  mastery_percentage: number;
  status: "Strong" | "Moderate" | "Weak";
  recommendation: string;
}

export interface SubjectMasteryOut {
  subject_id: string;
  student_id: string;
  overall_mastery_percentage: number;
  total_tests_taken: number;
  total_questions_attempted: number;
  strong_topics_count: number;
  moderate_topics_count: number;
  weak_topics_count: number;
  topics: TopicMasteryDetail[];
}

export interface SubjectCreatePayload {
  name: string;
  code?: string;
  department: string;
  description?: string;
  color_hex?: string;
  icon_name?: string;
}

export interface TestGeneratePayload {
  subject_id: string;
  count: number;
  difficulty: "basic" | "medium" | "hard" | "mixed";
  topics?: string[];
  title?: string;
}

export interface TestRegeneratePayload {
  mode: "weak_focus" | "balanced" | "challenge";
  count?: number;
  title?: string;
}
