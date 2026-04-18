import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './playwright',
  use: {
    baseURL: process.env.BASE_URL,
  },
  reporter: [['html', { open: 'never' }]],
});