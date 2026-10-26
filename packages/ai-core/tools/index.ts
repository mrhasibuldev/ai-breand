/**
 * NexusAI Tool Registry
 *
 * Registry for AI tools that can be called by the AI
 */

import {
  ToolRegistry,
  ToolDefinition,
  PermissionLevel,
  RiskLevel,
} from '../core/types';

/**
 * Tool Registry Implementation
 */
export class NexusToolRegistry implements ToolRegistry {
  private tools: Map<string, ToolDefinition> = new Map();

  /**
   * Register tool
   */
  register(tool: ToolDefinition): void {
    this.tools.set(tool.id, tool);
  }

  /**
   * Unregister tool
   */
  unregister(toolId: string): void {
    this.tools.delete(toolId);
  }

  /**
   * Get tool
   */
  get(toolId: string): ToolDefinition | undefined {
    return this.tools.get(toolId);
  }

  /**
   * List all tools
   */
  list(): ToolDefinition[] {
    return Array.from(this.tools.values());
  }

  /**
   * Execute tool
   */
  async execute(toolId: string, arguments: Record<string, any>): Promise<any> {
    const tool = this.tools.get(toolId);
    if (!tool) {
      throw new Error(`Tool ${toolId} not found`);
    }
    return await tool.execute(arguments);
  }
}

/**
 * Singleton instance
 */
export const toolRegistry = new NexusToolRegistry();
