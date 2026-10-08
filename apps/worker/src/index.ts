/** Foundation-only worker entrypoint. Job consumers are added in a later phase. */
export type WorkerJobKind =
  | 'ai_processing'
  | 'notification_delivery'
  | 'memory_lifecycle'
  | 'data_deletion'
  | 'data_export'
  | 'usage_processing';

export function isSupportedJobKind(value: string): value is WorkerJobKind {
  return [
    'ai_processing',
    'notification_delivery',
    'memory_lifecycle',
    'data_deletion',
    'data_export',
    'usage_processing',
  ].includes(value);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  process.stdout.write('NexusAI worker foundation ready; no jobs are registered yet.\n');
}
