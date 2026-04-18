import { test, expect } from '@playwright/test';

test('GET / returns 404 when root is not defined', async ({ request }) => {
  const response = await request.get('/');
  expect(response.status()).toBe(404);
});