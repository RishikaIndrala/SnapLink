# SnapLink — URL Shortener

A URL shortener built with FastAPI, Postgres, and Redis, and deployed
live on Render.

**Live app:** https://snaplink-pijm.onrender.com
**API docs:** https://snaplink-pijm.onrender.com/docs

---

## What it does

- Turn a long URL into a short one (`POST /shorten`)
- Visit the short one, get sent to the original (`GET /{short_code}`)
- Check how many times a link has been clicked (`GET /stats/{short_code}`)

## How it's built

![SnapLink architecture](architecture.svg)

1. A request comes into the FastAPI app (running on Render)
2. For a redirect, it checks Redis first — if the link is already cached, it answers immediately
3. If it's not cached, it looks it up in Postgres instead, then saves it in Redis so the next visit is faster
4. Either way, it counts the click and updates the database

Postgres is the permanent record. Redis is just a fast, temporary copy
of the most recently used links.

## Stack

| Part | What I used | Why |
|---|---|---|
| API | FastAPI | Simple to write, gives free interactive docs |
| Database | Postgres (Neon) | Free hosted Postgres, no server to manage |
| Cache | Redis (Upstash) | Free hosted Redis, same idea |
| Hosting | Render | Connects to GitHub, deploys on push |

## Building this in stages

I built this in small pieces instead of all at once, and measured
things as I went instead of assuming:

1. **Get it working** — shorten a link, follow it, nothing fancy
2. **Put it online** — deploy it so it's a real, working link
3. **Speed it up** — add caching, and check if it actually helped
4. **Add extras** — click counts

That order mattered. If I'd added caching from the start, I'd have
nothing to compare it to.

## What I found when I measured it

Before caching, a redirect took about **470ms**. After adding Redis
caching, a cached redirect took about **380ms** — roughly a **20%**
improvement.

I expected caching to help a lot more than that, so I looked into why
it didn't. It turned out most of the delay wasn't the database query
itself — it was just the distance data has to travel. My app, my
database, and my cache are all hosted in different places, so even a
"cached" answer still has to travel a similar distance, just to a
different server.

So the honest takeaway is: caching worked correctly, but I'd need to
host the app, database, and cache closer together to see the bigger
improvement it's normally capable of. That's the first thing on my
list to try next.

## Some choices worth explaining

- **Short codes are random**, not counted up one by one (like `1, 2, 3...`).
  That way nobody can guess how many links exist, or look through them
  in order.
- **Click counts update directly in the database**, using one atomic
  step (`click_count = click_count + 1`) so two people clicking at the
  same time can't overwrite each other's count.
- **Cached links expire after an hour.** If I ever add editing or
  deleting links, this keeps the cache from serving something outdated
  for too long.

## Running it yourself

```bash
git clone https://github.com/YOUR_USERNAME/SnapLink.git
cd SnapLink

python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

Create a `.env` file:
```env
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
REDIS_URL=rediss://default:password@host:6379
```

Then run:
```bash
uvicorn app.app:app --reload
```

Open `http://127.0.0.1:8000/docs` to try it.

## What I'd add next

- Host the app, database, and cache in the same region, and re-measure
- Make short-code creation avoid an extra database check on every write
- Run a proper load test to see how much traffic it can actually handle
- Custom short codes, chosen by the user
- Ability to delete or update a link
