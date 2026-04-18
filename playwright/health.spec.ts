import { test, expect } from '@playwright/test';

test('Health endpoint returns OK', async ({ request }) => {
  const response = await request.get('/health');
  expect(response.status()).toBe(200);

  const body = await response.json();
  expect(body.status).toBe('ok');
});