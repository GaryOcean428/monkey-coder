
import { test, expect } from '@jest/globals';

// This is a mock of the endpoint that was causing 422 errors.
// In a real-world scenario, you would replace this with an actual call
// to your staging or test environment.
const mockEndpoint = async (payload: any) => {
  if (!payload.model || !payload.messages) {
    return { status: 422, body: { error: 'Unprocessable Entity' } };
  }
  return { status: 200, body: { message: 'Success' } };
};

test('should return 200 for a valid payload', async () => {
  const payload = {
    model: 'gpt-4.1',
    messages: [{ role: 'user', content: 'Hello' }],
  };
  const response = await mockEndpoint(payload);
  expect(response.status).toBe(200);
});

test('should not return 422 for a valid payload', async () => {
  const payload = {
    model: 'gpt-4.1',
    messages: [{ role: 'user', content: 'Hello' }],
  };
  const response = await mockEndpoint(payload);
  expect(response.status).not.toBe(422);
});

test('should return 422 for an invalid payload', async () => {
  const payload = {
    messages: [{ role: 'user', content: 'Hello' }],
  };
  const response = await mockEndpoint(payload);
  expect(response.status).toBe(422);
});

