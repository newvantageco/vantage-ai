"use client";
import { useEffect, useState } from "react";

type Campaign = {
  id: string;
  org_id: string;
  name: string;
  objective?: string | null;
  start_date?: string | null;
  end_date?: string | null;
};

export default function CampaignsPage() {
  const [orgId, setOrgId] = useState("");
  const [name, setName] = useState("");
  const [objective, setObjective] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [list, setList] = useState<Campaign[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [nameWarn, setNameWarn] = useState<string | null>(null);
  const [objWarn, setObjWarn] = useState<string | null>(null);

  async function load() {
    setErr(null);
    if (!orgId) return;
    try {
      const resp = await fetch(`/api/campaigns?org_id=${encodeURIComponent(orgId)}`);
      const data = await resp.json();
      if (!resp.ok) throw new Error(data?.detail || "Failed");
      setList(data);
    } catch (e: any) {
      setErr(e.message || String(e));
    }
  }

  async function validateText(value: string, guideId?: string) {
    try {
      const resp = await fetch(`/api/content/validate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ caption: value, brand_guide_id: guideId || orgId }),
      });
      const data = await resp.json();
      return data as { ok: boolean; reasons: string[]; fixed_text: string };
    } catch {
      return { ok: true, reasons: [], fixed_text: value };
    }
  }

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    try {
      const resp = await fetch(`/api/campaigns`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ org_id: orgId, name, objective, start_date: startDate, end_date: endDate }),
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data?.detail || "Failed");
      setName("");
      setObjective("");
      setStartDate("");
      setEndDate("");
      await load();
    } catch (e: any) {
      setErr(e.message || String(e));
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [orgId]);

  return (
    <div>
      <h1>Campaigns</h1>
      <div>
        <label>Org ID</label>
        <input value={orgId} onChange={(e) => setOrgId(e.target.value)} />
      </div>
      <form onSubmit={onCreate}>
        <div>
          <label>Name</label>
          <input lang="en-GB" spellCheck={true} value={name} onChange={(e) => setName(e.target.value)} onBlur={async () => {
            const res = await validateText(name);
            setNameWarn(res.ok ? null : res.reasons.join(", "));
          }} />
          {nameWarn && <small>{nameWarn}</small>}
        </div>
        <div>
          <label>Objective</label>
          <input lang="en-GB" spellCheck={true} value={objective} onChange={(e) => setObjective(e.target.value)} onBlur={async () => {
            const res = await validateText(objective);
            setObjWarn(res.ok ? null : res.reasons.join(", "));
          }} />
          {objWarn && <small>{objWarn}</small>}
        </div>
        <div>
          <label>Start date</label>
          <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
        </div>
        <div>
          <label>End date</label>
          <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
        </div>
        <button type="submit">Create</button>
      </form>
      {err && <p>{err}</p>}
      <ul>
        {list.map((c) => (
          <li key={c.id}>{c.name} — {c.objective || ""}</li>
        ))}
      </ul>
    </div>
  );
}


