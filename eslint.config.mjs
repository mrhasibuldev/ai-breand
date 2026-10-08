import tseslint from 'typescript-eslint';
import nextPlugin from '@next/eslint-plugin-next';

export default [
  ...tseslint.configs.recommended,
  {
    ignores: [
      '**/dist/**',
      '**/node_modules/**',
      '**/.next/**',
      '**/next-env.d.ts',
      'pnpm-lock.yaml',
    ],
  },
  {
    files: ['**/*.{ts,tsx,mts,cts,mjs,cjs}'],
    plugins: { '@next/next': nextPlugin },
    settings: { next: { rootDir: 'apps/web/' } },
    rules: {
      'no-console': 'warn',
      'no-unused-vars': 'off',
      ...nextPlugin.configs.recommended.rules,
    },
  },
  {
    files: ['apps/web/**/*.{js,jsx,ts,tsx}'],
    rules: {
      '@next/next/no-html-link-for-pages': 'off',
    },
  },
];
