import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['tests/**/*.test.ts', 'packages/**/*.test.ts', 'apps/**/*.test.ts'],
    env: {
      // Test-only cookie signing secret — never a real credential.
      COOKIE_SECRET: 'vitest-test-only-cookie-secret',
    },
  },
});
