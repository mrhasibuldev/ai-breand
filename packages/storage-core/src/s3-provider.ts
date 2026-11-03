/**
 * S3-Compatible Storage Provider
 *
 * Implements StorageProvider interface for S3-compatible storage (Neon Object Storage, AWS S3, etc.)
 * Follows Neon S3 Client configuration requirements.
 */

import { S3Client, PutObjectCommand, GetObjectCommand, DeleteObjectCommand, HeadObjectCommand, ListObjectsV2Command } from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';
import { Readable } from 'stream';
import { StorageProvider, UploadResult, ObjectMetadata, UploadOptions, StorageException } from './storage-provider.js';

export interface S3ProviderConfig {
  /**
   * S3 endpoint URL (required for Neon Object Storage)
   */
  endpoint?: string;

  /**
   * AWS region
   */
  region: string;

  /**
   * Access key ID
   */
  accessKeyId: string;

  /**
   * Secret access key
   */
  secretAccessKey: string;

  /**
   * Bucket name
   */
  bucket: string;

  /**
   * Force path style (required for Neon Object Storage)
   */
  forcePathStyle?: boolean;
}

export class S3Provider implements StorageProvider {
  private client: S3Client;
  private bucket: string;

  constructor(config: S3ProviderConfig) {
    this.bucket = config.bucket;

    const clientConfig: any = {
      region: config.region,
      credentials: {
        accessKeyId: config.accessKeyId,
        secretAccessKey: config.secretAccessKey,
      },
      // forcePathStyle: true is REQUIRED for Neon Object Storage
      forcePathStyle: config.forcePathStyle ?? true,
    };

    // Only add endpoint if provided
    if (config.endpoint) {
      clientConfig.endpoint = config.endpoint;
    }

    this.client = new S3Client(clientConfig);
  }

  async upload(key: string, data: Buffer | Uint8Array | string, contentType: string, options?: UploadOptions): Promise<UploadResult> {
    try {
      const body = typeof data === 'string' ? Buffer.from(data) : data;

      const command = new PutObjectCommand({
        Bucket: this.bucket,
        Key: key,
        Body: body,
        ContentType: contentType,
        ContentEncoding: options?.contentEncoding,
        CacheControl: options?.cacheControl,
        Metadata: options?.metadata,
      });

      const response = await this.client.send(command);

      const metadata: ObjectMetadata = {
        key,
        sizeBytes: body.length,
        contentType,
      };

      if (response.ETag) {
        metadata.etag = response.ETag;
      }

      return {
        key,
        url: undefined,
        metadata,
      };
    } catch (error) {
      throw this.handleError(error, key, 'upload');
    }
  }

  async download(key: string): Promise<Buffer> {
    try {
      const command = new GetObjectCommand({
        Bucket: this.bucket,
        Key: key,
      });

      const response = await this.client.send(command);

      if (!response.Body) {
        throw new StorageException('Empty response body', 'EMPTY_BODY', 400, key);
      }

      // Convert stream to buffer
      const chunks: Uint8Array[] = [];
      const stream = response.Body as Readable;

      for await (const chunk of stream) {
        chunks.push(chunk);
      }

      return Buffer.concat(chunks);
    } catch (error) {
      throw this.handleError(error, key, 'download');
    }
  }

  async getMetadata(key: string): Promise<ObjectMetadata> {
    try {
      const command = new HeadObjectCommand({
        Bucket: this.bucket,
        Key: key,
      });

      const response = await this.client.send(command);

      const metadata: ObjectMetadata = {
        key,
        sizeBytes: response.ContentLength || 0,
        contentType: response.ContentType || 'application/octet-stream',
      };

      if (response.LastModified) {
        metadata.lastModified = response.LastModified;
      }
      if (response.ETag) {
        metadata.etag = response.ETag;
      }

      return metadata;
    } catch (error) {
      throw this.handleError(error, key, 'getMetadata');
    }
  }

  async delete(key: string): Promise<void> {
    try {
      const command = new DeleteObjectCommand({
        Bucket: this.bucket,
        Key: key,
      });

      await this.client.send(command);
    } catch (error) {
      throw this.handleError(error, key, 'delete');
    }
  }

  async exists(key: string): Promise<boolean> {
    try {
      await this.getMetadata(key);
      return true;
    } catch (error) {
      if (error instanceof StorageException && error.statusCode === 404) {
        return false;
      }
      throw error;
    }
  }

  async getPresignedUrl(key: string, expiresIn: number = 3600): Promise<string> {
    try {
      const command = new GetObjectCommand({
        Bucket: this.bucket,
        Key: key,
      });

      return await getSignedUrl(this.client, command, { expiresIn });
    } catch (error) {
      throw this.handleError(error, key, 'getPresignedUrl');
    }
  }

  async list(prefix?: string, maxKeys: number = 1000): Promise<Partial<ObjectMetadata>[]> {
    try {
      const command = new ListObjectsV2Command({
        Bucket: this.bucket,
        Prefix: prefix,
        MaxKeys: maxKeys,
      });

      const response = await this.client.send(command);

      const objects: ObjectMetadata[] = [];

      for (const obj of response.Contents || []) {
        if (obj.Key) {
          const metadata: ObjectMetadata = {
            key: obj.Key,
            sizeBytes: obj.Size || 0,
            contentType: 'application/octet-stream', // ListObjectsV2 doesn't return ContentType
          };

          if (obj.LastModified) {
            metadata.lastModified = obj.LastModified;
          }
          if (obj.ETag) {
            metadata.etag = obj.ETag;
          }

          objects.push(metadata);
        }
      }

      return objects;
    } catch (error) {
      throw this.handleError(error, prefix, 'list');
    }
  }

  private handleError(error: unknown, key: string | undefined, operation: string): StorageException {
    if (error instanceof Error) {
      const statusCode = (error as any).$metadata?.httpStatusCode;
      const code = (error as any).Code || (error as any).name;

      return new StorageException(
        `S3 ${operation} failed: ${error.message}`,
        code,
        statusCode,
        key
      );
    }

    return new StorageException(
      `S3 ${operation} failed: Unknown error`,
      'UNKNOWN',
      500,
      key
    );
  }
}

/**
 * Create S3 provider from environment variables
 * Follows Neon Object Storage environment variable naming convention
 */
export function createS3ProviderFromEnv(): S3Provider {
  const endpoint = process.env.AWS_ENDPOINT_URL_S3;
  const region = process.env.AWS_REGION;
  const accessKeyId = process.env.AWS_ACCESS_KEY_ID;
  const secretAccessKey = process.env.AWS_SECRET_ACCESS_KEY;
  const bucket = process.env.AWS_BUCKET;

  if (!endpoint || !region || !accessKeyId || !secretAccessKey || !bucket) {
    throw new Error(
      'Missing required S3 environment variables. ' +
      'Required: AWS_ENDPOINT_URL_S3, AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_BUCKET'
    );
  }

  return new S3Provider({
    endpoint,
    region,
    accessKeyId,
    secretAccessKey,
    bucket,
    forcePathStyle: true, // Required for Neon Object Storage
  });
}
