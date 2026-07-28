const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

type PollOptions<T> = {
  interval?: number;
  timeout?: number;
  onSuccess?: (data: T) => void;
  onError?: (error: unknown) => void;
};

export async function pollJob<T>(
  fn: () => Promise<T>,
  validate: (data: T) => boolean,
  options: PollOptions<T> = {}
): Promise<T> {
  const {
    interval = 3000,
    timeout = 1000 * 60 * 10,
    onSuccess,
    onError
  } = options;

  const start = Date.now();

  while (true) {
    try {
      const data = await fn();

      if (validate(data)) {
        onSuccess?.(data);
        return data; // Termina la función con éxito
      }

      // Validar si ya nos pasamos del tiempo límite global
      if (Date.now() - start > timeout) {
        throw new Error("Polling timeout");
      }

      // 👈 2. CLAVE: Esperamos obligatoriamente los 3 segundos ANTES de la próxima iteración
      await delay(interval);

    } catch (error) {
      onError?.(error);
      throw error; // Lanza el error para que lo cachee el llamador
    }
  }
}