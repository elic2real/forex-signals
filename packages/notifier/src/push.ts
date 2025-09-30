type AlertPayload = {
  title: string;
  body: string;
  data?: Record<string, any>;
};

export function formatAlertPayload(signal: any): AlertPayload {
  return {
    title: `Signal: ${signal.bias}`,
    body: `Score: ${signal.score}`,
    data: signal
  };
}
