import { test, expect } from '@playwright/test';

test('Health endpoint returns OK', { tag: '@smoke' }, async ({ request }) => {
  const response = await request.get('/health');
  expect(response.status()).toBe(200);
});
