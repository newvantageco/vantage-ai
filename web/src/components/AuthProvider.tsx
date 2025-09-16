"use client";

import * as React from "react";
import { DevAuthWrapper } from "./DevAuthWrapper";

export default function AuthProvider({
  children,
  publishableKey,
}: {
  children: React.ReactNode;
  publishableKey?: string;
}) {
  // Always use dev auth for now
  return <DevAuthWrapper>{children}</DevAuthWrapper>;
}