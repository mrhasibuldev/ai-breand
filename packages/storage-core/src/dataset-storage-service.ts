/**
 * Dataset Storage Service
 *
 * High-level service for dataset storage operations.
 * Provides safe object naming, validation, and metadata management for datasets.
 */

import { StorageProvider, ObjectMetadata, StorageException } from './storage-provider.js';

export interface DatasetMetadata {
  id: string;
  name: string;
  description?: string;
  datasetType: string;
  language: string;
  domain: string;
  taskType: string;
  version: string;
  fileFormat: string;
  recordCount?: number;
  languageDistribution?: Record<string, number>;
  createdAt: Date;
}

export interface DatasetUploadOptions {
  /**
   * User ID (owner of the dataset)
   */
  userId: string;

  /**
   * Dataset ID (UUID)
   */
  datasetId: string;

  /**
   * Dataset version
   */
  version: string;

  /**
   * File format (json, jsonl, csv, parquet, etc.)
   */
  fileFormat: string;

  /**
   * Metadata about the dataset
   */
  metadata: Omit<DatasetMetadata, 'id' | 'version' | 'fileFormat' | 'createdAt'>;
}

export interface AvatarUploadOptions {
  /**
   * User ID
   */
  userId: string;

  /**
   * File name
   */
  fileName: string;

  /**
   * File extension
   */
  fileExtension: string;
}

export class DatasetStorageService {
  constructor(private storage: StorageProvider) {}

  /**
   * Upload a dataset file
   * Generates a safe object key: datasets/{userId}/{datasetId}/versions/{version}.{format}
   */
  async uploadDataset(
    data: Buffer | Uint8Array | string,
    contentType: string,
    options: DatasetUploadOptions
  ): Promise<{ key: string; metadata: ObjectMetadata }> {
    const key = this.generateDatasetKey(options.userId, options.datasetId, options.version, options.fileFormat);

    try {
      const result = await this.storage.upload(key, data, contentType, {
        metadata: {
          datasetId: options.datasetId,
          version: options.version,
          datasetType: options.metadata.datasetType,
          language: options.metadata.language,
          domain: options.metadata.domain,
          taskType: options.metadata.taskType,
          recordCount: options.metadata.recordCount?.toString() || '0',
        },
      });

      return {
        key: result.key,
        metadata: result.metadata,
      };
    } catch (error) {
      throw new StorageException(
        `Dataset upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        'DATASET_UPLOAD_FAILED',
        500,
        key
      );
    }
  }

  /**
   * Download a dataset file
   */
  async downloadDataset(userId: string, datasetId: string, version: string, fileFormat: string): Promise<Buffer> {
    const key = this.generateDatasetKey(userId, datasetId, version, fileFormat);
    return await this.storage.download(key);
  }

  /**
   * Get dataset file metadata
   */
  async getDatasetMetadata(userId: string, datasetId: string, version: string, fileFormat: string): Promise<ObjectMetadata> {
    const key = this.generateDatasetKey(userId, datasetId, version, fileFormat);
    return await this.storage.getMetadata(key);
  }

  /**
   * Delete a dataset file
   */
  async deleteDataset(userId: string, datasetId: string, version: string, fileFormat: string): Promise<void> {
    const key = this.generateDatasetKey(userId, datasetId, version, fileFormat);
    await this.storage.delete(key);
  }

  /**
   * Check if a dataset version exists
   */
  async datasetExists(userId: string, datasetId: string, version: string, fileFormat: string): Promise<boolean> {
    const key = this.generateDatasetKey(userId, datasetId, version, fileFormat);
    return await this.storage.exists(key);
  }

  /**
   * List all versions of a dataset
   */
  async listDatasetVersions(userId: string, datasetId: string): Promise<Partial<ObjectMetadata>[]> {
    const prefix = `datasets/${userId}/${datasetId}/versions/`;
    if (this.storage.list) {
      return await this.storage.list(prefix);
    }
    return [];
  }

  /**
   * Upload a user avatar
   * Generates a safe object key: avatars/{userId}/{timestamp}.{ext}
   */
  async uploadAvatar(
    userId: string,
    data: Buffer | Uint8Array,
    contentType: string,
    fileExtension: string
  ): Promise<{ key: string; url: string; metadata: ObjectMetadata }> {
    const timestamp = Date.now();
    const key = `avatars/${userId}/${timestamp}.${fileExtension}`;

    try {
      const result = await this.storage.upload(key, data, contentType, {
        metadata: {
          userId,
          type: 'avatar',
          uploadedAt: new Date().toISOString(),
        },
      });

      // Generate public URL (for public bucket)
      // Note: For private buckets, use presigned URLs
      let url = '';
      if (this.storage.getPresignedUrl) {
        url = await this.storage.getPresignedUrl(key, 3600);
      }

      return {
        key: result.key,
        url,
        metadata: result.metadata,
      };
    } catch (error) {
      throw new StorageException(
        `Avatar upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        'AVATAR_UPLOAD_FAILED',
        500,
        key
      );
    }
  }

  /**
   * Download a user avatar
   */
  async downloadAvatar(userId: string, timestamp: number, fileExtension: string): Promise<Buffer> {
    const key = `avatars/${userId}/${timestamp}.${fileExtension}`;
    return await this.storage.download(key);
  }

  /**
   * Delete a user avatar
   */
  async deleteAvatar(userId: string, timestamp: number, fileExtension: string): Promise<void> {
    const key = `avatars/${userId}/${timestamp}.${fileExtension}`;
    await this.storage.delete(key);
  }

  /**
   * List all avatars for a user
   */
  async listUserAvatars(userId: string): Promise<Partial<ObjectMetadata>[]> {
    const prefix = `avatars/${userId}/`;
    if (this.storage.list) {
      return await this.storage.list(prefix);
    }
    return [];
  }

  /**
   * Generate a safe dataset object key
   */
  private generateDatasetKey(userId: string, datasetId: string, version: string, fileFormat: string): string {
    // Sanitize inputs to prevent path traversal
    const safeUserId = this.sanitizeKey(userId);
    const safeDatasetId = this.sanitizeKey(datasetId);
    const safeVersion = this.sanitizeKey(version);
    const safeFormat = this.sanitizeKey(fileFormat);

    return `datasets/${safeUserId}/${safeDatasetId}/versions/${safeVersion}.${safeFormat}`;
  }

  /**
   * Sanitize a key component to prevent path traversal
   */
  private sanitizeKey(key: string): string {
    // Remove any path traversal attempts
    return key.replace(/\.\./g, '').replace(/\//g, '').replace(/\\/g, '');
  }

  /**
   * Validate file type for datasets
   */
  static validateDatasetFileFormat(fileFormat: string): boolean {
    const allowedFormats = ['json', 'jsonl', 'csv', 'parquet', 'txt'];
    return allowedFormats.includes(fileFormat.toLowerCase());
  }

  /**
   * Validate file type for avatars
   */
  static validateAvatarFileFormat(fileExtension: string): boolean {
    const allowedExtensions = ['jpg', 'jpeg', 'png', 'webp', 'gif'];
    return allowedExtensions.includes(fileExtension.toLowerCase());
  }

  /**
   * Validate file size
   */
  static validateFileSize(sizeBytes: number, maxSizeBytes: number): boolean {
    return sizeBytes <= maxSizeBytes;
  }
}
