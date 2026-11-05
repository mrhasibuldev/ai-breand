/**
 * Image Optimization Utility
 *
 * Client-side image optimization using Canvas API
 * Resizes and compresses images before upload to reduce file size
 * while maintaining visual quality
 */

export interface OptimizationResult {
  optimizedFile: File;
  originalSize: number;
  optimizedSize: number;
  compressionRatio: number;
  originalDimensions: { width: number; height: number };
  optimizedDimensions: { width: number; height: number };
  processingTime: number;
}

export interface OptimizationOptions {
  maxWidth?: number;
  maxHeight?: number;
  quality?: number;
  outputFormat?: 'image/jpeg' | 'image/png' | 'image/webp';
  targetSizeKB?: number;
}

const DEFAULT_OPTIONS: OptimizationOptions = {
  maxWidth: 1600,
  maxHeight: 1600,
  quality: 0.85,
  outputFormat: 'image/webp',
  targetSizeKB: 500,
};

/**
 * Optimize an image file using Canvas API
 */
export async function optimizeImage(
  file: File,
  options: OptimizationOptions = {}
): Promise<OptimizationResult> {
  const startTime = performance.now();
  const opts = { ...DEFAULT_OPTIONS, ...options };

  console.log('[ImageOptimizer] Starting optimization:', {
    originalSize: file.size,
    originalType: file.type,
    options: opts,
  });

  // Skip optimization for very small files
  if (file.size < 100 * 1024) {
    console.log('[ImageOptimizer] File too small, skipping optimization');
    return {
      optimizedFile: file,
      originalSize: file.size,
      optimizedSize: file.size,
      compressionRatio: 1,
      originalDimensions: { width: 0, height: 0 },
      optimizedDimensions: { width: 0, height: 0 },
      processingTime: performance.now() - startTime,
    };
  }

  try {
    // Load image
    const bitmap = await createImageBitmap(file);
    const originalWidth = bitmap.width;
    const originalHeight = bitmap.height;

    console.log('[ImageOptimizer] Original dimensions:', { width: originalWidth, height: originalHeight });

    // Calculate new dimensions (maintain aspect ratio)
    let newWidth = originalWidth;
    let newHeight = originalHeight;

    if (originalWidth > opts.maxWidth! || originalHeight > opts.maxHeight!) {
      const widthRatio = opts.maxWidth! / originalWidth;
      const heightRatio = opts.maxHeight! / originalHeight;
      const ratio = Math.min(widthRatio, heightRatio);

      newWidth = Math.round(originalWidth * ratio);
      newHeight = Math.round(originalHeight * ratio);
    }

    console.log('[ImageOptimizer] Optimized dimensions:', { width: newWidth, height: newHeight });

    // Create canvas and draw image
    const canvas = document.createElement('canvas');
    canvas.width = newWidth;
    canvas.height = newHeight;
    const ctx = canvas.getContext('2d');

    if (!ctx) {
      throw new Error('Failed to get canvas context');
    }

    // Draw image with high quality
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(bitmap, 0, 0, newWidth, newHeight);

    // Convert to blob with compression
    const blob = await new Promise<Blob>((resolve, reject) => {
      canvas.toBlob(
        (blob) => {
          if (blob) {
            resolve(blob);
          } else {
            reject(new Error('Failed to create blob'));
          }
        },
        opts.outputFormat ?? 'image/webp',
        opts.quality ?? 0.85
      );
    });

    // Adaptive compression: if still too large, reduce quality
    let finalBlob = blob;
    let finalQuality = opts.quality ?? 0.85;
    let iterations = 0;
    const maxIterations = 5;

    while (finalBlob.size > (opts.targetSizeKB ?? 500) * 1024 && iterations < maxIterations && finalQuality > 0.5) {
      iterations++;
      finalQuality -= 0.05;

      console.log(`[ImageOptimizer] Adaptive compression iteration ${iterations}, quality: ${finalQuality}`);

      finalBlob = await new Promise<Blob>((resolve, reject) => {
        canvas.toBlob(
          (blob) => {
            if (blob) {
              resolve(blob);
            } else {
              reject(new Error('Failed to create blob'));
            }
          },
          opts.outputFormat ?? 'image/webp',
          finalQuality
        );
      });
    }

    // Create File object
    const outputFormat = opts.outputFormat ?? 'image/webp';
    const extension = outputFormat === 'image/jpeg' ? 'jpg' : outputFormat.split('/')[1];
    const optimizedFile = new File([finalBlob], `optimized.${extension}`, {
      type: outputFormat,
    });

    const processingTime = performance.now() - startTime;
    const compressionRatio = file.size / optimizedFile.size;

    console.log('[ImageOptimizer] Optimization complete:', {
      originalSize: file.size,
      optimizedSize: optimizedFile.size,
      compressionRatio,
      processingTime,
    });

    // Fallback: if optimized is larger than original, use original
    if (optimizedFile.size >= file.size) {
      console.log('[ImageOptimizer] Optimized size >= original, using original');
      return {
        optimizedFile: file,
        originalSize: file.size,
        optimizedSize: file.size,
        compressionRatio: 1,
        originalDimensions: { width: originalWidth, height: originalHeight },
        optimizedDimensions: { width: originalWidth, height: originalHeight },
        processingTime,
      };
    }

    return {
      optimizedFile,
      originalSize: file.size,
      optimizedSize: optimizedFile.size,
      compressionRatio,
      originalDimensions: { width: originalWidth, height: originalHeight },
      optimizedDimensions: { width: newWidth, height: newHeight },
      processingTime,
    };
  } catch (error) {
    console.error('[ImageOptimizer] Optimization failed:', error);
    // Fallback to original file
    return {
      optimizedFile: file,
      originalSize: file.size,
      optimizedSize: file.size,
      compressionRatio: 1,
      originalDimensions: { width: 0, height: 0 },
      optimizedDimensions: { width: 0, height: 0 },
      processingTime: performance.now() - startTime,
    };
  }
}

/**
 * Check if browser supports image optimization
 */
export function supportsImageOptimization(): boolean {
  return typeof createImageBitmap !== 'undefined' && typeof document !== 'undefined';
}
