type NavigationProgressBarProps = {
  active: boolean;
  progress: number;
};

export function NavigationProgressBar({ active, progress }: NavigationProgressBarProps) {
  if (!active) {
    return null;
  }

  return (
    <div className="nav-progress-bar" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={progress}>
      <div className="nav-progress-bar__fill" style={{ width: `${progress}%` }} />
    </div>
  );
}
