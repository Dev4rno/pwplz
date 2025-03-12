!(function () {
    var a,
        o = window.location,
        r = window.document,
        t = r.currentScript,
        l = t.getAttribute("data-api") || new URL(t.src).origin + "/api/event",
        c = t.getAttribute("data-domain");
    function s(t, e, n) {
        e && console.warn("Ignoring Event: " + e), n && n.callback && n.callback(), "pageview" === t && (a = !0);
    }
    var d,
        u,
        w = o.href,
        p = {},
        h = -1,
        f = !1,
        e = !1;
    function n() {
        var t = r.body || {},
            e = r.documentElement || {};
        return Math.max(
            t.scrollHeight || 0,
            t.offsetHeight || 0,
            t.clientHeight || 0,
            e.scrollHeight || 0,
            e.offsetHeight || 0,
            e.clientHeight || 0
        );
    }
    function i() {
        var t = r.body || {},
            e = r.documentElement || {},
            n = window.innerHeight || e.clientHeight || 0,
            e = window.scrollY || e.scrollTop || t.scrollTop || 0;
        return v <= n ? v : e + n;
    }
    var v = n(),
        g = i();
    function b() {
        var t = d ? u + (Date.now() - d) : u;
        e ||
            a ||
            !(h < g || 3e3 <= t) ||
            ((h = g),
            setTimeout(function () {
                e = !1;
            }, 300),
            (t = { n: "engagement", sd: Math.round((g / v) * 100), d: c, u: w, p: p, e: t }),
            (d = null),
            (u = 0),
            y(l, t));
    }
    function m(t, e) {
        var n = "pageview" === t;
        if (/^localhost$|^127(\.[0-9]+){0,2}\.[0-9]+$|^\[::1?\]$/.test(o.hostname) || "file:" === o.protocol)
            return s(t, "localhost", e);
        if (
            (window._phantom || window.__nightmare || window.navigator.webdriver || window.Cypress) &&
            !window.__plausible
        )
            return s(t, null, e);
        try {
            if ("true" === window.localStorage.plausible_ignore) return s(t, "localStorage flag", e);
        } catch (t) {}
        var i = {};
        (i.n = t),
            (i.u = o.href),
            (i.d = c),
            (i.r = r.referrer || null),
            e && e.meta && (i.m = JSON.stringify(e.meta)),
            e && e.props && (i.p = e.props),
            n &&
                ((a = !1),
                (w = i.u),
                (p = i.p),
                (h = -1),
                (u = 0),
                (d = Date.now()),
                f ||
                    (r.addEventListener("visibilitychange", function () {
                        "hidden" === r.visibilityState ? ((u += Date.now() - d), (d = null), b()) : (d = Date.now());
                    }),
                    (f = !0))),
            y(l, i, e);
    }
    function y(t, e, n) {
        window.fetch &&
            fetch(t, {
                method: "POST",
                headers: { "Content-Type": "text/plain" },
                keepalive: !0,
                body: JSON.stringify(e),
            }).then(function (t) {
                n && n.callback && n.callback({ status: t.status });
            });
    }
    window.addEventListener("load", function () {
        v = n();
        var t = 0,
            e = setInterval(function () {
                (v = n()), 15 == ++t && clearInterval(e);
            }, 200);
    }),
        r.addEventListener("scroll", function () {
            v = n();
            var t = i();
            g < t && (g = t);
        });
    var S = (window.plausible && window.plausible.q) || [];
    window.plausible = m;
    for (var E, H = 0; H < S.length; H++) m.apply(this, S[H]);
    function L(t) {
        (t && E === o.pathname) || (t && f && (b(), (v = n()), (g = i())), (E = o.pathname), m("pageview"));
    }
    function _() {
        L(!0);
    }
    var k,
        t = window.history;
    t.pushState &&
        ((k = t.pushState),
        (t.pushState = function () {
            k.apply(this, arguments), _();
        }),
        window.addEventListener("popstate", _)),
        "prerender" === r.visibilityState
            ? r.addEventListener("visibilitychange", function () {
                  E || "visible" !== r.visibilityState || L();
              })
            : L(),
        window.addEventListener("pageshow", function (t) {
            t.persisted && L();
        });
})();
