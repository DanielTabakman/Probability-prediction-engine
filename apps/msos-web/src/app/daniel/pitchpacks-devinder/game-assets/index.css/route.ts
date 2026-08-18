const UPSTREAM_CSS =
  "https://raw.githubusercontent.com/devenderbutani21/PitchPacks/gh-pages/assets/index-D03Axhh7.css";

export async function GET() {
  const upstream = await fetch(UPSTREAM_CSS, {
    next: { revalidate: 86400 },
  });

  if (!upstream.ok || !upstream.body) {
    return new Response("PitchPacks stylesheet is unavailable.", {
      status: 502,
      headers: { "content-type": "text/plain; charset=utf-8" },
    });
  }

  return new Response(upstream.body, {
    headers: {
      "content-type": "text/css; charset=utf-8",
      "cache-control": "public, max-age=3600, s-maxage=86400",
    },
  });
}
