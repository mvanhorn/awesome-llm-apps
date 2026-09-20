# The outage was a for loop

At 2:47am on March 11th our payments API started returning 502s for every merchant in Europe — 4,100 of them, all at once. I know the exact minute because PagerDuty screenshots are forever, and because I spent the next four hours learning something embarrassing about code I had personally reviewed.

The culprit was a retry loop I approved in October. Three lines. It retried failed webhook deliveries — sensible, standard, boring. Except the author had put the retry inside the database transaction, and I had looked straight at it and thought "clean."

Here is what actually happened that night. A merchant in Rotterdam had a webhook endpoint that started timing out. Each timeout held its transaction open for 30 seconds while the loop retried. Postgres has a default of 100 connections. You can do the math faster than our dashboard did — it took 11 minutes to eat the entire pool. Every other request in Europe queued behind a Dutch furniture store's broken endpoint.

I keep thinking about why I missed it in review. The code was tidy. The tests passed — all 34 of them, because every test mocked the database, so no test could ever hold a real connection open. Our test suite was structurally incapable of catching our worst outage of the year. That sentence still bothers me.

We fixed it in three moves: move the retry outside the transaction, add a 5-second statement timeout, and cap webhook retries at 2 before punting to a queue. The fix diff was 19 lines. The incident doc was 9 pages.

What I actually took from it: review the shape of the failure, not the shape of the code. Tidy, tested, and approved — and it still took down a continent. Now when I review anything with a loop and an external call, I ask one question first: what does this hold while it waits? It has caught two more of these since. Cheap question. I plan to keep asking it.
