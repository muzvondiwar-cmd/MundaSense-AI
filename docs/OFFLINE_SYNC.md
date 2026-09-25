# Offline storage and synchronization

## What works without the backend

The installed PWA shell, logo, navigation, saved preferences and previously cached results open
without internet. Assessment changes auto-save to Dexie/IndexedDB. A farmer can finish the form and
save it locally while disconnected.

MundaSense deliberately does **not** run a JavaScript copy of the model. An offline submission is
shown as **Saved offline—prediction pending** until the Python service is reachable.

## Browser stores

| Store | Key | Contents |
| --- | --- | --- |
| `drafts` | draft ID | Current wizard step, values and update time |
| `queue` | idempotency key | Entity type, payload, status, attempts and next retry time |
| `assessments` | assessment UUID | Cached completed result for local continuity |

The Settings page reports browser quota usage, exports these stores as JSON and can clear them after
confirmation.

## Retry rules

- Online events trigger an immediate attempt.
- A background browser timer tries every 30 seconds while the app is open.
- Failed records use exponential backoff starting at four seconds, capped at five minutes.
- **Sync now** bypasses the timer for records whose retry time has arrived.
- Validation failures remain visible as failed queue items; the browser does not silently alter data.

## Idempotency and conflicts

- Farms and fields use browser-generated UUIDs. Repeating an existing ID returns the existing entity.
- Assessments use a stable idempotency key in both the queue and server database.
- The backend records synchronization events with a unique key. Replaying a completed request returns
  the original entity ID.
- Assessments are immutable. A corrected record is a new assessment, avoiding ambiguous merges.
- Farms/fields currently use server-first conflict behavior for an existing UUID. A production pilot
  should add a user-visible timestamp comparison and merge screen.

## Demonstrating offline mode

1. Open New assessment while connected and enter values; wait one second for auto-save.
2. In browser developer tools, enable offline mode, or stop FastAPI.
3. Submit. Confirm **Saved offline—prediction pending** and a queue count of one.
4. Restore FastAPI/network and choose **Sync now**.
5. Open History and confirm one synchronized result, not a duplicate.

## Operational warning

IndexedDB belongs to a browser profile. Clearing site data, using private browsing or replacing the
device can remove unsynchronized records. Export a backup before field demonstrations and keep the
local SQLite file backed up separately.
