import Dexie, { type EntityTable } from "dexie";

import type {
  AssessmentCreate,
  AssessmentResponse,
  SyncStatus,
} from "../types/api";

export interface AssessmentDraft {
  id: string;
  step: number;
  values: AssessmentCreate & Record<string, unknown>;
  updatedAt: string;
}

export interface QueueRecord {
  idempotencyKey: string;
  entityType: "assessment" | "farm" | "field";
  payload: Record<string, unknown>;
  status: SyncStatus;
  attempts: number;
  createdAt: string;
  updatedAt: string;
  nextAttemptAt: number;
  error?: string;
}

export interface CachedAssessment {
  assessment_id: string;
  created_at: string;
  result: AssessmentResponse;
}

class MundaSenseDatabase extends Dexie {
  drafts!: EntityTable<AssessmentDraft, "id">;
  queue!: EntityTable<QueueRecord, "idempotencyKey">;
  assessments!: EntityTable<CachedAssessment, "assessment_id">;

  constructor() {
    super("mundasense-offline-v1");
    this.version(1).stores({
      drafts: "&id, updatedAt",
      queue: "&idempotencyKey, entityType, status, nextAttemptAt, createdAt",
      assessments: "&assessment_id, created_at",
    });
  }
}

export const offlineDb = new MundaSenseDatabase();
export const offlineEvents = new EventTarget();

function changed() {
  offlineEvents.dispatchEvent(new Event("change"));
}

export async function saveDraft(draft: AssessmentDraft) {
  await offlineDb.drafts.put(draft);
  changed();
}

export async function loadDraft(id = "new-assessment") {
  return offlineDb.drafts.get(id);
}

export async function removeDraft(id = "new-assessment") {
  await offlineDb.drafts.delete(id);
  changed();
}

export async function enqueueRecord(
  entityType: QueueRecord["entityType"],
  payload: Record<string, unknown>,
  idempotencyKey: string = crypto.randomUUID(),
) {
  const now = new Date().toISOString();
  await offlineDb.queue.put({
    idempotencyKey,
    entityType,
    payload,
    status: "pending",
    attempts: 0,
    createdAt: now,
    updatedAt: now,
    nextAttemptAt: Date.now(),
  });
  changed();
  return idempotencyKey;
}

export async function dueQueueRecords() {
  const records = await offlineDb.queue
    .where("status")
    .anyOf("pending", "failed")
    .toArray();
  return records
    .filter((item) => item.nextAttemptAt <= Date.now())
    .slice(0, 50);
}

export async function markQueueFailed(key: string, error: string) {
  const record = await offlineDb.queue.get(key);
  if (!record) return;
  const attempts = record.attempts + 1;
  const backoff = Math.min(5 * 60_000, 2 ** attempts * 2_000);
  await offlineDb.queue.update(key, {
    status: "failed",
    attempts,
    error,
    updatedAt: new Date().toISOString(),
    nextAttemptAt: Date.now() + backoff,
  });
  changed();
}

export async function removeQueued(key: string) {
  await offlineDb.queue.delete(key);
  changed();
}

export async function queueCounts() {
  const [pending, failed] = await Promise.all([
    offlineDb.queue.where("status").equals("pending").count(),
    offlineDb.queue.where("status").equals("failed").count(),
  ]);
  return { pending, failed, total: pending + failed };
}

export async function cacheAssessment(result: AssessmentResponse) {
  await offlineDb.assessments.put({
    assessment_id: result.assessment_id,
    created_at: result.created_at,
    result,
  });
  changed();
}

export async function clearOfflineData() {
  await offlineDb.transaction(
    "rw",
    offlineDb.drafts,
    offlineDb.queue,
    offlineDb.assessments,
    async () => {
      await Promise.all([
        offlineDb.drafts.clear(),
        offlineDb.queue.clear(),
        offlineDb.assessments.clear(),
      ]);
    },
  );
  changed();
}
