/**
 * Tests for task runner utilities
 */
import { describe, it, expect, jest } from '@jest/globals';
import { runTasksWithProgress, createSubtask } from '../src/ui/tasks';

describe('Task Runner', () => {
  describe('runTasksWithProgress', () => {
    it('should run tasks sequentially', async () => {
      const results: string[] = [];
      
      await runTasksWithProgress('Test Tasks', [
        {
          title: 'Task 1',
          task: async () => {
            results.push('task1');
          },
        },
        {
          title: 'Task 2',
          task: async () => {
            results.push('task2');
          },
        },
      ]);

      expect(results).toEqual(['task1', 'task2']);
    });

    it('should handle task failures with exitOnError', async () => {
      const results: string[] = [];
      
      await expect(
        runTasksWithProgress(
          'Test Tasks',
          [
            {
              title: 'Task 1',
              task: async () => {
                results.push('task1');
              },
            },
            {
              title: 'Task 2',
              task: async () => {
                throw new Error('Task 2 failed');
              },
            },
            {
              title: 'Task 3',
              task: async () => {
                results.push('task3');
              },
            },
          ],
          { exitOnError: true }
        )
      ).rejects.toThrow('Task 2 failed');

      // Task 3 should not run because exitOnError is true
      expect(results).toEqual(['task1']);
    });

    it('should skip tasks when skip returns true', async () => {
      const results: string[] = [];
      
      await runTasksWithProgress('Test Tasks', [
        {
          title: 'Task 1',
          task: async () => {
            results.push('task1');
          },
        },
        {
          title: 'Task 2 (skipped)',
          task: async () => {
            results.push('task2');
          },
          skip: () => true,
        },
        {
          title: 'Task 3',
          task: async () => {
            results.push('task3');
          },
        },
      ]);

      expect(results).toEqual(['task1', 'task3']);
    });

    it('should respect enabled flag', async () => {
      const results: string[] = [];
      
      await runTasksWithProgress('Test Tasks', [
        {
          title: 'Task 1',
          task: async () => {
            results.push('task1');
          },
          enabled: true,
        },
        {
          title: 'Task 2 (disabled)',
          task: async () => {
            results.push('task2');
          },
          enabled: false,
        },
        {
          title: 'Task 3',
          task: async () => {
            results.push('task3');
          },
        },
      ]);

      expect(results).toEqual(['task1', 'task3']);
    });
  });

  describe('createSubtask', () => {
    it('should create a valid subtask', () => {
      const taskFn = async () => {
        // Task implementation
      };
      const subtask = createSubtask('Test Subtask', taskFn);

      expect(subtask).toHaveProperty('title', 'Test Subtask');
      expect(subtask).toHaveProperty('task');
      expect(typeof subtask.task).toBe('function');
    });

    it('should handle subtask execution', async () => {
      let executed = false;
      const subtask = createSubtask('Test Subtask', async () => {
        executed = true;
      });

      // Mock subtask context - using proper types
      const mockSubtask: any = {
        title: 'Test Subtask',
      };

      await subtask.task({}, mockSubtask);
      expect(executed).toBe(true);
    });
  });
});
