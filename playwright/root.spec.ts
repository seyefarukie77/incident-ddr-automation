import { test, expect } from '@playwright/test';

test('GET / returns 404 for undefined root path', async ({ request }) => {
  const response = await request.get('/');

  expect(response.status()).toBe(404);

  const body = await response.json();
  expect(body.detail).toBe('Not Found');
});
