"use client";
import { useAuth } from "@/contexts/AuthContext";

export default function UserMenu() {
  const auth = useAuth();

  return (
    <div className="flex items-center gap-2">
      {auth.isAuthenticated ? (
        <div className="flex items-center gap-2">
          <img 
            src={'/default-avatar.png'} 
            alt={auth.user?.name}
            className="w-8 h-8 rounded-full"
          />
          <span className="text-sm font-medium">
            {auth.user?.name}
          </span>
          <button
            onClick={auth.logout}
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            Sign Out
          </button>
        </div>
      ) : (
        <div className="text-sm text-muted-foreground">Loading...</div>
      )}
    </div>
  );
}