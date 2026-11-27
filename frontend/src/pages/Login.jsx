import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Truck, ArrowRight } from "lucide-react";

export default function Login() {
  const [mode, setMode] = useState("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { login, signup } = useAuth();
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (mode === "login") await login(email, password);
      else await signup(name, email, password);
      navigate("/");
    } catch (err) {
      const detail = err?.response?.data?.detail;
      if (!err?.response) {
        setError("Can't reach the server. Make sure the backend is running on http://localhost:8000.");
      } else if (typeof detail === "string") {
        setError(detail);
      } else if (Array.isArray(detail)) {
        setError(detail.map((d) => d.msg).join(", "));
      } else {
        setError(`Server error (${err.response.status}). Check the backend terminal for details.`);
      }
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-ink px-4">
      <div className="w-full max-w-md">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-9 h-9 rounded-lg bg-sage/10 border border-sage/30 flex items-center justify-center">
            <Truck className="w-5 h-5 text-sage" strokeWidth={1.75} />
          </div>
          <span className="font-display font-semibold text-lg tracking-tight">Supply Chain Agent</span>
        </div>
        <div className="route-dash w-full mb-8" />

        <div className="bg-panel border border-line rounded-2xl shadow-soft p-8">
          <h1 className="font-display text-2xl font-semibold mb-1">
            {mode === "login" ? "Welcome back" : "Create your account"}
          </h1>
          <p className="text-mist text-sm mb-6">
            {mode === "login"
              ? "Sign in to pick up where your fleet left off."
              : "Set up an account to start tracking disruptions."}
          </p>

          <form onSubmit={submit} className="space-y-4">
            {mode === "signup" && (
              <div>
                <label className="text-xs uppercase tracking-wide text-mist">Name</label>
                <input
                  className="mt-1 w-full bg-panel2 border border-line rounded-lg px-3 py-2.5 text-cloud focus:border-sage outline-none"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>
            )}
            <div>
              <label className="text-xs uppercase tracking-wide text-mist">Email</label>
              <input
                type="email"
                className="mt-1 w-full bg-panel2 border border-line rounded-lg px-3 py-2.5 text-cloud focus:border-sage outline-none"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div>
              <label className="text-xs uppercase tracking-wide text-mist">Password</label>
              <input
                type="password"
                className="mt-1 w-full bg-panel2 border border-line rounded-lg px-3 py-2.5 text-cloud focus:border-sage outline-none"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
              />
            </div>

            {error && (
              <div className="text-clay text-sm bg-clay/10 border border-clay/30 rounded-lg px-3 py-2">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={busy}
              className="w-full flex items-center justify-center gap-2 bg-sand text-ink font-semibold rounded-lg py-2.5 hover:brightness-110 transition disabled:opacity-50"
            >
              {busy ? "Please wait…" : mode === "login" ? "Sign in" : "Create account"}
              {!busy && <ArrowRight className="w-4 h-4" />}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-mist">
            {mode === "login" ? (
              <>
                New here?{" "}
                <button className="text-sand hover:underline" onClick={() => setMode("signup")}>
                  Create an account
                </button>
              </>
            ) : (
              <>
                Already have an account?{" "}
                <button className="text-sand hover:underline" onClick={() => setMode("login")}>
                  Sign in
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
