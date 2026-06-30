"use client";

import { Component, type ErrorInfo, type ReactNode } from "react";

type StrategyLabErrorBoundaryProps = {
  children: ReactNode;
};

type StrategyLabErrorBoundaryState = {
  error: Error | null;
};

/** Catches render errors in Strategy Lab so tour entry fails gracefully. */
export class StrategyLabErrorBoundary extends Component<
  StrategyLabErrorBoundaryProps,
  StrategyLabErrorBoundaryState
> {
  state: StrategyLabErrorBoundaryState = { error: null };

  static getDerivedStateFromError(error: Error): StrategyLabErrorBoundaryState {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error("Strategy Lab render error", error, info.componentStack);
  }

  render() {
    if (this.state.error) {
      return (
        <div className="route-loading-panel" role="alert">
          <div className="route-loading-card">
            <h1 className="route-loading-title">Strategy Lab hit a snag</h1>
            <p className="route-loading-subtitle">
              Something went wrong while loading the lab. Try refreshing, or start the tour again from
              the homepage.
            </p>
            <p className="footer-note" style={{ marginTop: 16 }}>
              <a className="btn slim primary" href="/strategy-lab?tutorial=1&amp;asset=BTC">
                Restart guided tour
              </a>
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
