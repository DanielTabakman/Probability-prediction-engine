import { AppSidebar } from "@/components/AppSidebar";

type AppShellProps = {
  children: React.ReactNode;
  activeNavId?: string;
};

export function AppShell({ children, activeNavId }: AppShellProps) {
  return (
    <div className="app-shell">
      <AppSidebar activeNavId={activeNavId} />
      <div className="app-main">{children}</div>
    </div>
  );
}
