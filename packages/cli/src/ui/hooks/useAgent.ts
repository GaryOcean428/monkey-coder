/**
 * useAgent - Hook for agent execution and tool management
 */
import { useState, useCallback, useEffect } from 'react';
import { MCPClientManager } from '../../mcp-client.js';
import { Task, ToolCall } from '../types.js';

export interface UseAgentOptions {
  mcpServers?: Array<{
    name: string;
    type: 'stdio' | 'sse' | 'http';
    command?: string;
    args?: string[];
    url?: string;
  }>;
  autoApprove?: boolean;
}

export interface UseAgentReturn {
  tasks: Task[];
  currentTool: string | null;
  pendingToolCall: ToolCall | null;
  executeTool: (toolCall: ToolCall) => Promise<void>;
  approveTool: () => Promise<void>;
  rejectTool: () => void;
  isExecuting: boolean;
  error: Error | null;
}

export function useAgent(options: UseAgentOptions = {}): UseAgentReturn {
  const [mcpClient] = useState(() => new MCPClientManager());
  const [tasks, setTasks] = useState<Task[]>([]);
  const [currentTool, setCurrentTool] = useState<string | null>(null);
  const [pendingToolCall, setPendingToolCall] = useState<ToolCall | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Initialize MCP servers
  useEffect(() => {
    const initMCPServers = async () => {
      if (!options.mcpServers) return;

      for (const serverConfig of options.mcpServers) {
        try {
          mcpClient.registerServer({
            name: serverConfig.name,
            type: serverConfig.type,
            command: serverConfig.command,
            args: serverConfig.args,
            url: serverConfig.url,
            enabled: true,
          });

          await mcpClient.connect(serverConfig.name);
        } catch (err) {
          console.error(`Failed to connect to MCP server ${serverConfig.name}:`, err);
        }
      }
    };

    initMCPServers();

    return () => {
      // Cleanup: disconnect all servers
      mcpClient.disconnectAll();
    };
  }, [options.mcpServers, mcpClient]);

  const executeTool = useCallback(
    async (toolCall: ToolCall) => {
      if (!options.autoApprove) {
        // Request approval
        setPendingToolCall(toolCall);
        return;
      }

      // Auto-approve and execute
      await executeToolInternal(toolCall);
    },
    [options.autoApprove]
  );

  const executeToolInternal = async (toolCall: ToolCall) => {
    setIsExecuting(true);
    setCurrentTool(toolCall.name);
    
    const taskId = `task-${Date.now()}`;
    setTasks((prev) => [
      ...prev,
      {
        id: taskId,
        title: `Executing ${toolCall.name}`,
        status: 'running',
      },
    ]);

    try {
      // Execute the tool
      const result = await mcpClient.executeTool(
        toolCall.name,
        toolCall.args
      );

      if (result.isError) {
        throw new Error(result.content[0]?.text || 'Tool execution failed');
      }

      // Update task status
      setTasks((prev) =>
        prev.map((task) =>
          task.id === taskId
            ? { ...task, status: 'completed' as const }
            : task
        )
      );
    } catch (err) {
      setError(err as Error);
      setTasks((prev) =>
        prev.map((task) =>
          task.id === taskId
            ? { ...task, status: 'failed' as const }
            : task
        )
      );
    } finally {
      setIsExecuting(false);
      setCurrentTool(null);
    }
  };

  const approveTool = useCallback(async () => {
    if (!pendingToolCall) return;

    const toolCall = pendingToolCall;
    setPendingToolCall(null);
    await executeToolInternal(toolCall);
  }, [pendingToolCall]);

  const rejectTool = useCallback(() => {
    setPendingToolCall(null);
  }, []);

  return {
    tasks,
    currentTool,
    pendingToolCall,
    executeTool,
    approveTool,
    rejectTool,
    isExecuting,
    error,
  };
}
