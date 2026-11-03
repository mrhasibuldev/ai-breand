/**
 * Storage Provider Interface
 *
 * Provider-independent storage operations interface.
 * This allows switching between different storage providers (Neon, AWS S3, Cloudflare R2, etc.)
 * without changing application code.
 */

export interface ObjectMetadata {
  key: string;
  sizeBytes: number;
  contentType: string;
  lastModified?: Date;
  etag?: string;
}

export interface UploadResult {
  key: string;
  url: string | undefined;
  metadata: ObjectMetadata;
}

export interface StorageProvider {
  /**
   * Upload a file to storage
   */
  upload(key: string, data: Buffer | Uint8Array | string, contentType: string, options?: UploadOptions): Promise<UploadResult>;

  /**
   * Download a file from storage
   */
  download(key: string): Promise<Buffer>;

  /**
   * Get object metadata without downloading the entire file
   */
  getMetadata(key: string): Promise<ObjectMetadata>;

  /**
   * Delete an object from storage
   */
  delete(key: string): Promise<void>;

  /**
   * Check if an object exists
   */
  exists(key: string): Promise<boolean>;

  /**
   * Generate a presigned URL for temporary access (if supported)
   */
  getPresignedUrl?(key: string, expiresIn: number): Promise<string>;

  /**
   * List objects in a bucket with optional prefix
   * Note: Some providers may not return all metadata fields (e.g., contentType) in list operations
   */
  list?(prefix?: string, maxKeys?: number): Promise<Partial<ObjectMetadata>[]>;

}

export interface UploadOptions {
  /**
   * Content encoding (e.g., 'gzip')
   */
  contentEncoding?: string;

  /**
   * Cache control header
   */
  cacheControl?: string;

  /**
   * Custom metadata
   */
  metadata?: Record<string, string>;
}

export interface StorageError extends Error {
  code?: string;
  statusCode?: number;
  key?: string;
}

export class StorageException extends Error implements StorageError {
  code?: string;
  statusCode?: number;
  key?: string;

  constructor(message: string, code?: string, statusCode?: number, key?: string) {
    super(message);
    this.name = 'StorageException';
    if (code !== undefined) this.code = code;
    if (statusCode !== undefined) this.statusCode = statusCode;
    if (key !== undefined) this.key = key;
  }
}
