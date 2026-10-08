export type AppRole = "student" | "teacher" | "admin";

export type AuthUser = {
  id: string;
  email?: string;
  fullName?: string;
  roles: AppRole[];
};

export type TokenPair = {
  accessToken: string;
  refreshToken?: string | null;
};

export type LoginInput = {
  email: string;
  password: string;
};

export type RegisterInput = {
  email: string;
  password: string;
  full_name?: string;
};
