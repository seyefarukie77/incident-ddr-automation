import { test, expect } from '@playwright/test';

test(
  'Undefined root path returns 404',
  { tag: '@negative' },
  async ({ request }) => {
    const response = await request.get('/');
    expect(response.status()).toBe(404);

    const body = await response.json();
    expect(body.detail).toBe('Not Found');
  }
);

test.describe('Negative & edge‑case tests', { tag: '@negative' }, () => {
  test('Invalid route returns 404', async ({ request }) => {
    const response = await request.get('/invalid');
    expect(response.status()).toBe(404);
  });
});