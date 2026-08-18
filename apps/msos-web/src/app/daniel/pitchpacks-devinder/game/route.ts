const UPSTREAM_INDEX =
  "https://raw.githubusercontent.com/devenderbutani21/PitchPacks/gh-pages/index.html";

export async function GET() {
  const upstream = await fetch(UPSTREAM_INDEX, {
    next: { revalidate: 3600 },
  });

  if (!upstream.ok) {
    return new Response("PitchPacks upstream build is unavailable.", {
      status: 502,
      headers: { "content-type": "text/plain; charset=utf-8" },
    });
  }

  let html = await upstream.text();
  html = html
    .replace(
      "/PitchPacks/assets/index-W4KOU7cP.js",
      "/daniel/pitchpacks-devinder/game-assets/index.js",
    )
    .replace(
      "/PitchPacks/assets/index-D03Axhh7.css",
      "/daniel/pitchpacks-devinder/game-assets/index.css",
    );

  return new Response(html, {
    headers: {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "public, max-age=300, s-maxage=3600",
    },
  });
}
