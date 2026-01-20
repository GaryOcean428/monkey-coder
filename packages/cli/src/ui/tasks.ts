/**
 * Task Runner - listr2 integration for multi-step operations
 */
import { Listr, ListrTask } from 'listr2';

export interface TaskStep {
  title: string;
  task: () => Promise<void>;
  enabled?: boolean | (() => boolean);
  skip?: () => boolean | string | Promise<boolean | string>;
}

export interface TaskRunnerOptions {
  concurrent?: boolean;
  exitOnError?: boolean;
  showTimer?: boolean;
  collapseSubtasks?: boolean;
}

/**
 * Run a series of tasks with progress display using listr2
 */
export async function runTasksWithProgress(
  title: string,
  steps: TaskStep[],
  options: TaskRunnerOptions = {}
): Promise<void> {
  const {
    concurrent = false,
    exitOnError = true,
    showTimer = true,
    collapseSubtasks = false,
  } = options;

  const tasks = new Listr<{ results: Record<string, any> }>(
    steps.map((step): ListrTask<{ results: Record<string, any> }> => ({
      title: step.title,
      enabled: step.enabled,
      skip: step.skip,
      task: async (ctx, task) => {
        try {
          await step.task();
        } catch (error) {
          task.title = `${step.title} - Failed`;
          throw error;
        }
      },
    })),
    {
      concurrent,
      exitOnError,
      rendererOptions: {
        collapseSubtasks,
      },
    }
  );

  await tasks.run({ results: {} });
}

/**
 * Create a subtask that can be added to a listr2 task
 */
export function createSubtask(
  title: string,
  task: () => Promise<void>
): ListrTask {
  return {
    title,
    task: async (_, subtask) => {
      try {
        await task();
        subtask.title = `${title} - Done`;
      } catch (error) {
        subtask.title = `${title} - Failed`;
        throw error;
      }
    },
  };
}

// Usage examples in comments
/**
 * Example 1: Simple sequential tasks
 * 
 * await runTasksWithProgress('Building project', [
 *   { title: 'Installing dependencies', task: async () => { await install() } },
 *   { title: 'Running linter', task: async () => { await lint() } },
 *   { title: 'Building code', task: async () => { await build() } },
 * ]);
 * 
 * Example 2: Conditional tasks
 * 
 * await runTasksWithProgress('Setup', [
 *   { 
 *     title: 'Checking Docker',
 *     task: async () => { await checkDocker() },
 *     skip: () => !needsDocker
 *   },
 * ]);
 * 
 * Example 3: Concurrent tasks
 * 
 * await runTasksWithProgress('Running tests', [
 *   { title: 'Unit tests', task: async () => { await runUnitTests() } },
 *   { title: 'Integration tests', task: async () => { await runIntegrationTests() } },
 * ], { concurrent: true });
 */
