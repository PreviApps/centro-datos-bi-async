import { createContext, useContext, useState } from "react";

interface UserSession {
  id: string;
  name: string;
  corporate_email: string;
  collaborator_position_name: string;
}

interface AuthContextType {
  user: UserSession;
  setUser: (user: UserSession) => void;
}

// Credenciales simuladas de usuario logueado para desarrollo/pruebas
const MOCK_LOGGED_USER: UserSession = {
  id: "f4d48315-f61c-41b0-a6f3-82898e73d7f2", 
  name: "SERGIO DAVID",
  corporate_email: "sergio.lema@previsalud.com.co",
  collaborator_position_name: "DESARROLLADOR JUNIOR",
};

const AuthContext = createContext<AuthContextType>({
  user: MOCK_LOGGED_USER,
  setUser: () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserSession>(MOCK_LOGGED_USER);

  return (
    <AuthContext.Provider value={{ user, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}