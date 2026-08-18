const UPSTREAM_JS =
  "https://raw.githubusercontent.com/devenderbutani21/PitchPacks/gh-pages/assets/index-W4KOU7cP.js";

export async function GET() {
  const upstream = await fetch(UPSTREAM_JS, {
    next: { revalidate: 86400 },
  });

  if (!upstream.ok || !upstream.body) {
    return new Response("PitchPacks JavaScript bundle is unavailable.", {
      status: 502,
      headers: { "content-type": "text/plain; charset=utf-8" },
    });
  }

  return new Response(upstream.body, {
    headers: {
      "content-type": "text/javascript; charset=utf-8",
      "cache-control": "public, max-age=3600, s-maxage=86400",
    },
  });
}
