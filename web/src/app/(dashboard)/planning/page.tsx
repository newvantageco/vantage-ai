"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Suggestion = { key: string; when: string };

export default function PlanningPage() {
	const [channel, setChannel] = useState("linkedin");
	const [orgId, setOrgId] = useState("");
	const [items, setItems] = useState<Suggestion[]>([]);

	useEffect(() => {
		if (!orgId) return;
		api
			.get("/content/plan/timeslots", { params: { org_id: orgId, channel, n: 5 } })
			.then((r) => setItems(r.data.suggestions))
			.catch((e) => console.error(e));
	}, [orgId, channel]);

	return (
		<div className="p-6">
			<h1 className="text-2xl font-semibold mb-4">Best next timeslots</h1>
			<div className="mb-4 flex gap-2">
				<input
					className="border px-2 py-1 rounded"
					placeholder="Org ID"
					value={orgId}
					onChange={(e) => setOrgId(e.target.value)}
				/>
				<select
					className="border px-2 py-1 rounded"
					value={channel}
					onChange={(e) => setChannel(e.target.value)}
				>
					<option value="linkedin">LinkedIn</option>
					<option value="meta">Meta</option>
				</select>
			</div>
			<ul className="space-y-2">
				{items.map((s, i) => (
					<li key={i} className="border rounded p-3 flex justify-between">
						<span className="font-mono">{s.key}</span>
						<span>{s.when ? new Date(s.when).toLocaleString() : "derived"}</span>
					</li>
				))}
			</ul>
		</div>
	);
}


