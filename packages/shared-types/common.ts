/**
 * Common shared types
 */

export type Environment = 'development' | 'production' | 'test';

export interface BaseEntity {
  id: string;
  createdAt: string;
  updatedAt: string;
}

export interface User extends BaseEntity {
  email: string;
  name?: string;
  avatar?: string;
}
