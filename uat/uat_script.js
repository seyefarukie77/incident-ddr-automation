test('UAT – PIR incomplete blocks DDR PASS', async ({ request }) => {
  const res = await request.post('/ddr/assess', {
    data: { incidentId: "INC_UAT_001" }
  });

  const body = await res.json();
  expect(body.overallStatus).toBe("FAIL");
});
