import { Component, type ErrorInfo, type ReactNode } from "react";

type ErrorBoundaryProps = {
  children: ReactNode;
};

type ErrorBoundaryState = {
  error: Error | null;
};

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { error: null };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    const crash = {
      message: error.message,
      stack: error.stack,
      componentStack: info.componentStack,
      occurredAt: new Date().toISOString(),
    };
    localStorage.setItem("flife:last-ui-crash", JSON.stringify(crash));
  }

  render() {
    if (this.state.error) {
      return (
        <main className="fatal-screen">
          <div>
            <strong>FLIFE Lite recovered from a UI fault</strong>
            <p>The current session was protected. Restart the app or return to the dashboard after saving your work.</p>
            <button onClick={() => this.setState({ error: null })}>Return to workspace</button>
          </div>
        </main>
      );
    }
    return this.props.children;
  }
}
