# Marketing Automation Guide

## 🎯 Overview

The Automated Marketing Team consists of **5 specialized AI agents** working together to handle all marketing activities with minimal human intervention.

---

## 🤖 The 5 Marketing Agents

### 1. Content Creator Agent

**Role**: Generates all marketing content

**Capabilities**:
- Social media posts (Twitter, Instagram, TikTok, LinkedIn, Reddit)
- Email drip campaigns (5-email sequence)
- Paid ads copy (Google Ads, Facebook Ads)
- SEO content (meta tags, blog outlines, FAQs)

**Usage**:
```python
from agents.marketing_team import ContentCreatorAgent

creator = ContentCreatorAgent()
result = await creator.run(project_id=1)

content = result['data']
# {
#     'social_posts': {...},
#     'email_templates': {...},
#     'ad_copy': {...},
#     'seo_content': {...}
# }
```

---

### 2. Social Media Manager Agent

**Role**: Posts content to social platforms

**Capabilities**:
- Auto-post to Twitter/X
- Schedule Instagram posts
- Publish to LinkedIn
- Submit to Reddit (community-appropriate)

**Usage**:
```python
from agents.marketing_team import SocialMediaManagerAgent

manager = SocialMediaManagerAgent()

# Post to Twitter
await manager.post_to_twitter(
    content="Check out Math Quest! 🎮 Educational game for ages 8-12",
    project_id=1
)

# Post to Instagram
await manager.post_to_instagram(
    content="New game alert! 🎉",
    image_url="https://...",
    project_id=1
)
```

**API Integration** (Production):
```bash
# Install social media SDKs
pip install tweepy instagrapi linkedin-api praw

# Set environment variables
TWITTER_API_KEY=...
TWITTER_API_SECRET=...
INSTAGRAM_USERNAME=...
INSTAGRAM_PASSWORD=...
LINKEDIN_ACCESS_TOKEN=...
REDDIT_CLIENT_ID=...
```

---

### 3. Email Marketer Agent

**Role**: Manages automated email campaigns

**Capabilities**:
- Drip campaign scheduling (5 emails over 14 days)
- Welcome emails
- Tips & tricks emails
- Social proof emails
- Upgrade prompts
- Win-back campaigns

**Usage**:
```python
from agents.marketing_team import EmailMarketerAgent

marketer = EmailMarketerAgent()

# Send drip campaign
await marketer.send_drip_campaign(
    project_id=1,
    email_templates={
        'email_1': {'subject': '...', 'body': '...'},
        'email_2': {'subject': '...', 'body': '...'},
        ...
    }
)
```

**Email Schedule**:
- **Day 1**: Welcome email (immediate)
- **Day 2**: Tips & tricks
- **Day 5**: Social proof (testimonials, stats)
- **Day 7**: Upgrade/monetization
- **Day 14**: Win-back (if inactive)

**API Integration** (Production):
```bash
# Install email service SDK
pip install sendgrid  # or mailchimp, mailgun, etc.

# Set environment variable
SENDGRID_API_KEY=...
```

---

### 4. Paid Ads Optimizer Agent

**Role**: Creates and optimizes paid advertising campaigns

**Capabilities**:
- Create Google Ads campaigns
- Create Facebook/Instagram Ads
- A/B test ad variations
- Adjust bids based on performance
- Pause underperforming ads
- Scale winning ads

**Usage**:
```python
from agents.marketing_team import PaidAdsOptimizerAgent

optimizer = PaidAdsOptimizerAgent()

# Create Google Ads campaign
await optimizer.create_google_ads_campaign(
    project_id=1,
    ad_copy={
        'headlines': ['Math Quest', 'Learn While Playing', 'Safe for Kids'],
        'descriptions': ['Educational game...', 'No ads, no tracking...']
    },
    budget=100.0  # $100/day
)

# Optimize existing campaigns
await optimizer.optimize_campaigns(project_id=1)
# Automatically pauses ads with CPA > target
# Increases budget for ads with ROAS > 3.0
```

**Optimization Rules**:
- **Pause** if CPA > target_cpa * 1.5
- **Increase budget** if ROAS > 3.0
- **A/B test** new variations every 7 days
- **Stop** if no conversions after $50 spend

**API Integration** (Production):
```bash
# Install ad platform SDKs
pip install google-ads facebook-business

# Set environment variables
GOOGLE_ADS_DEVELOPER_TOKEN=...
GOOGLE_ADS_CLIENT_ID=...
FACEBOOK_APP_ID=...
FACEBOOK_APP_SECRET=...
```

---

### 5. Growth Hacker Agent

**Role**: Implements viral growth loops

**Capabilities**:
- Referral program implementation
- Viral coefficient optimization (K factor)
- Sharing incentive design
- Social proof integration
- Network effects analysis

**Usage**:
```python
from agents.marketing_team import GrowthHackerAgent

hacker = GrowthHackerAgent()

# Implement referral program
await hacker.implement_referral_program(project_id=1)
# Adds: "Invite 3 friends, unlock premium features!"

# Optimize viral loops
await hacker.optimize_viral_loops(project_id=1)
# Analyzes K factor, suggests improvements
```

**Viral Coefficient (K Factor)**:
```
K = Invites per User × Invite Conversion Rate

If K > 1.0 → Viral growth 🚀
If K < 1.0 → Need improvements
```

**Example Improvements**:
- Add share button after app completion
- Increase incentive ("5 friends = unlock all themes")
- Simplify sharing (one-tap WhatsApp)
- Add social proof ("Join 1,234 users!")

---

## 🔄 Automated Marketing Team

Coordinates all 5 agents together.

### Daily Marketing Cycle

```python
from agents.marketing_team import AutomatedMarketingTeam

team = AutomatedMarketingTeam()

# Run daily automation
result = await team.run_daily_marketing_cycle(project_id=1)
```

**What happens**:
1. **Content Creator** generates fresh content
2. **Social Manager** posts to all platforms (1 post each)
3. **Email Marketer** sends scheduled emails
4. **Ads Optimizer** adjusts bids and budgets
5. **Growth Hacker** optimizes viral loops

**Frequency**: Runs daily at 9 AM (configurable)

---

### Launch Campaign

```python
# Full marketing blitz for new app launch
result = await team.run_launch_campaign(
    project_id=1,
    budget=100.0  # $100 total
)
```

**What happens**:
1. **Content Creator** generates all content
2. **Social Manager** posts to ALL platforms (multiple posts)
3. **Ads Optimizer** creates Google Ads (60% budget) + Facebook Ads (40% budget)
4. **Growth Hacker** activates referral program
5. **Email Marketer** sets up drip campaign

**Budget Allocation**:
- Google Ads: 60% ($60)
- Facebook Ads: 40% ($40)

---

## 📊 Analytics

Track marketing performance:

```python
from database.models import SessionLocal, Project, Metric

session = SessionLocal()

# Get marketing metrics
metrics = session.query(Metric).filter_by(
    project_id=1,
    metric_name='marketing_performance'
).all()

for m in metrics:
    print(f"{m.metric_name}: {m.metric_value}")

session.close()
```

**Key Metrics**:
- **Social reach**: Impressions, clicks
- **Email open rate**: %
- **Email click rate**: %
- **Ad CTR**: Click-through rate
- **Ad CPA**: Cost per acquisition
- **Ad ROAS**: Return on ad spend
- **Viral K factor**: Invite conversion
- **Share rate**: % users who share

---

## ⚙️ Configuration

Add to `.env`:

```bash
# Social Media APIs
TWITTER_API_KEY=...
TWITTER_API_SECRET=...
INSTAGRAM_USERNAME=...
INSTAGRAM_PASSWORD=...
LINKEDIN_ACCESS_TOKEN=...
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...

# Email Service
SENDGRID_API_KEY=...

# Paid Ads
GOOGLE_ADS_DEVELOPER_TOKEN=...
GOOGLE_ADS_CLIENT_ID=...
GOOGLE_ADS_CLIENT_SECRET=...
FACEBOOK_APP_ID=...
FACEBOOK_APP_SECRET=...
FACEBOOK_ACCESS_TOKEN=...

# Marketing Schedule
MARKETING_RUN_HOUR=9  # Run at 9 AM
MARKETING_RUN_TIMEZONE=UTC
```

---

## 🚀 Integration with Pipeline

Add marketing to orchestration pipeline:

```python
# In orchestration/pipeline.py

from agents.marketing_team import AutomatedMarketingTeam

class AgentPipeline:
    def __init__(self):
        # ... existing agents ...
        self.marketing_team = AutomatedMarketingTeam()
    
    async def run_full_pipeline(self, project_id=None):
        # ... after launch ...
        
        # Run marketing campaign
        logger.info("stage_started", stage="marketing_automation", project_id=project_id)
        marketing_result = await self.marketing_team.run_launch_campaign(
            project_id=project_id,
            budget=50.0  # $50 launch budget
        )
        results["stages"]["marketing_automation"] = marketing_result
```

---

## 📈 Advanced Features

### A/B Testing Marketing Copy

```python
# Generate 3 variations of social posts
variations = await content_creator.generate_social_variations(
    project_id=1,
    count=3
)

# Test each variation
for i, variant in enumerate(variations):
    await social_manager.post_to_twitter(variant, project_id=1)
    
    # Track performance
    performance = await track_performance(variant_id=i)
    
    # Pick winner after 24 hours
    if i == len(variations) - 1:
        winner = max(performance, key=lambda x: x['engagement_rate'])
        logger.info("ab_test_winner", variant_id=winner['variant_id'])
```

### Automated Influencer Outreach

```python
# Find relevant influencers
influencers = await growth_hacker.find_influencers(
    niche="educational games",
    follower_count=(10000, 100000),
    engagement_rate=0.03  # 3%+
)

# Send personalized DMs
for influencer in influencers:
    await social_manager.send_dm(
        platform="instagram",
        username=influencer['username'],
        message=f"Hi {influencer['name']}, we'd love to collaborate..."
    )
```

---

## ⚠️ Compliance

**Social Media**:
- Respect platform rate limits
- Follow community guidelines
- Disclose sponsored content
- Don't spam

**Email**:
- CAN-SPAM compliance
- Include unsubscribe link
- Accurate from/subject lines
- Honor unsubscribes within 10 days

**Paid Ads**:
- Google Ads policies
- Facebook Ads policies
- Age-appropriate targeting
- No misleading claims

**GDPR/Privacy**:
- Get consent for emails
- Allow data deletion requests
- Transparent data usage

---

## 🎯 Best Practices

1. **Start Small**: Test with one platform, then scale
2. **Monitor Daily**: Check metrics every day
3. **Iterate**: A/B test everything
4. **Budget Wisely**: Start with $50/month, scale based on ROAS
5. **Be Authentic**: No corporate speak, genuine voice
6. **Respect Users**: Don't spam, provide value
7. **Track Everything**: Use UTM parameters
8. **Optimize Weekly**: Review and adjust strategies

---

## 📝 Checklist

Before launching automated marketing:

- [ ] Set up social media accounts
- [ ] Configure API keys in `.env`
- [ ] Test email deliverability
- [ ] Set up Google Analytics
- [ ] Create Facebook Pixel
- [ ] Define target CPA and ROAS
- [ ] Prepare ad creatives (images, videos)
- [ ] Set up referral program page
- [ ] Configure budget limits
- [ ] Test one campaign manually
- [ ] Set up monitoring dashboard

---

## 🔧 Troubleshooting

**Issue**: Social posts not publishing

**Solution**: Check API credentials, rate limits

**Issue**: Email open rate < 15%

**Solution**: Improve subject lines, verify deliverability

**Issue**: Ad CPA too high

**Solution**: Narrow targeting, improve ad copy, test new creatives

**Issue**: Low viral K factor (<0.5)

**Solution**: Increase sharing incentives, simplify sharing flow

---

**The marketing team runs 24/7, so you don't have to.** ✨
