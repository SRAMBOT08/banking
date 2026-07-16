import axios from 'axios';
export const api = axios.create({ baseURL: process.env.NEXT_PUBLIC_GATEWAY_URL ?? 'http://localhost:8000', timeout: 12000 });
export const gateway = {
  investigations: async () => {
    const response = (await api.get('/api/v1/investigations')).data;
    return Array.isArray(response) ? response : (response?.investigations ?? []);
  },
  investigation: async (id: string) => (await api.get(`/api/v1/investigations/${id}/context`)).data,
  runScenario: async (scenario: string) => (await api.post('/api/v1/simulations/run', { scenario })).data,
  timeline: async (id: string) => (await api.get(`/api/v1/investigations/${id}/timeline`)).data,
  memory: async (id: string) => (await api.get(`/api/v1/investigations/${id}/memory`)).data,
  graph: async (id: string) => (await api.get(`/api/v1/graph/investigation/${id}`)).data,
  executionStatus: async () => (await api.get('/api/v1/executions/status')).data,
  simulation: async (id: string) => (await api.get(`/api/v1/simulations/${id}`)).data,
  simulationEvents: async (id: string) => (await api.get(`/api/v1/simulations/${id}/events`)).data,
  health: async () => (await api.get('/api/v1/platform/health')).data,
};

export async function gatewayFirst<T>(request: () => Promise<T>, fallback: T): Promise<T> {
  try { return await request(); } catch { return fallback; }
}
