import Link from "next/link";

import {
  railDisplayLabel,
  trustBadgeTone,
  type ExposurePathRecord,
} from "@/lib/ppeExposureMenu";
import { useDisplayCurrency } from "@/lib/useDisplayCurrency";

type ExposurePathCardProps = {
  path: ExposurePathRecord;
};

export function ExposurePathCard({ path }: ExposurePathCardProps) {
  const { formatMoney } = useDisplayCurrency();
  const trustTone = trustBadgeTone(path.trust_badge);
  const showCost = typeof path.cost_hint_usd === "number" && Number.isFinite(path.cost_hint_usd);

  return (
    <article className="exposure-path-card panel" aria-labelledby={`exposure-path-${path.path_id}`}>
      <header className="exposure-path-card-head">
        <div>
          <h2 id={`exposure-path-${path.path_id}`}>{path.label}</h2>
          <p className="panel-sub">{path.headline}</p>
        </div>
        <div className="exposure-path-badges">
          <span className="tag muted">{railDisplayLabel(path.instrument_rail)}</span>
          <span className={`tag ${trustTone}`.trim()}>{path.trust_badge}</span>
        </div>
      </header>

      <p className="exposure-path-capital">{path.capital_shape}</p>

      {showCost ? (
        <p className="exposure-path-cost">
          Illustrative cost: <strong>{formatMoney(path.cost_hint_usd!)}</strong>
        </p>
      ) : null}

      <div className="exposure-path-lists">
        <div>
          <span className="micro">Pros</span>
          <ul>
            {path.pros.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div>
          <span className="micro">Cons</span>
          <ul>
            {path.cons.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>

      {path.deep_link ? (
        <Link href={path.deep_link} className="btn slim">
          Open in Strategy Lab
        </Link>
      ) : null}
    </article>
  );
}
