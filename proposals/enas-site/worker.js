// Enas Latif proposal. Static files in ./public are served first on enas.shotbyfvm.com.
// Anything else lands here: shotbyfvm.com/enas (any capitalisation) forwards to the subdomain.
export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (url.hostname !== "enas.shotbyfvm.com") return Response.redirect("https://enas.shotbyfvm.com/", 302);
    return env.ASSETS.fetch(new Request("https://enas.shotbyfvm.com/", req));
  }
};
