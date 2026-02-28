import axios from "axios";

/**
 * Extrae un mensaje de error legible de una respuesta de Axios.
 * El backend de Django DRF puede enviar errores en varios formatos:
 * - { detail: "mensaje" }
 * - { email: ["error1"], password: ["error2"] }
 * - { non_field_errors: ["error"] }
 */
export function getApiErrorMessage(error: unknown): string {
  if (!axios.isAxiosError(error) || !error.response?.data) {
    return "Ocurrio un error inesperado. Intenta de nuevo.";
  }

  const data = error.response.data;

  // Formato: { detail: "mensaje" }
  if (typeof data.detail === "string") {
    return data.detail;
  }

  // Formato: { message: "mensaje" }
  if (typeof data.message === "string") {
    return data.message;
  }

  // Formato: { campo: ["error1", "error2"] } — toma el primer error del primer campo
  if (typeof data === "object") {
    const firstKey = Object.keys(data)[0];
    if (firstKey && Array.isArray(data[firstKey])) {
      return data[firstKey][0];
    }
    if (firstKey && typeof data[firstKey] === "string") {
      return data[firstKey];
    }
  }

  return "Ocurrio un error inesperado. Intenta de nuevo.";
}
