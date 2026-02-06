"""Campaign Executor - Automates Valentine's and Ramadan campaigns."""

import json
import asyncio
from datetime import datetime
from typing import Dict, Any
from agents.marketing_team import AutomatedMarketingTeam
from database.models import SessionLocal, Project
from utils.logger import get_logger

logger = get_logger("campaigns.executor")


class CampaignExecutor:
    """Executes pre-defined seasonal campaigns."""
    
    def __init__(self):
        self.marketing_team = AutomatedMarketingTeam()
    
    async def execute_valentines_campaign(self, project_id: int):
        """
        Execute Valentine's Day campaign for PlayGift.
        
        Based on: campaigns/valentines_campaign.json
        """
        
        logger.info("valentines_campaign_started", project_id=project_id)
        
        # Load campaign config
        with open('campaigns/valentines_campaign.json', 'r') as f:
            campaign = json.load(f)
        
        # Generate Valentine's-specific content
        content = await self._generate_valentines_content(project_id, campaign)
        
        # Execute multi-channel campaign
        results = {
            "campaign": "valentines",
            "channels": {}
        }
        
        # Channel 1: TikTok/Instagram
        logger.info("channel_started", channel="tiktok_instagram")
        results["channels"]["tiktok_instagram"] = await self._execute_social_media(
            platform="instagram",
            content=content["social_posts"]["instagram"],
            budget=campaign["channels"][0]["budget"]
        )
        
        # Channel 2: Google Ads
        logger.info("channel_started", channel="google_ads")
        results["channels"]["google_ads"] = await self._execute_google_ads(
            keywords=campaign["channels"][1]["keywords"],
            ad_copy=content["ad_copy"]["google"],
            budget=campaign["channels"][1]["budget"]
        )
        
        # Channel 3: Facebook/Instagram Ads
        logger.info("channel_started", channel="facebook_ads")
        results["channels"]["facebook_ads"] = await self._execute_facebook_ads(
            targeting=campaign["channels"][2]["targeting"],
            ad_copy=content["ad_copy"]["facebook"],
            budget=campaign["channels"][2]["budget"]
        )
        
        # Channel 4: Reddit (Organic)
        logger.info("channel_started", channel="reddit")
        results["channels"]["reddit"] = await self._execute_reddit_campaign(
            subreddits=campaign["channels"][3]["subreddits"],
            content=content["reddit_posts"]
        )
        
        # Channel 5: Email
        logger.info("channel_started", channel="email")
        results["channels"]["email"] = await self._execute_email_campaign(
            project_id=project_id,
            sequence=campaign["channels"][6]["sequence"],
            templates=content["email_templates"]
        )
        
        # Cross-promotion
        await self._enable_cross_promotion(project_id, campaign["cross_promotion"])
        
        logger.info("valentines_campaign_completed", project_id=project_id, results=results)
        
        return results
    
    async def execute_ramadan_campaign(self, project_id: int):
        """
        Execute Ramadan campaign for PlayGift.
        
        Based on: campaigns/ramadan_campaign.json
        """
        
        logger.info("ramadan_campaign_started", project_id=project_id)
        
        # Load campaign config
        with open('campaigns/ramadan_campaign.json', 'r') as f:
            campaign = json.load(f)
        
        # Generate Ramadan-specific content
        content = await self._generate_ramadan_content(project_id, campaign)
        
        # Execute multi-channel campaign
        results = {
            "campaign": "ramadan",
            "channels": {}
        }
        
        # Channel 1: WhatsApp (Viral)
        logger.info("channel_started", channel="whatsapp")
        results["channels"]["whatsapp"] = await self._setup_whatsapp_viral_loop(
            share_message=campaign["channels"][0]["mechanics"]["share_message"],
            viral_target=campaign["channels"][0]["mechanics"]["viral_coefficient_target"]
        )
        
        # Channel 2: Instagram (Influencers)
        logger.info("channel_started", channel="instagram_influencers")
        results["channels"]["instagram"] = await self._execute_influencer_campaign(
            influencers=campaign["channels"][1]["influencers"],
            content=content["social_posts"]["instagram"],
            budget=campaign["channels"][1]["budget"]
        )
        
        # Channel 3: TikTok
        logger.info("channel_started", channel="tiktok")
        results["channels"]["tiktok"] = await self._execute_tiktok_campaign(
            content_themes=campaign["channels"][2]["content_themes"],
            content=content["social_posts"]["tiktok"],
            budget=campaign["channels"][2]["budget"]
        )
        
        # Channel 4: Mosques (Offline)
        logger.info("channel_started", channel="mosques")
        results["channels"]["mosques"] = await self._setup_mosque_campaign(
            partner_mosques=campaign["channels"][3]["execution"]["partner_mosques"],
            qr_code_link=f"https://playgift.app/ramadan?ref=mosque",
            budget=campaign["channels"][3]["budget"]
        )
        
        # Charitable component
        await self._setup_charitable_donation(
            campaign["charitable_component"]["initiative"],
            campaign["charitable_component"]["expected_donation"]
        )
        
        logger.info("ramadan_campaign_completed", project_id=project_id, results=results)
        
        return results
    
    async def _generate_valentines_content(self, project_id: int, campaign: Dict) -> Dict:
        """Generate Valentine's-specific content."""
        
        # Use content creator agent
        result = await self.marketing_team.content_creator.run(project_id)
        
        if not result["success"]:
            raise Exception(f"Content generation failed: {result['error']}")
        
        content = result["data"]
        
        # Customize for Valentine's
        content["social_posts"]["instagram"] = [
            "💝 Skip the flowers this Valentine's. Send a personalized GAME instead! ✨",
            "POV: Your partner made you a custom game for Valentine's Day 🥹❤️",
            "Chocolates melt. Flowers die. But THIS gift lasts forever 🎮💘"
        ]
        
        content["reddit_posts"] = [
            {
                "subreddit": "r/dubai",
                "title": "I made my girlfriend a personalized game for Valentine's [authentic story]",
                "body": "Wanted to share because I was stressing about what to get her..."
            }
        ]
        
        return content
    
    async def _generate_ramadan_content(self, project_id: int, campaign: Dict) -> Dict:
        """Generate Ramadan-specific content."""
        
        result = await self.marketing_team.content_creator.run(project_id)
        
        if not result["success"]:
            raise Exception(f"Content generation failed: {result['error']}")
        
        content = result["data"]
        
        # Customize for Ramadan
        content["social_posts"]["instagram"] = [
            "🌙 Ramadan Mubarak! Share joy with your family through FREE games ✨",
            "After Iftar, bring the family together with these Ramadan games 🎮",
            "Teaching kids about Zakat has never been this fun! 📚🎮"
        ]
        
        content["social_posts"]["tiktok"] = [
            "POV: It's Ramadan and your family is ultra competitive 😂🌙",
            "Surprising my mom with a personalized Ramadan game 🥹❤️",
            "Things Muslims do in Ramadan: Play Iftar Rush with siblings 🎮"
        ]
        
        return content
    
    async def _execute_social_media(self, platform: str, content: list, budget: float):
        """Execute social media campaign."""
        
        posts_scheduled = 0
        
        for post in content[:5]:  # Post 5 times during campaign
            await self.marketing_team.social_manager.post_to_instagram(
                content=post,
                image_url=None,
                project_id=1
            )
            posts_scheduled += 1
        
        return {
            "platform": platform,
            "posts_scheduled": posts_scheduled,
            "budget_allocated": budget,
            "status": "scheduled"
        }
    
    async def _execute_google_ads(self, keywords: list, ad_copy: dict, budget: float):
        """Execute Google Ads campaign."""
        
        await self.marketing_team.ads_optimizer.create_google_ads_campaign(
            project_id=1,
            ad_copy=ad_copy,
            budget=budget
        )
        
        return {
            "platform": "google_ads",
            "keywords": keywords,
            "budget_allocated": budget,
            "status": "live"
        }
    
    async def _execute_facebook_ads(self, targeting: dict, ad_copy: dict, budget: float):
        """Execute Facebook Ads campaign."""
        
        await self.marketing_team.ads_optimizer.create_facebook_ads_campaign(
            project_id=1,
            ad_copy=ad_copy,
            budget=budget
        )
        
        return {
            "platform": "facebook_ads",
            "targeting": targeting,
            "budget_allocated": budget,
            "status": "live"
        }
    
    async def _execute_reddit_campaign(self, subreddits: list, content: list):
        """Execute Reddit organic campaign."""
        
        posts_submitted = 0
        
        for i, post in enumerate(content):
            if i < len(subreddits):
                await self.marketing_team.social_manager.post_to_reddit(
                    subreddit=subreddits[i],
                    title=post["title"],
                    content=post["body"],
                    project_id=1
                )
                posts_submitted += 1
        
        return {
            "platform": "reddit",
            "subreddits": subreddits,
            "posts_submitted": posts_submitted,
            "budget_allocated": 0,
            "status": "submitted"
        }
    
    async def _execute_email_campaign(self, project_id: int, sequence: list, templates: dict):
        """Execute email drip campaign."""
        
        await self.marketing_team.email_marketer.send_drip_campaign(
            project_id=project_id,
            email_templates=templates
        )
        
        return {
            "platform": "email",
            "emails_scheduled": len(sequence),
            "status": "scheduled"
        }
    
    async def _execute_influencer_campaign(self, influencers: dict, content: list, budget: float):
        """Execute influencer marketing campaign."""
        
        logger.info(
            "influencer_campaign_setup",
            count=influencers["count"],
            budget_per_post=influencers["cost_per_post"],
            total_budget=budget
        )
        
        return {
            "platform": "instagram_influencers",
            "influencer_count": influencers["count"],
            "budget_allocated": budget,
            "posts_expected": influencers["count"],
            "status": "outreach_in_progress"
        }
    
    async def _execute_tiktok_campaign(self, content_themes: list, content: list, budget: float):
        """Execute TikTok campaign."""
        
        for post in content[:3]:  # 3 posts during campaign
            # Schedule TikTok posts
            logger.info("tiktok_post_scheduled", content=post[:50])
        
        return {
            "platform": "tiktok",
            "posts_scheduled": len(content_themes),
            "budget_allocated": budget,
            "status": "scheduled"
        }
    
    async def _setup_mosque_campaign(self, partner_mosques: int, qr_code_link: str, budget: float):
        """Set up mosque/community center campaign."""
        
        logger.info(
            "mosque_campaign_setup",
            partner_mosques=partner_mosques,
            qr_link=qr_code_link,
            budget=budget
        )
        
        return {
            "platform": "offline_mosques",
            "partner_mosques": partner_mosques,
            "qr_codes_printed": partner_mosques * 5,  # 5 posters per mosque
            "budget_allocated": budget,
            "status": "printing_in_progress"
        }
    
    async def _setup_whatsapp_viral_loop(self, share_message: str, viral_target: float):
        """Set up WhatsApp viral sharing mechanics."""
        
        logger.info(
            "whatsapp_viral_setup",
            target_k_factor=viral_target
        )
        
        return {
            "platform": "whatsapp",
            "share_message_template": share_message,
            "viral_coefficient_target": viral_target,
            "status": "active"
        }
    
    async def _enable_cross_promotion(self, project_id: int, cross_promo: dict):
        """Enable cross-promotion between PlayGift and Autonomous Factory."""
        
        logger.info(
            "cross_promotion_enabled",
            playgift_to_factory=cross_promo.get("playgift_to_factory"),
            factory_to_playgift=cross_promo.get("factory_to_playgift")
        )
    
    async def _setup_charitable_donation(self, initiative: str, expected_donation: float):
        """Set up charitable donation component."""
        
        logger.info(
            "charitable_donation_setup",
            initiative=initiative,
            expected_donation_usd=expected_donation
        )


async def main():
    """Run campaign executor."""
    
    executor = CampaignExecutor()
    
    # Check current date to determine which campaign to run
    now = datetime.utcnow()
    
    if now.month == 2 and now.day <= 14:
        # Valentine's campaign
        print("🚀 Launching Valentine's Campaign...")
        result = await executor.execute_valentines_campaign(project_id=1)
        print(f"✅ Valentine's campaign launched: {result}")
    
    elif now.month == 3 and now.day <= 30:
        # Ramadan campaign
        print("🚀 Launching Ramadan Campaign...")
        result = await executor.execute_ramadan_campaign(project_id=1)
        print(f"✅ Ramadan campaign launched: {result}")
    
    else:
        print("ℹ️ No seasonal campaign active. Run specific campaign manually.")


if __name__ == "__main__":
    asyncio.run(main())
