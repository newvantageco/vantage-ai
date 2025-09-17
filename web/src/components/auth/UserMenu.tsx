"use client";
import { useDevAuth } from "../DevAuthWrapper";

export default function UserMenu() {
  const devAuth = useDevAuth();

  return (
    <div className="flex items-center gap-2">
      {devAuth.isSignedIn ? (
        <div className="flex items-center gap-2">
          <img 
            src={devAuth.user?.imageUrl} 
            alt={devAuth.user?.firstName}
            className="w-8 h-8 rounded-full"
          />
          <span className="text-sm font-medium">
            {devAuth.user?.firstName} {devAuth.user?.lastName}
          </span>
          <button
            onClick={devAuth.signOut}
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