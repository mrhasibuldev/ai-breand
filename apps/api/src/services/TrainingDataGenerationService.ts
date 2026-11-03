/**
 * Training Data Generation Service
 *
 * Converts approved datasets into training-ready format.
 * Ensures only approved and training-eligible datasets are used.
 */

import { readDatabaseConfig, createDatabaseClient } from '@nexusai/database-core';
import { createS3ProviderFromEnv, DatasetStorageService } from '@nexusai/storage-core';
import crypto from 'node:crypto';

interface TrainingDataGenerationOptions {
  dataset_id: string;
  dataset_version: string;
  account_id: string;
  train_split?: number; // Default 0.8
  max_len?: number; // Default 256
  shuffle?: boolean; // Default true
}

interface TrainingDataResult {
  training_data_key: string;
  validation_data_key: string;
  training_size: number;
  validation_size: number;
  total_size: number;
  checksum: string;
  tokenizer_config: any;
  preprocessing_config: any;
}

export class TrainingDataGenerationService {
  private db: any;
  private storageService: DatasetStorageService;

  constructor() {
    const config = readDatabaseConfig();
    this.db = createDatabaseClient(config);
    this.db.connect();

    const s3Provider = createS3ProviderFromEnv();
    this.storageService = new DatasetStorageService(s3Provider);
  }

  /**
   * Generate training data from an approved dataset
   */
  async generateTrainingData(options: TrainingDataGenerationOptions): Promise<TrainingDataResult> {
    const {
      dataset_id,
      dataset_version,
      account_id,
      train_split = 0.8,
      max_len = 256,
      shuffle = true
    } = options;

    try {
      // Verify dataset is approved and training-eligible
      const datasetResult = await this.db.query(
        `SELECT id, dataset_name, storage_key, approval_status, training_eligible, sha256_checksum
         FROM nexus.dataset_registry
         WHERE id = $1 AND account_id = $2 AND deleted_at IS NULL`,
        [dataset_id, account_id]
      );

      if (datasetResult.rows.length === 0) {
        throw new Error('Dataset not found');
      }

      const dataset = datasetResult.rows[0];

      if (dataset.approval_status !== 'approved') {
        throw new Error(`Dataset is not approved. Current status: ${dataset.approval_status}`);
      }

      if (!dataset.training_eligible) {
        throw new Error('Dataset is not training-eligible');
      }

      // Download dataset from storage
      const buffer = await this.storageService.downloadDataset(
        account_id,
        dataset.dataset_name,
        dataset_version,
        'jsonl'
      );

      const datasetContent = buffer.toString('utf-8');
      const lines = datasetContent.split('\n').filter(line => line.trim() !== '');

      // Parse JSONL
      const documents = lines.map(line => {
        try {
          return JSON.parse(line);
        } catch (e) {
          console.error('[Training Data Generation] Failed to parse line:', line);
          return null;
        }
      }).filter(doc => doc !== null);

      if (documents.length === 0) {
        throw new Error('No valid documents in dataset');
      }

      // Shuffle if requested
      if (shuffle) {
        this.shuffleArray(documents);
      }

      // Split into train/validation
      const splitIndex = Math.floor(documents.length * train_split);
      const trainDocs = documents.slice(0, splitIndex);
      const valDocs = documents.slice(splitIndex);

      // Extract text content
      const trainTexts = trainDocs.map(doc => doc.text || doc.content || '');
      const valTexts = valDocs.map(doc => doc.text || doc.content || '');

      // Prepare training configuration
      const tokenizerConfig = {
        type: 'SimpleTokenizer',
        max_len
      };

      const preprocessingConfig = {
        train_split,
        shuffle,
        document_count: documents.length,
        train_count: trainDocs.length,
        validation_count: valDocs.length,
        max_len
      };

      // Prepare training data format (JSON)
      const trainingData = {
        texts: trainTexts,
        config: preprocessingConfig,
        metadata: {
          dataset_id,
          dataset_version,
          checksum: dataset.sha256_checksum,
          created_at: new Date().toISOString()
        }
      };

      const validationData = {
        texts: valTexts,
        config: preprocessingConfig,
        metadata: {
          dataset_id,
          dataset_version,
          checksum: dataset.sha256_checksum,
          created_at: new Date().toISOString()
        }
      };

      // Convert to buffers
      const trainingBuffer = Buffer.from(JSON.stringify(trainingData, null, 2), 'utf-8');
      const validationBuffer = Buffer.from(JSON.stringify(validationData, null, 2), 'utf-8');

      // Calculate combined checksum
      const hash = crypto.createHash('sha256');
      hash.update(trainingBuffer);
      hash.update(validationBuffer);
      const checksum = hash.digest('hex');

      // Upload training data
      const trainingKey = `training/${dataset_id}_${dataset_version}_train.json`;
      const validationKey = `training/${dataset_id}_${dataset_version}_val.json`;

      await this.storageService.uploadDataset(trainingBuffer, 'application/json', {
        userId: account_id,
        datasetId: dataset_id,
        version: dataset_version,
        fileFormat: 'json',
        metadata: {
          name: `${dataset.dataset_name}_train`,
          datasetType: 'training',
          language: 'mixed',
          domain: 'general',
          taskType: 'training'
        }
      });

      await this.storageService.uploadDataset(validationBuffer, 'application/json', {
        userId: account_id,
        datasetId: dataset_id,
        version: dataset_version,
        fileFormat: 'json',
        metadata: {
          name: `${dataset.dataset_name}_val`,
          datasetType: 'validation',
          language: 'mixed',
          domain: 'general',
          taskType: 'validation'
        }
      });

      return {
        training_data_key: trainingKey,
        validation_data_key: validationKey,
        training_size: trainingBuffer.length,
        validation_size: validationBuffer.length,
        total_size: trainingBuffer.length + validationBuffer.length,
        checksum,
        tokenizer_config: tokenizerConfig,
        preprocessing_config: preprocessingConfig
      };
    } catch (error) {
      console.error('[Training Data Generation] Failed to generate training data:', error);
      throw error;
    }
  }

  /**
   * Fisher-Yates shuffle
   */
  private shuffleArray<T>(array: T[]): void {
    for (let i = array.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      const temp = array[i]!;
      array[i] = array[j]!;
      array[j] = temp;
    }
  }

  /**
   * Get training-eligible datasets
   */
  async getTrainingEligibleDatasets(account_id: string): Promise<any[]> {
    try {
      const result = await this.db.query(
        `SELECT id, dataset_name, version, storage_key, sha256_checksum,
                training_eligible, approval_status, created_at
         FROM nexus.dataset_registry
         WHERE account_id = $1
           AND training_eligible = true
           AND approval_status = 'approved'
           AND deleted_at IS NULL
         ORDER BY created_at DESC`,
        [account_id]
      );

      return result.rows;
    } catch (error) {
      console.error('[Training Data Generation] Failed to get training-eligible datasets:', error);
      throw error;
    }
  }
}
