"use client";
import { useState } from "react";

export default function BrandGuidePage() {
  const [orgId, setOrgId] = useState("");
  const [voice, setVoice] = useState("");
  const [audience, setAudience] = useState("");
  const [pillars, setPillars] = useState("");
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setResult(null);
    try {
      const resp = await fetch("/api/brand-guide", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ org_id: orgId, voice, audience, pillars }),
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data?.detail || "Failed");
      setResult(JSON.stringify(data));
    } catch (err: any) {
      setError(err.message || String(err));
    }
  }

  return (
    <div>
      <h1>Brand Guide</h1>
      <form onSubmit={onSubmit}>
        <div>
          <label>Org ID</label>
          <input value={orgId} onChange={(e) => setOrgId(e.target.value)} />
        </div>
        <div>
          <label>Voice</label>
          <textarea lang="en-GB" spellCheck={true} value={voice} onChange={(e) => setVoice(e.target.value)} />
        </div>
        <div>
          <label>Audience</label>
          <textarea lang="en-GB" spellCheck={true} value={audience} onChange={(e) => setAudience(e.target.value)} />
        </div>
        <div>
          <label>Pillars</label>
          <textarea lang="en-GB" spellCheck={true} value={pillars} onChange={(e) => setPillars(e.target.value)} />
        </div>
        <button type="submit">Save</button>
      </form>
      {result && <pre>{result}</pre>}
      {error && <p>{error}</p>}
    </div>
  );
}


