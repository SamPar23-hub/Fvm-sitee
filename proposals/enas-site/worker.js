// Enas Latif proposal, served at shotbyfvm.com/enas (any capitalisation).
// This Worker only owns the /enas paths on the main domain; the files live in ./public.
export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const m = url.pathname.match(/^\/enas(\/.*)?$/i);
    if (!m) return Response.redirect("https://shotbyfvm.com/", 302);
    // Keep one address so the page's files resolve: /enas, /Enas and /ENAS/ all go to /enas/
    if (!m[1] || !url.pathname.startsWith("/enas/")) return Response.redirect("https://shotbyfvm.com/enas/" + (m[1] || "/").slice(1), 302);
    const res = await env.ASSETS.fetch(new Request(new URL(m[1], url.origin), req));
    const out = new Response(res.body, res);
    out.headers.set("x-robots-tag", "noindex, nofollow");
    return out;
  }
};
