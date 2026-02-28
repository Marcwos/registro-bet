import { httpClient } from "@/shared/lib/http-client";
import type {
  ChangePasswordRequest,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  SendVerificationRequest,
  VerifyEmailRequest,
  RecoverPasswordRequest,
  ResetPasswordRequest,
} from "../types";

/**
 * Funciones que llaman a los endpoints de autenticacion del backend.
 * Cada funcion retorna la data de la respuesta directamente (sin el wrapper de Axios).
 */

export async function loginUser(data: LoginRequest): Promise<LoginResponse> {
  const response = await httpClient.post<LoginResponse>(
    "/users/login/",
    data,
  );
  return response.data;
}

export async function registerUser(
  data: RegisterRequest,
): Promise<RegisterResponse> {
  const response = await httpClient.post<RegisterResponse>(
    "/users/register/",
    data,
  );
  return response.data;
}

export async function sendVerificationEmail(
  data: SendVerificationRequest,
): Promise<{ message: string }> {
  const response = await httpClient.post<{ message: string }>(
    "/users/send-verification/",
    data,
  );
  return response.data;
}

export async function verifyEmail(
  data: VerifyEmailRequest,
): Promise<{ message: string }> {
  const response = await httpClient.post<{ message: string }>(
    "/users/verify-email/",
    data,
  );
  return response.data;
}

export async function recoverPassword(
  data: RecoverPasswordRequest,
): Promise<{ message: string }> {
  const response = await httpClient.post<{ message: string }>(
    "/users/recover-password/",
    data,
  );
  return response.data;
}

export async function resetPassword(
  data: ResetPasswordRequest,
): Promise<{ message: string }> {
  const response = await httpClient.post<{ message: string }>(
    "/users/reset-password/",
    data,
  );
  return response.data;
}

export async function logoutUser(refreshToken: string): Promise<void> {
  await httpClient.post("/users/logout/", { refresh_token: refreshToken });
}

export async function changePassword(
  data: ChangePasswordRequest,
): Promise<{ message: string }> {
  const response = await httpClient.post<{ message: string }>(
    "/users/change-password/",
    data,
  );
  return response.data;
}
