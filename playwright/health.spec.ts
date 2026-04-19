import { test, expect } from '@playwright/test';

test('Health endpoint returns OK', { tag: '@smoke' }, async ({ request }) => {
  const response = await request.get('/health');
  expect(response.status()).toBe(200);
});


test.describe('Critical journey regression', { tag: '@regression' }, () => {
  test('DDR API health remains available', async ({ request }) => {
    const res = await request.get('/health');
    expect(res.status()).toBe(200);
  });
});
