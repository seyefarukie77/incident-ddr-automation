import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '30s', target: 30 },
    { duration: '30s', target: 60 },
    { duration: '30s', target: 100 },   // push system
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<1500'],
    http_req_failed: ['rate<0.10'],
  },
};

const BASE_URL = __ENV.BASE_URL;

export default function () {
  const res = http.get(`${BASE_URL}/health`);
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}