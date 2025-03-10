!(function () {
    "use strict";
    if (
        /^localhost$|^127(\.[0-9]+){0,2}\.[0-9]+$|^\[::1?\]$/.test(window.location.hostname) ||
        "file:" === window.location.protocol ||
        window !== window.parent
    )
        return void console.warn("DataFast: Tracking disabled on localhost, file protocol, or inside iframe");
    const t = document.currentScript,
        n = "data-",
        e = t.getAttribute.bind(t),
        o = !t.src.includes("datafa.st")
            ? new URL("/api/events", window.location.origin).href
            : "https://datafa.st/api/events",
        i = e(n + "website-id"),
        a = e(n + "domain");
    function s(t, n, e) {
        let o = "";
        if (e) {
            const t = new Date();
            t.setTime(t.getTime() + 24 * e * 60 * 60 * 1e3), (o = "; expires=" + t.toUTCString());
        }
        document.cookie = t + "=" + (n || "") + o + "; path=/";
    }
    function r(t) {
        const n = t + "=",
            e = document.cookie.split(";");
        for (let t = 0; t < e.length; t++) {
            let o = e[t];
            for (; " " === o.charAt(0); ) o = o.substring(1, o.length);
            if (0 === o.indexOf(n)) return o.substring(n.length, o.length);
        }
        return null;
    }
    function c() {
        const t = window.location.href;
        if (!t)
            return void console.warn(
                "DataFast: Unable to collect href. This may indicate incorrect script implementation or browser issues."
            );
        const n = {
                websiteId: i,
                domain: a,
                href: t,
                referrer: document.referrer || null,
                viewport: { width: window.innerWidth, height: window.innerHeight },
            },
            e = (function () {
                let t = r("datafast_visitor_id");
                t ||
                    ((t = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (t) {
                        const n = (16 * Math.random()) | 0;
                        return ("x" == t ? n : (3 & n) | 8).toString(16);
                    })),
                    s("datafast_visitor_id", t, 365));
                return t;
            })(),
            o = u();
        return (n.visitorId = e), (n.sessionId = o), n;
    }
    function d(t) {
        const n = c();
        (n.type = "pageview"), f(n, t);
    }
    function l(t, n, e) {
        const o = c();
        (o.type = t), (o.extraData = n), f(o, e);
    }
    function x(t) {
        var n;
        t &&
            t.href &&
            ((n = t.href), window.location.hostname !== new URL(n, window.location.origin).hostname) &&
            l("external_link", { url: t.href, text: t.textContent.trim() });
    }
    function u() {
        let t = r("datafast_session_id");
        return (
            t ||
                ((t = "sxxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (t) {
                    const n = (16 * Math.random()) | 0;
                    return ("x" == t ? n : (3 & n) | 8).toString(16);
                })),
                s("datafast_session_id", t, 1 / 48)),
            t
        );
    }
    function f(t, n) {
        if ("true" === localStorage.getItem("datafast_ignore"))
            return console.log("DataFast: Tracking disabled via localStorage flag"), void (n && n({ status: 200 }));
        !(function (t, n) {
            const e = new XMLHttpRequest();
            e.open("POST", o, !0),
                e.setRequestHeader("Content-Type", "application/json"),
                (e.onreadystatechange = function () {
                    if (e.readyState === XMLHttpRequest.DONE) {
                        if (200 === e.status) {
                            console.log("Event data sent successfully");
                            s("datafast_session_id", u(), 1 / 48);
                        } else console.error("Error sending event data:", e.status);
                        n && n({ status: e.status });
                    }
                }),
                e.send(JSON.stringify(t));
        })(t, n);
    }
    if (
        ((window.datafast = function (t, n) {
            t
                ? !["signup", "payment"].includes(t) || n?.email
                    ? ["signup", "payment"].includes(t)
                        ? l(t, { email: n.email })
                        : l("custom", { eventName: t, ...n })
                    : console.warn(`DataFast: Missing email for ${t} event`)
                : console.warn("DataFast: Missing event_name for custom event");
        }),
        document.addEventListener("click", function (t) {
            x(t.target.closest("a"));
        }),
        document.addEventListener("keydown", function (t) {
            if ("Enter" === t.key || " " === t.key) {
                x(t.target.closest("a"));
            }
        }),
        !i || !a)
    )
        return void console.warn("Missing website ID or domain");
    d();
    let w = window.location.pathname;
    const p = window.history.pushState;
    (window.history.pushState = function () {
        p.apply(this, arguments), w !== window.location.pathname && ((w = window.location.pathname), d());
    }),
        window.addEventListener("popstate", function () {
            w !== window.location.pathname && ((w = window.location.pathname), d());
        });
})();
