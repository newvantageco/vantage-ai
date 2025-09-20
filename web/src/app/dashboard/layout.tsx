import { LatticeDashboardLayout } from "@/components/layout/LatticeDashboardLayout";
import { ProtectedRoute } from "@/components/ProtectedRoute";

export default function DashboardRootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Always require authentication in production
  
  return (
    <ProtectedRoute>
      <LatticeDashboardLayout>{children}</LatticeDashboardLayout>
    </ProtectedRoute>
  );
}
