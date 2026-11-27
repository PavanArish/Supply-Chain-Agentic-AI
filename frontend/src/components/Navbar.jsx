import { Truck, LogOut } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <div className="border-b border-line bg-ink/80 backdrop-blur sticky top-0 z-20">
      <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-sage/10 border border-sage/30 flex items-center justify-center">
            <Truck className="w-4.5 h-4.5 text-sage" strokeWidth={1.75} />
          </div>
          <span className="font-display font-semibold tracking-tight">Supply Chain Agent</span>
        </div>
        <div className="flex items-center gap-4">
          {user && <span className="text-sm text-mist">{user.name}</span>}
          <button
            onClick={logout}
            className="flex items-center gap-1.5 text-sm text-mist hover:text-cloud transition"
          >
            <LogOut className="w-4 h-4" />
            Sign out
          </button>
        </div>
      </div>
    </div>
  );
}
