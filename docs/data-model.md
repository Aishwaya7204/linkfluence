# LinkFluence Data Model

## creators
Stores creator profile information: name, handle, niche, platform, follower count, engagement rate, estimated demo rate, location, biography, and image URL.

## campaigns
Stores brand campaign briefs, including brand name, campaign title, niche, platform, budget, target follower count, and description.

## campaign_matches
Stores the score calculated for each creator against a campaign. Each row references one campaign and one creator.

## Relationships
- One campaign can have many campaign match rows.
- One creator can appear in many campaign match rows.
- Foreign keys connect `campaign_matches` to `campaigns` and `creators`.

## Notes
The included profiles are fictional sample data. Rates, follower counts, and engagement figures are for demonstration only.
