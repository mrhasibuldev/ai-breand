/**
 * Storage Integration Test
 *
 * Test script to verify Neon Object Storage integration.
 * Run with: pnpm exec tsx src/test-storage.ts
 */

import 'dotenv/config';
import { createS3ProviderFromEnv, DatasetStorageService } from './index.js';

async function testStorageIntegration() {
  console.log('Starting Neon Object Storage integration test...\n');

  try {
    // Initialize S3 provider
    console.log('1. Initializing S3 provider...');
    const s3Provider = createS3ProviderFromEnv();
    console.log('   ✓ S3 provider initialized\n');

    // Initialize storage service
    console.log('2. Initializing storage service...');
    const storageService = new DatasetStorageService(s3Provider);
    console.log('   ✓ Storage service initialized\n');

    // Test upload
    console.log('3. Testing upload...');
    const testData = Buffer.from('Hello from NexusAI Storage Test!');
    const testKey = `nexusai-test-${Date.now()}.txt`;
    const uploadResult = await s3Provider.upload(testKey, testData, 'text/plain');
    console.log('   ✓ Upload successful');
    console.log(`   Key: ${uploadResult.key}`);
    console.log(`   Size: ${uploadResult.metadata.sizeBytes} bytes\n`);

    // Test metadata
    console.log('4. Testing metadata retrieval...');
    const metadata = await s3Provider.getMetadata(testKey);
    console.log('   ✓ Metadata retrieved');
    console.log(`   Key: ${metadata.key}`);
    console.log(`   Size: ${metadata.sizeBytes} bytes`);
    console.log(`   Content-Type: ${metadata.contentType}\n`);

    // Test download
    console.log('5. Testing download...');
    const downloadedData = await s3Provider.download(testKey);
    console.log('   ✓ Download successful');
    console.log(`   Downloaded size: ${downloadedData.length} bytes`);
    console.log(`   Content: ${downloadedData.toString()}\n`);

    // Verify content
    console.log('6. Verifying content integrity...');
    if (downloadedData.toString() === testData.toString()) {
      console.log('   ✓ Content integrity verified\n');
    } else {
      throw new Error('Content mismatch!');
    }

    // Test presigned URL
    console.log('7. Testing presigned URL generation...');
    if (s3Provider.getPresignedUrl) {
      const presignedUrl = await s3Provider.getPresignedUrl(testKey, 3600);
      console.log('   ✓ Presigned URL generated');
      console.log(`   URL: ${presignedUrl.substring(0, 50)}...\n`);
    } else {
      console.log('   ⚠ Presigned URL not supported\n');
    }

    // Test delete
    console.log('8. Testing deletion...');
    await s3Provider.delete(testKey);
    console.log('   ✓ Object deleted\n');

    // Verify deletion
    console.log('9. Verifying deletion...');
    const exists = await s3Provider.exists(testKey);
    if (!exists) {
      console.log('   ✓ Deletion verified\n');
    } else {
      throw new Error('Object still exists after deletion!');
    }

    console.log('✅ All tests passed successfully!\n');
    return true;
  } catch (error) {
    console.error('❌ Test failed:', error);
    console.error('\nError details:');
    if (error instanceof Error) {
      console.error(`Message: ${error.message}`);
      console.error(`Stack: ${error.stack}`);
    }
    return false;
  }
}

// Run tests
testStorageIntegration()
  .then((success) => {
    process.exit(success ? 0 : 1);
  })
  .catch((error) => {
    console.error('Unexpected error:', error);
    process.exit(1);
  });
