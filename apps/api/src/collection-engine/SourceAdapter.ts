/**
 * Source Adapter Interface
 * Defines contract for all knowledge source adapters
 */

export interface SourceConfig {
  sourceId: string;
  sourceType: string;
  sourceUrl?: string;
  sourceName?: string;
  collectionMethod: string;
  apiConfigRef?: string;
  robotsTxtPolicy?: string;
  tosStatus: string;
  language?: string;
  trustLevel: string;
  metadata?: Record<string, any>;
}

export interface CollectionOptions {
  dryRun?: boolean | undefined;
  maxDocuments?: number | undefined;
  maxDocumentSize?: number | undefined;
  maxRetries?: number | undefined;
  timeout?: number | undefined;
  allowPrivateNetworks?: boolean | undefined;
}

export interface CollectionItem {
  sourceId: string;
  originalUrl: string;
  finalUrl?: string;
  title?: string;
  content?: string | undefined;
  contentType?: string;
  language?: string;
  publicationDate?: string;
  author?: string;
  collectionTimestamp: Date;
  license?: string;
  licenseMetadata?: Record<string, any>;
  httpStatus?: number;
  checksum?: string;
  sizeBytes?: number;
  error?: string;
}

export interface CollectionResult {
  sourceId: string;
  status: 'success' | 'partial' | 'failed';
  itemsCollected: number;
  itemsFailed: number;
  itemsSkipped: number;
  bytesDownloaded: number;
  durationMs: number;
  items: CollectionItem[];
  errors: string[];
  metadata?: Record<string, any>;
}

export interface SourceAdapter {
  /**
   * Validate source configuration
   */
  validate(config: SourceConfig): Promise<{ valid: boolean; errors: string[] }>;

  /**
   * Execute collection
   */
  collect(config: SourceConfig, options: CollectionOptions): Promise<CollectionResult>;

  /**
   * Check if source supports robots.txt compliance
   */
  supportsRobotsTxt(): boolean;

  /**
   * Get rate limit configuration for this source
   */
  getRateLimits(): {
    requestsPerWindow: number;
    windowSeconds: number;
    concurrentRequests: number;
  };
}
