type TradeProsConsCardProps = {
  strengths: string[];
  risks: string[];
};

export function TradeProsConsCard({ strengths, risks }: TradeProsConsCardProps) {
  if (!strengths.length && !risks.length) {
    return null;
  }

  return (
    <div className="trade-pros-cons" aria-label="Trade strengths and risks">
      {strengths.length ? (
        <div className="trade-pros-cons-block">
          <h3>Strengths — works if…</h3>
          <ul>
            {strengths.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        </div>
      ) : null}
      {risks.length ? (
        <div className="trade-pros-cons-block risks">
          <h3>Risks — hurts if…</h3>
          <ul>
            {risks.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        </div>
      ) : null}
      <p className="micro trade-pros-cons-foot">
        Illustrative paper plan only — not financial advice.
      </p>
    </div>
  );
}
