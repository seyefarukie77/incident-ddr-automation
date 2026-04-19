import { test, expect } from '@playwright/test';

test('Complete DDR workflow executes successfully', async ({ request }) => {
  const res = await request.post('/ddr/assess', {
    data: {
      incidentId: "INC13089493"
    }
  });

  const body = await res.json();
  expect(res.status()).toBe(200);
  expect(body.overallStatus).toBe("PASS");
});