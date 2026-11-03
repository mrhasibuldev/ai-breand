/**
 * HTTP Source Adapter
 * Safe HTTP fetching for authorized sources with SSRF protection
 */

import { SourceAdapter, SourceConfig, CollectionOptions, CollectionResult, CollectionItem } from './SourceAdapter.js';
import { URL } from 'url';
import { createHash } from 'crypto';

// Private IP ranges to block (SSRF protection)
const PRIVATE_IP_RANGES = [
  '127.0.0.0/8',      // Loopback
  '10.0.0.0/8',       // Private Class A
  '172.16.0.0/12',    // Private Class B
  '192.168.0.0/16',   // Private Class C
  '169.254.0.0/16',   // Link-local
  '::1/128',          // IPv6 loopback
  'fc00::/7',         // IPv6 private
  'fe80::/10',        // IPv6 link-local
];

// Cloud metadata endpoints to block
const BLOCKED_METADATA_ENDPOINTS = [
  '169.254.169.254',  // AWS
  'metadata.google.internal',  // GCP
  'metadata.azure.microsoft.com',  // Azure
];

interface RobotsTxtRule {
  userAgent: string;
  allow: string[];
  disallow: string[];
  crawlDelay?: number;
}

export class HttpSourceAdapter implements SourceAdapter {
  private robotsCache = new Map<string, RobotsTxtRule>();
  private rateLimitStore = new Map<string, number[]>();

  async validate(config: SourceConfig): Promise<{ valid: boolean; errors: string[] }> {
    const errors: string[] = [];

    if (!config.sourceUrl) {
      errors.push('sourceUrl is required for HTTP adapter');
    }

    try {
      if (!config.sourceUrl) {
        errors.push('sourceUrl is required');
        return { valid: false, errors };
      }

      const url = new URL(config.sourceUrl);
      
      // Check protocol
      if (url.protocol !== 'http:' && url.protocol !== 'https:') {
        errors.push('Only http and https protocols are allowed');
      }

      // Check for blocked endpoints
      if (BLOCKED_METADATA_ENDPOINTS.some(endpoint => url.hostname === endpoint)) {
        errors.push('Cloud metadata endpoints are blocked');
      }

      // Check for private IPs
      if (this.isPrivateIP(url.hostname)) {
        errors.push('Private IP addresses are not allowed');
      }

    } catch (error) {
      errors.push(`Invalid URL: ${error}`);
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  async collect(config: SourceConfig, options: CollectionOptions): Promise<CollectionResult> {
    const startTime = Date.now();
    const items: CollectionItem[] = [];
    const errors: string[] = [];
    let itemsCollected = 0;
    let itemsFailed = 0;
    let itemsSkipped = 0;
    let bytesDownloaded = 0;

    if (!config.sourceUrl) {
      return {
        sourceId: config.sourceId,
        status: 'failed',
        itemsCollected: 0,
        itemsFailed: 0,
        itemsSkipped: 0,
        bytesDownloaded: 0,
        durationMs: 0,
        items: [],
        errors: ['sourceUrl is required']
      };
    }

    try {
      // Check robots.txt if enabled
      if (this.supportsRobotsTxt() && config.collectionMethod === 'crawl') {
        const robotsAllowed = await this.checkRobotsTxt(config.sourceUrl);
        if (!robotsAllowed) {
          return {
            sourceId: config.sourceId,
            status: 'failed',
            itemsCollected: 0,
            itemsFailed: 0,
            itemsSkipped: 0,
            bytesDownloaded: 0,
            durationMs: Date.now() - startTime,
            items: [],
            errors: ['robots.txt disallows crawling']
          };
        }
      }

      // Check rate limits
      if (!this.checkRateLimit(config.sourceUrl)) {
        return {
          sourceId: config.sourceId,
          status: 'failed',
          itemsCollected: 0,
          itemsFailed: 0,
          itemsSkipped: 0,
          bytesDownloaded: 0,
          durationMs: Date.now() - startTime,
          items: [],
          errors: ['Rate limit exceeded']
        };
      }

      // Fetch the URL
      const response = await this.fetchWithRetry(config.sourceUrl, options);

      if (!response.ok) {
        itemsFailed++;
        errors.push(`HTTP ${response.status}: ${response.statusText}`);
      } else {
        const content = await response.text();
        const sizeBytes = Buffer.byteLength(content, 'utf8');

        // Check size limit
        if (options.maxDocumentSize && sizeBytes > options.maxDocumentSize) {
          itemsSkipped++;
          errors.push(`Document size (${sizeBytes} bytes) exceeds limit (${options.maxDocumentSize} bytes)`);
        } else {
          // Calculate checksum
          const checksum = createHash('sha256').update(content).digest('hex');

          const item: CollectionItem = {
            sourceId: config.sourceId,
            originalUrl: config.sourceUrl,
            finalUrl: response.url,
            title: this.extractTitle(config.sourceUrl),
            contentType: response.headers.get('content-type') || 'text/plain',
            collectionTimestamp: new Date(),
            httpStatus: response.status,
            checksum,
            sizeBytes,
            ...(options.dryRun !== true ? { content } : {})
          };

          items.push(item);
          itemsCollected++;
          bytesDownloaded += sizeBytes;
        }
      }

    } catch (error) {
      itemsFailed++;
      errors.push(String(error));
    }

    return {
      sourceId: config.sourceId,
      status: errors.length > 0 ? 'partial' : 'success',
      itemsCollected,
      itemsFailed,
      itemsSkipped,
      bytesDownloaded,
      durationMs: Date.now() - startTime,
      items,
      errors
    };
  }

  supportsRobotsTxt(): boolean {
    return true;
  }

  getRateLimits() {
    return {
      requestsPerWindow: 100,
      windowSeconds: 60,
      concurrentRequests: 5
    };
  }

  private async fetchWithRetry(url: string, options: CollectionOptions): Promise<Response> {
    const maxRetries = options.maxRetries || 3;
    const timeout = options.timeout || 30000; // 30 seconds default

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        const response = await fetch(url, {
          headers: {
            'User-Agent': 'NexusAI-KnowledgeCollector/1.0 (https://nexusai.com)',
            'Accept': 'text/html,application/xhtml+xml,application/xml,text/plain'
          },
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (response.ok || response.status >= 400 && response.status < 500) {
          return response;
        }

        // Retry on 5xx errors
        if (response.status >= 500 && attempt < maxRetries) {
          const delay = Math.pow(2, attempt) * 1000; // Exponential backoff
          await new Promise(resolve => setTimeout(resolve, delay));
          continue;
        }

        return response;

      } catch (error) {
        if (attempt === maxRetries) {
          throw error;
        }

        const delay = Math.pow(2, attempt) * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }

    throw new Error('Max retries exceeded');
  }

  private async checkRobotsTxt(url: string): Promise<boolean> {
    try {
      const urlObj = new URL(url);
      const robotsUrl = `${urlObj.protocol}//${urlObj.host}/robots.txt`;

      const response = await fetch(robotsUrl, {
        headers: { 'User-Agent': 'NexusAI-KnowledgeCollector/1.0' }
      });

      if (!response.ok) {
        // If robots.txt is unavailable, allow crawling conservatively
        return true;
      }

      const content = await response.text();
      const lines = content.split('\n');
      let userAgentMatch = false;
      let disallowCount = 0;

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith('#')) continue;

        if (trimmed.toLowerCase().startsWith('user-agent:')) {
          const ua = trimmed.substring(11).trim().toLowerCase();
          if (ua === '*' || ua.includes('nexusai')) {
            userAgentMatch = true;
          }
        }

        if (userAgentMatch && trimmed.toLowerCase().startsWith('disallow:')) {
          const path = trimmed.substring(9).trim();
          if (path === '/' || path === '') {
            return false; // Entire site disallowed
          }
          disallowCount++;
        }
      }

      return true;

    } catch (error) {
      // If robots.txt check fails, allow crawling conservatively
      return true;
    }
  }

  private checkRateLimit(url: string): boolean {
    const now = Date.now();
    const windowMs = 60000; // 1 minute window
    const limits = this.getRateLimits();

    const key = new URL(url).hostname;
    const timestamps = this.rateLimitStore.get(key) || [];

    // Remove timestamps outside the window
    const recent = timestamps.filter(t => now - t < windowMs);

    if (recent.length >= limits.requestsPerWindow) {
      return false;
    }

    recent.push(now);
    this.rateLimitStore.set(key, recent);
    return true;
  }

  private isPrivateIP(hostname: string): boolean {
    // Basic check for common private patterns
    if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '::1') {
      return true;
    }

    if (hostname.startsWith('192.168.') || hostname.startsWith('10.') || hostname.startsWith('172.')) {
      return true;
    }

    return false;
  }

  private extractTitle(url: string): string {
    try {
      const urlObj = new URL(url);
      const pathParts = urlObj.pathname.split('/').filter(p => p);
      if (pathParts.length > 0) {
        const lastPart = pathParts[pathParts.length - 1];
        if (lastPart) {
          return lastPart.replace(/-/g, ' ').replace(/_/g, ' ').replace(/\.[^/.]+$/, '');
        }
      }
      return urlObj.hostname;
    } catch {
      return url;
    }
  }
}
