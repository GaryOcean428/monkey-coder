/**
 * Permission Manager for Monkey Coder CLI
 * 
 * Provides glob-based permission controls for file access and command execution
 * similar to Claude Code's settings.json approach.
 */

import * as fs from 'fs';
import * as fsPromises from 'fs/promises';
import * as path from 'path';
import * as os from 'os';
import { minimatch } from 'minimatch';

export interface PermissionRules {
  fileRead: { allow: string[]; deny: string[] };
  fileWrite: { allow: string[]; deny: string[] };
  shellExecute: { allow: string[]; deny: string[] };
  requireApproval: string[];  // Tools that always need approval
}

const DEFAULT_PERMISSIONS: PermissionRules = {
  fileRead: {
    allow: ['**/*'],
    deny: ['**/.env*', '**/secrets*', '**/*.pem', '**/*.key', '**/.ssh/**'],
  },
  fileWrite: {
    allow: ['**/*'],
    deny: ['**/.git/**', '**/node_modules/**', '**/.env*', '**/*.pem', '**/*.key'],
  },
  shellExecute: {
    allow: ['npm *', 'yarn *', 'pnpm *', 'git *', 'node *', 'python *', 'pytest *', 'ls *', 'cat *', 'grep *', 'find *'],
    deny: ['rm -rf /*', 'sudo *', 'curl * | sh', 'wget * | sh', 'dd *', 'mkfs *'],
  },
  requireApproval: ['shell_execute', 'file_delete', 'file_write'],
};

const CONFIG_DIR = path.join(os.homedir(), '.monkey-coder');
const PERMISSIONS_FILE = path.join(CONFIG_DIR, 'permissions.json');
const PROJECT_RC_FILE = '.monkeyrc.json';

export class PermissionManager {
  private globalRules: PermissionRules;
  private projectRules: Partial<PermissionRules> | null = null;
  private workingDir: string;

  constructor(workingDir: string = process.cwd()) {
    this.workingDir = workingDir;
    this.globalRules = this.loadGlobalRules();
    this.projectRules = this.loadProjectRules();
  }

  private loadGlobalRules(): PermissionRules {
    try {
      if (fs.existsSync(PERMISSIONS_FILE)) {
        const content = fs.readFileSync(PERMISSIONS_FILE, 'utf-8');
        return { ...DEFAULT_PERMISSIONS, ...JSON.parse(content) };
      }
    } catch (error) {
      console.warn('Failed to load global permissions:', error);
    }
    return DEFAULT_PERMISSIONS;
  }

  private loadProjectRules(): Partial<PermissionRules> | null {
    try {
      const rcPath = path.join(this.workingDir, PROJECT_RC_FILE);
      if (fs.existsSync(rcPath)) {
        const content = fs.readFileSync(rcPath, 'utf-8');
        const rc = JSON.parse(content);
        return rc.permissions || null;
      }
    } catch (error) {
      console.warn('Failed to load project permissions:', error);
    }
    return null;
  }

  private getMergedRules(): PermissionRules {
    if (!this.projectRules) {
      return this.globalRules;
    }

    return {
      fileRead: {
        allow: [...this.globalRules.fileRead.allow, ...(this.projectRules.fileRead?.allow || [])],
        deny: [...this.globalRules.fileRead.deny, ...(this.projectRules.fileRead?.deny || [])],
      },
      fileWrite: {
        allow: [...this.globalRules.fileWrite.allow, ...(this.projectRules.fileWrite?.allow || [])],
        deny: [...this.globalRules.fileWrite.deny, ...(this.projectRules.fileWrite?.deny || [])],
      },
      shellExecute: {
        allow: [...this.globalRules.shellExecute.allow, ...(this.projectRules.shellExecute?.allow || [])],
        deny: [...this.globalRules.shellExecute.deny, ...(this.projectRules.shellExecute?.deny || [])],
      },
      requireApproval: [...this.globalRules.requireApproval, ...(this.projectRules.requireApproval || [])],
    };
  }

  private matchesAny(value: string, patterns: string[]): boolean {
    return patterns.some(pattern => minimatch(value, pattern, { dot: true, matchBase: true }));
  }

  canReadFile(filePath: string): { allowed: boolean; reason?: string } {
    const rules = this.getMergedRules();
    const absolutePath = path.isAbsolute(filePath) ? filePath : path.join(this.workingDir, filePath);
    const relativePath = path.relative(this.workingDir, absolutePath);

    // Check denied paths first
    if (this.matchesAny(relativePath, rules.fileRead.deny)) {
      return { allowed: false, reason: `File matches deny pattern` };
    }

    // Check allowed paths
    if (!this.matchesAny(relativePath, rules.fileRead.allow)) {
      return { allowed: false, reason: `File does not match any allow pattern` };
    }

    return { allowed: true };
  }

  canWriteFile(filePath: string): { allowed: boolean; reason?: string } {
    const rules = this.getMergedRules();
    const absolutePath = path.isAbsolute(filePath) ? filePath : path.join(this.workingDir, filePath);
    const relativePath = path.relative(this.workingDir, absolutePath);

    // Check denied paths first
    if (this.matchesAny(relativePath, rules.fileWrite.deny)) {
      return { allowed: false, reason: `File matches deny pattern` };
    }

    // Check allowed paths
    if (!this.matchesAny(relativePath, rules.fileWrite.allow)) {
      return { allowed: false, reason: `File does not match any allow pattern` };
    }

    return { allowed: true };
  }

  canExecuteCommand(command: string): { allowed: boolean; reason?: string; requiresApproval?: boolean } {
    const rules = this.getMergedRules();

    // Check denied commands first
    if (this.matchesAny(command, rules.shellExecute.deny)) {
      return { allowed: false, reason: `Command is explicitly denied` };
    }

    // Check allowed commands
    if (!this.matchesAny(command, rules.shellExecute.allow)) {
      return { allowed: false, reason: `Command is not in allowed list` };
    }

    // Check if approval is required
    const requiresApproval = rules.requireApproval.includes('shell_execute');

    return { allowed: true, requiresApproval };
  }

  toolRequiresApproval(toolName: string): boolean {
    const rules = this.getMergedRules();
    return rules.requireApproval.includes(toolName);
  }

  async saveGlobalRules(rules: Partial<PermissionRules>): Promise<void> {
    try {
      // Ensure config directory exists
      await fsPromises.mkdir(CONFIG_DIR, { recursive: true });

      // Merge with existing rules
      const updatedRules = { ...this.globalRules, ...rules };
      
      // Save to file
      await fsPromises.writeFile(PERMISSIONS_FILE, JSON.stringify(updatedRules, null, 2), 'utf-8');
      
      // Reload rules
      this.globalRules = updatedRules;
    } catch (error) {
      throw new Error(`Failed to save global permissions: ${error}`);
    }
  }

  async saveProjectRules(rules: Partial<PermissionRules>): Promise<void> {
    try {
      const rcPath = path.join(this.workingDir, PROJECT_RC_FILE);
      
      // Load existing .monkeyrc.json if it exists
      let rc: any = {};
      if (fs.existsSync(rcPath)) {
        const content = await fsPromises.readFile(rcPath, 'utf-8');
        rc = JSON.parse(content);
      }

      // Merge permissions
      rc.permissions = { ...rc.permissions, ...rules };
      
      // Save to file
      await fsPromises.writeFile(rcPath, JSON.stringify(rc, null, 2), 'utf-8');
      
      // Reload rules
      this.projectRules = rc.permissions;
    } catch (error) {
      throw new Error(`Failed to save project permissions: ${error}`);
    }
  }

  getGlobalRules(): PermissionRules {
    return { ...this.globalRules };
  }

  getProjectRules(): Partial<PermissionRules> | null {
    return this.projectRules ? { ...this.projectRules } : null;
  }

  getMergedRulesPublic(): PermissionRules {
    return this.getMergedRules();
  }

  getPermissionsFilePath(): string {
    return PERMISSIONS_FILE;
  }

  getProjectRCPath(): string {
    return path.join(this.workingDir, PROJECT_RC_FILE);
  }
}
