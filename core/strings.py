import random

rate_limit_warnings = [
    "Whoa there, speedster! Take a break and try again in a bit.",
    "You've reached the top of the speedometer. Slow down and refresh later!",
    "Easy, tiger! You're clicking faster than we can handle.",
    "You’ve exceeded the maximum fun-per-minute quota. Please pause for awesomeness to catch up.",
    "Server: ‘I'm only human... Wait, I’m not even human. But still, slow down!’",
    "Relax, Neo. You’ve overloaded the Matrix. Try again later.",
    "Even The Flash needs a breather. Cool your jets, superhero!",
    "Simmer down, Padawan. The Force needs a moment to recharge.",
    "It’s not Hogwarts Express; you need to wait for the next train.",
    "You’ve been Rickrolled by the rate limiter. Never gonna give you up, but you must wait.",
    "Your bandwidth exceeded our chill limit. Retry soon.",
    "HTTP 429: Too Many Requests. Redis is crying in a corner right now.",
    "You've spammed us into a timeout. API rage quit in 3... 2... 1...",
    "Buffer overflow: your clicks are ahead of our clock cycles.",
    "You’ve DOS-ed yourself! Take five and retry.",
    "Oops, you've hit the request ceiling. Grab a snack and come back!",
    "Hold on, we’re giving your browser a coffee break.",
    "Breathe in, breathe out. And… refresh after a moment.",
    "Too many requests, not enough cookies. Wait a bit and we’ll bake some for you!",
    "You’ve won the ‘Most Enthusiastic Clicker’ award! Your prize: a short timeout.",
]

def get_random_rate_limit_warning(warnings = rate_limit_warnings):
    return random.choice(warnings)

def is_valid_warning(warning: str) -> bool:
    if not warning:
        raise ValueError("Invalid warning string")
    return warning in rate_limit_warnings