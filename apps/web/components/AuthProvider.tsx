'use client';

import React from 'react';
import type { AuthUser } from '@/lib/api';
import { clearAuth, loadAuth, saveAuth } from '@/lib/authStorage';

interface AuthContextValue {
  user: AuthUser | null;
  setUser: (u: AuthUser | null) => void;
  logout: () => void;
}

const AuthContext = React.createContext<AuthContextValue>({
  user: null,
  setUser: () => undefined,
  logout: () => undefined,
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUserState] = React.useState<AuthUser | null>(null);

  React.useEffect(() => {
    setUserState(loadAuth());
  }, []);

  const setUser = React.useCallback((u: AuthUser | null) => {
    setUserState(u);
    if (u) saveAuth(u);
    else clearAuth();
  }, []);

  const logout = React.useCallback(() => {
    setUserState(null);
    clearAuth();
  }, []);

  return <AuthContext.Provider value={{ user, setUser, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  return React.useContext(AuthContext);
}
