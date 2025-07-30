class Prompts:
    def __init__(self, json_result):
        self.json_result = json_result

    def marketing_prompt(self):
        return f"""
I want a concise, professional, highly insightful daily newsletter summarising the top 5 global marketing stories from the past 48 hours, specifically for marketing professionals. Then add a Bonus Round of 5–7 additional stories.

1. Filter by Topic
Identify and retain only the articles that are related to Marketing. This includes news about:

- Advertising campaigns and media buys
- Brand launches, rebrands, or stunts
- Influencer marketing, social media trends
- Big moves from brands or agencies
- Consumer insights and behaviour
- Marketing tools, platforms, or ad tech updates

Skip articles that don't centre around marketing.

2. Handle Paywalled Links
If any article is from a paywalled website (e.g., AdAge, Bloomberg, WSJ), find an equivalent article covering the same story from a non-paywalled source and update the link.
Check that the link works and loads the article.

If it leads to a "Something went wrong" or error page, replace it with another working version of the same topic from a different site.

3. Remove Duplicates
I will provide a list of article titles that have already been used in past newsletters. Remove any article with a matching title from the JSON object.

4. Return Format
Output a new JSON object with only the relevant, non-duplicate marketing-related articles, like this:
(
  "title": "link",
  "title": "link"
)

Here is the JSON object of articles:
{self.json_result}

Here is the list of previously used article titles:
There are no previously used article titles yet, as this is the first newsletter being created.

Please evaluate and rank the articles I've provided based on how compelling, buzzworthy, and attention-grabbing they are from a marketing perspective. I'm looking for the Top 5 most interesting stories—the kind that would spark curiosity, conversation, or shares. Make sure the articles are in English.

If you feel that some of the current articles aren't particularly strong, feel free to search for more interesting marketing-related articles and add them to the pool for consideration. However, please ensure the following:

No paywalls: Only include articles that are freely accessible.

If you find a great article that is behind a paywall, try to locate an alternative non-paywalled version (same title or substantially the same story) and use that version in your evaluation.

Prioritise stories that are:
- Big, eye-catching brand campaigns, launches, or creative stunts
- Surprising moves from major companies (e.g., TikTok, Nike, Amazon, Meta, etc.)
- Major investments, acquisitions, partnerships, or ad spend shifts
- Viral moments, trends, or influencer plays with a wide reach
- New ad tech, creative tools, or experimental formats with real impact
- Bold, weird, or dramatic marketing decisions that spark conversation

Deprioritise or skip:
- Slow-moving policy or legal updates unless they're making headlines
- Think pieces or ethical debates without a clear news hook
- Minor platform changes or tool updates without strategic implications

📰 Deliverables

=== TOP 5 MARKETING STORIES TODAY ===
Rank them from most to least compelling. For each of the Top 5, write a full summary like this:

[Title of Article] – (6 mins)
[Link to article]
What's happening?
Explain the who, what, when, where — include names of brands, campaign specifics, platforms, creative agencies, timing, spend, etc.

Why does it matter?
Frame the big-picture impact: Is this trend-setting? Changing how marketers work? Creating a new standard for engagement?

Key Insight:
What's the strategic punchline or biggest takeaway? Why should marketers pay attention?

=== BONUS ROUND: OTHER MARKETING NEWS WORTH A LOOK ===
These didn't make the Top 5, but are still interesting and valuable. Around 5–7 links is ideal.

[Title] – (5 mins) [Full URL Link]
One-liner summarising the news and why it matters.

[Title] – (4 mins) [Full URL Link]
One-liner summarising the news and why it matters.

[Continue with all remaining secondary stories...]

An example of how the top 5 stories should be presented:

Coca‑Cola leans on marketing to navigate choppy economic waters in Q2 – (2 min)
https://www.marketingdive.com/news/coca-cola-leaned-on-marketing-to-navigate-choppy-economic-waters-in-q2/753702 

What's happening? 
During its Q2 earnings call, Coca‑Cola executives highlighted the relaunch of "Share a Coke" and other global campaigns as key drivers of a 4% volume uptick. The relaunch rolled out across 150 markets with refreshed personalised packaging, integrated social‑first activations, OOH (out‑of‑home) partnerships (e.g., digital billboards in London and Shanghai), and a $50 million global media spend. Early results show a 15% lift in branded search and 20% growth in streaming‑video ad recall.

Why does it matter? 
Coca‑Cola's pivot back to ubiquitous, personalisation-driven branding resets the tone for legacy CPG players facing inflation‑weary consumers and intensifying competition from low‑cost private labels. The success in both emerging and mature markets signals enduring loyalty potential—and offers a playbook for other beverage and FMCG brands to follow.

Key insight: 
Personalisation at scale—blending packaging, digital, and OOH—can reinvigorate heritage brands even amid economic headwinds.

REMEMBER: Clearly separate the TOP 5 STORIES from the BONUS ROUND so they can be properly placed in different sections of the HTML template.
"""


    def AI_prompt(self):
        return f"""
        1. Filter by Topic:
 Identify and retain only the articles that are related to Artificial Intelligence (AI).
2. Handle Paywalled Links:
 If any article is from a paywalled website, for example, Bloomberg, please find an equivalent article covering the same topic from a different, non-paywalled source, and update the link accordingly. Make sure the link leads to the article. Go through each URL and see if it leads to the article. If there is a page “something went wrong” or something along the lines of that, then find another website with the same article title and do the same check.
3. Remove Duplicates:
 I will also provide a list of article titles that have already been covered in previous content. Remove any matching articles from the JSON object.
4. Return Format:
 Output a new JSON object containing only the relevant, unique AI-related articles in the format:
(
  "title": "link",
  "title": "link",
  ...
)

Here is the JSON object of articles:
{self.json_result}

Here is the list of previously used article titles:
None

Next, using the filtered JSON of AI-related news articles generated above, analyse, rank, and summarise the articles based on how interesting and compelling they are — the kind of stories people want to click, talk about, or share. Do not add extra links to sources as you usually do.
🧭 Evaluation Criteria: What Makes a Story “Super Interesting”?
Rank all articles using these criteria — the Top 5 most interesting articles will be selected. If you believe you can find more interesting articles, then please do so and add them to the JSON list to make it easy for you. Ensure all articles are in English and non‑paywalled (or replaced by non‑paywalled equivalents).

Prioritise stories that are:
- Eye-catching product launches, surprising demos, or mind-blowing capabilities
- Unexpected moves from big players (OpenAI, Google, Meta, Apple, etc.)
- Big money: major funding rounds, mergers, or surprise acquisitions
- Breakthroughs or experiments that feel like science fiction are becoming reality
- Weird, bold, or dramatic developments in AI — the ones that make you say “Whoa”
- Anything stirring headlines, trending on social, or causing public buzz

Deprioritise or skip:
- Slow-burning policy developments, unless they sparked major attention
-Generic ethical debates or think pieces
- Low-impact, technical updates with no twist or "hook"

📰 Deliverables
Top AI Stories Today
 Rank based on the prioritisation criteria above — #1 should be the most interesting, clickable, attention-worthy story. Do not add extra links to describe parts of the summary. For each, write a full summary in this format:
[Title of Article] - How long would it take to read the full article Example - (6 mins)
 [Link to article]
 What’s happening? (~60 words)
 Clearly explain the event. Include who, what, when, where, and how — e.g., product names, companies, funding amounts, technical claims, release timelines. No need to click through: the full story is here.
 Why does it matter?(~50 words)
 Connect the event to its global or strategic implications. Is it accelerating AI capability, reshaping an industry, signalling consolidation, or influencing regulation? Ground the importance in real-world stakes.
 Key insight: (~30 words)
 What’s the biggest takeaway? It could be a pattern emerging, a sign of an AI arms race, a new business model shift, or a technical leap. Think of it as the strategic punchline — the "wow" or “watch this space” moment.
✨ Other AI News Worth a Look
 These didn’t make the Top 5, but are still attention-worthy. Around 5–7 links are enough.
 [Title] – (How long would it take to read the full article example - (6 mins))[Link (URL)]
Small explanation of the news (one-line summary of why it matters).
 (Continue this list with all remaining interesting but secondary stories.)
        """
        return self.prompt

    def Fintech_prompt(self):
        return f"""
I want a concise, professional, highly insightful daily newsletter summarising the Top 5 global FinTech stories from the past 48 hours, specifically for finance and tech professionals. Then add a Bonus Round of 5–7 additional stories.

1. Filter by Topic
Identify and retain only the articles related to FinTech. This includes news about:
- Digital banking, neobanks, challenger banks
- Payments innovations, remittances, embedded finance
- Blockchain, cryptocurrencies, DeFi, Web3
- Insurtech, regtech, lending platforms
- Major investments, funding rounds, IPOs in FinTech
- FinTech partnerships, acquisitions, M&A
- AI and data‑driven finance tools, analytics platforms
Skip any articles that don’t centre on FinTech.

2. Handle Paywalled Links
- If an article is from a paywalled site (e.g., WSJ, Bloomberg, Financial Times), find an equivalent non‑paywalled version and update the link.
- Verify each link loads correctly; if it errors, replace it with another working source covering the same story.

3. Remove Duplicates
- I will provide a list of previously used article titles. Exclude any matching titles.

4. Return Format
Output a JSON object with only the relevant, non‑duplicate FinTech articles, in the form:
(
  "Article Title A": "https://link.to/articleA",
  "Article Title B": "https://link.to/articleB",
)


Here is the JSON object of articles:
{self.json_result}

Here are the previously used titles:
None

Evaluation & Ranking
- Rank all provided articles by how compelling, buzzworthy, and attention‑grabbing they are from a FinTech perspective.
- Select the Top 5 most interesting stories—the kind that spark conversation, debate, or shares among FinTech professionals.
- Ensure all articles are in English and non‑paywalled (or replaced by non‑paywalled equivalents).
- If current articles aren’t strong enough, feel free to search for better FinTech news (subject to the same paywall and relevance rules) and include them in the ranking also. Make sure that the link works and doesn't lead me to a 404 page or content not found page. The link must lead to the article. I need you to personally review each link and verify that it leads to the article, not an error page or another page.



Prioritise stories that feature:
Monumental product launches, platform rollouts, or market entries
Surprising strategic moves by major players (e.g., Stripe, Square, Revolut, PayPal, Coinbase)
Large funding rounds, acquisitions, partnerships, or shifts in capital deployment
Viral innovations, integrations, or use‑cases with broad adoption
Cutting‑edge AI/data‑driven finance tools or protocols with real use cases
Bold regulatory or compliance moves that reshape the industry

Deprioritise:
Dry policy/legal updates unless they trigger major industry shifts
Opinion pieces without a clear news event
Minor feature tweaks or small‑scale product updates without strategic impact

Deliverables

Top FinTech Stories Today
Rank from most to least compelling. For each of the Top 5, provide:

1. [Title of Article] – (Reading time, e.g. 5 mins)
   [Link to article]
   What’s happening?
   Concisely explain the who, what, when, and where — include names of companies, product specifics, regions, partners, funding amounts, timelines, etc. Make this readable for everyone, not just fintech enthusiasts
   Why does it matter?
   Frame the big‑picture impact: Is this trend‑setting? Changing how finance works? Shaking up incumbents? Make this readable for everyone, not just fintech enthusiasts.
   Key Insight:
   What’s the strategic punchline or biggest takeaway? Why should FinTech pros pay attention? Make this readable for everyone, not just fintech enthusiasts.

✨ Other FinTech News Worth a Look
These didn’t make the Top 5 but are still notable. List 5–7 with:

– [Title] – (Reading time) - Link(full URL)
  One‑line summary of why it matters.

for context purposes only this is an example of what i want the out put to be similar to:

PayPal to Bring 100 AI and Data Science Jobs to Dublin with New Innovation Centre – (Reading time: 2 mins)
https://www.fintechinshorts.com/paypal-to-bring-100-ai-and-data-science-jobs-to-dublin-with-new-innovation-centre/

What’s happening?
PayPal is opening a dedicated “Advanced Analytics & AI Hub” in Dublin, hiring 100 engineers, data scientists, and ML researchers over the next 12 months. The centre will focus on fraud prevention, credit‑scoring algorithms, and personalized financial insights for small businesses across EMEA.

Why does it matter?
This expansion signals PayPal’s commitment to data‑driven product differentiation. Locating in Dublin leverages EU talent pools and positions the firm to rapidly iterate AI features as Europe’s regulatory landscape around payments and data evolves.

Key Insight:
Scaling AI talent in‑house lets PayPal shorten R&D cycles — a competitive advantage as embedded finance providers race to deliver predictive lending, dynamic risk scoring, and hyper‑personalized payment experiences.
"""

    def crypto_prompt(self):
        return f"""
Crypto Prompt:
Build a tight, high-signal newsletter featuring the Top 5 crypto stories from the last 48 hours.
Target audience: crypto investors, founders, builders, and analysts.
Each top story should include just enough detail to make the reader want to click, while still delivering a punchy summary with substance.
End with a Bonus Round of 5–7 one-liner headlines and links.
1. Filter by Topic
Only include articles related to crypto, blockchain, or Web3. Keep:
Token launches, burns, upgrades, airdrops, tokenomics changes
Protocol upgrades, L1/L2 developments, major forks
DeFi, NFT, or DAO news
Major funding rounds, M&A, ecosystem grants
Regulatory rulings, ETF decisions, crackdowns, or approvals
Exchange listings/delistings, outages, or strategic changes
High-profile hacks, exploits, rug pulls, chain halts
On-chain data signals: TVL shifts, user spikes, fee revenue, treasury moves
Skip anything not about crypto or lacking real impact.
2. Paywalled Sources
If an article is behind a paywall (e.g. WSJ, Bloomberg):
Find a freely accessible version of the same story
Make sure the link works and opens the correct article
If not, replace it with a working alternative
3. Remove Duplicates
If a list of previously used article titles is provided, remove any that match.
4. Output Format
Return a clean JSON object like:
(
"Article Title 1": "https://link1.com",
"Article Title 2": "https://link2.com"
)
Here is the JSON object of articles:
{self.json_result}
Here is the list of previously used article titles:
There are no previously used article titles yet, as this is the first newsletter being created.

5. Article Selection
Pick the 5 most compelling stories — not necessarily the biggest, but the ones that will spark curiosity, FOMO, or insight.
Must be in English
No paywalls
If the current batch is weak, find stronger stories elsewhere
Prioritise stories with:
Big launches, testnets, upgrades, or tokenomics shifts
Surprising moves by major players (Coinbase, Ethereum, SEC, Binance)
$10M+ raises, major M&A, treasury votes
Exploits, critical bugs, and market liquidations
Regulatory action, ETF approvals/denials, and new compliance frameworks
Emerging trends, DAO experiments, DeFi mechanisms, creative mechanisms
Skip or deprioritise:
Legal battles with no resolution
Opinion pieces or speculation
Feature announcements without clear implications
Deliverables — Top 5 Stories
For each of the top 5, use this format:
[Title of Article] – (6 min read)
[Paste URL here]
What’s happening? (~60 words)
Start strong. Say what happened, who’s involved, and why it matters. Include token names, amounts, platforms, chains, or timelines. This should surprise or inform the reader — give them a reason to care.
Why does it matter? (~50 words)
Zoom out. What’s the significance for the market, users, protocols, or regulators? Focus on impact — not summary. Think behaviour change, new playbooks, threat signals, or competitive shifts.
Key Insight: (~30 words)
Leave them with a punchline. What should a founder, investor, or analyst walk away with?
✨ Bonus Round — Other Crypto News Worth a Look
Add 5–7 stories that didn’t make the top 5, but are still useful. Format:
[Title] – (5 min) [Link]
One-line summary that teases the news.
🧪 Example:
StarkWare unlock sends $750M in STRK to insiders, sparking dump fears – The Block, July 26, 2025 – (4 min)
https://www.theblock.co/post/xyz/starkware-token-unlock-fears
What’s happening?
StarkWare released 64 million STRK tokens (~$750M) to early contributors and investors, triggering a 12% price drop overnight. The unlock represents 13% of the total supply and comes amid low liquidity and weak demand.
Why does it matter?
Token unlocks often pressure price, but this size and timing could destabilise confidence in L2S more broadly. Some investors are calling for revised token schedules and governance accountability.
Key Insight:
Tokenomics design is being tested—unlocks without demand or transparency can rattle ecosystems.
"""