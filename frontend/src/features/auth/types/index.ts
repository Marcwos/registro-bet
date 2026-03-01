/** Tipos de datos para el modulo de autenticacion */

export interface User {
  id: string;
  email: string;
  role: string;
}

export interface LoginRequest {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user_id: string;
  email: string;
  role: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface RegisterResponse {
  id: string;
  email: string;
  role: string;
  is_email_verified: boolean;
  created_at: string;
}

export interface VerifyEmailRequest {
  user_id: string;
  code: string;
}

export interface SendVerificationRequest {
  user_id: string;
}

export interface RecoverPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  email: string;
  code: string;
  new_password: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}
