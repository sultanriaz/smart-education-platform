import { apiRequest } from "../../lib/api-client";
import type {
  SelfLearningMaterial,
  SelfLearningSubject,
  SelfLearningTest,
  StorageQuota,
  SubjectCreatePayload,
  SubjectMasteryOut,
  TestGeneratePayload,
  TestRegeneratePayload,
  TestResultOut,
} from "./types";

export async function getSubjects(department?: string): Promise<SelfLearningSubject[]> {
  const query = department ? `?department=${encodeURIComponent(department)}` : "";
  return apiRequest<SelfLearningSubject[]>(`/api/v1/learning/self-learning/subjects${query}`);
}

export async function createSubject(payload: SubjectCreatePayload): Promise<SelfLearningSubject> {
  return apiRequest<SelfLearningSubject>("/api/v1/learning/self-learning/subjects", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function deleteSubject(subjectId: string): Promise<void> {
  await apiRequest(`/api/v1/learning/self-learning/subjects/${subjectId}`, {
    method: "DELETE",
  });
}

export async function getMaterials(subjectId?: string): Promise<SelfLearningMaterial[]> {
  const query = subjectId ? `?subject_id=${subjectId}` : "";
  return apiRequest<SelfLearningMaterial[]>(`/api/v1/learning/self-learning/materials${query}`);
}

export async function uploadMaterial(
  subjectId: string,
  file: File,
  title?: string,
): Promise<SelfLearningMaterial> {
  const formData = new FormData();
  formData.append("subject_id", subjectId);
  formData.append("file", file);
  if (title) formData.append("title", title);

  return apiRequest<SelfLearningMaterial>("/api/v1/learning/self-learning/materials/upload", {
    method: "POST",
    body: formData,
  });
}

export async function deleteMaterial(materialId: string): Promise<void> {
  await apiRequest(`/api/v1/learning/self-learning/materials/${materialId}`, {
    method: "DELETE",
  });
}

export async function getStorageQuota(): Promise<StorageQuota> {
  return apiRequest<StorageQuota>("/api/v1/learning/self-learning/quota");
}

export async function generateTest(payload: TestGeneratePayload): Promise<SelfLearningTest> {
  return apiRequest<SelfLearningTest>("/api/v1/learning/self-learning/tests/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function listTests(subjectId?: string): Promise<SelfLearningTest[]> {
  const query = subjectId ? `?subject_id=${subjectId}` : "";
  return apiRequest<SelfLearningTest[]>(`/api/v1/learning/self-learning/tests${query}`);
}

export async function getTest(testId: string): Promise<SelfLearningTest> {
  return apiRequest<SelfLearningTest>(`/api/v1/learning/self-learning/tests/${testId}`);
}

export async function deleteTest(testId: string): Promise<void> {
  await apiRequest(`/api/v1/learning/self-learning/tests/${testId}`, {
    method: "DELETE",
  });
}

export async function submitTest(
  testId: string,
  answers: Record<string, string>,
  timeTakenSeconds?: number,
): Promise<TestResultOut> {
  return apiRequest<TestResultOut>(`/api/v1/learning/self-learning/tests/${testId}/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      answers,
      time_taken_seconds: timeTakenSeconds,
    }),
  });
}

export async function getTestResult(testId: string): Promise<TestResultOut> {
  return apiRequest<TestResultOut>(`/api/v1/learning/self-learning/tests/${testId}/result`);
}

export async function regenerateTest(
  testId: string,
  payload: TestRegeneratePayload,
): Promise<SelfLearningTest> {
  return apiRequest<SelfLearningTest>(`/api/v1/learning/self-learning/tests/${testId}/regenerate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function getSubjectMastery(subjectId: string): Promise<SubjectMasteryOut> {
  return apiRequest<SubjectMasteryOut>(`/api/v1/learning/self-learning/subjects/${subjectId}/mastery`);
}
