import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '10s', target: 5 },     // normal traffic
    { duration: '5s', target: 50 },     // sudden spike
    { duration: '30s', target: 50 },    // sustain spike
    { duration: '10s', target: 5 },     // recovery
  ],
  thresholds: {
    http_req_duration: ['p(95)<800'],
    http_req_failed: ['rate<0.05'],
  },
};

const BASE_URL = __ENV.BASE_URL;

export default function () {
  const res = http.get(`${BASE_URL}/health`);
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}