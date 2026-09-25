import { Component, type ErrorInfo, type ReactNode } from "react";

import { Alert, Button, Card } from "../components/ui";

export class ErrorBoundary extends Component<
  { children: ReactNode },
  { failed: boolean }
> {
  state = { failed: false };

  static getDerivedStateFromError() {
    return { failed: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("MundaSense interface error", error, info.componentStack);
  }

  render() {
    if (!this.state.failed) return this.props.children;
    return (
      <main className="grid min-h-screen place-items-center bg-pale p-5">
        <Card className="max-w-xl p-6">
          <Alert tone="critical" title="This page could not be displayed">
            Your saved records have not been changed. Refresh the local
            interface or return home.
          </Alert>
          <Button className="mt-5" onClick={() => window.location.assign("/")}>
            Return home
          </Button>
        </Card>
      </main>
    );
  }
}
