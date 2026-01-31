/**
 * TaskList - Display hierarchical task progress with spinners
 */
import React from 'react';
import { Box, Text } from 'ink';

import { Task } from '../types.js';

interface TaskListProps {
  tasks: Task[];
}

interface TaskItemProps {
  task: Task;
  depth?: number;
}

const TaskItem: React.FC<TaskItemProps> = ({ task, depth = 0 }) => {
  const getIcon = (status: Task['status']) => {
    switch (status) {
      case 'pending':
        return '○';
      case 'completed':
        return '✓';
      case 'failed':
        return '✗';
      case 'running':
      default:
        return '⏳';
    }
  };

  const getColor = (status: Task['status']) => {
    switch (status) {
      case 'pending':
        return 'gray';
      case 'running':
        return 'yellow';
      case 'completed':
        return 'green';
      case 'failed':
        return 'red';
    }
  };

  const icon = getIcon(task.status);
  const color = getColor(task.status);

  return (
    <Box flexDirection="column" marginLeft={depth * 2}>
      <Box>
        <Text color={color}>{icon} </Text>
        <Text color={color}>{task.title}</Text>
      </Box>
      {task.subtasks && task.subtasks.length > 0 && (
        <Box flexDirection="column">
          {task.subtasks.map((subtask) => (
            <TaskItem key={subtask.id} task={subtask} depth={depth + 1} />
          ))}
        </Box>
      )}
    </Box>
  );
};

export const TaskList: React.FC<TaskListProps> = ({ tasks }) => {
  return (
    <Box flexDirection="column" paddingY={1}>
      {tasks.map((task) => (
        <TaskItem key={task.id} task={task} />
      ))}
    </Box>
  );
};
