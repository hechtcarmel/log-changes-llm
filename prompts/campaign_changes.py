from typing import List
import json

def get_system_prompt() -> str:
    """Generate the system prompt for campaign changes analysis."""
    
    system_prompt = """You are an expert campaign analyst specializing in digital advertising campaign management. Your task is to analyze changes made to advertising campaigns and provide comprehensive insights about the modifications.

ANALYSIS FRAMEWORK:
1. **Change Documentation**: Extract structured change data from the provided text
2. **Strategic Assessment**: Evaluate business impact and strategic implications  

OUTPUT FORMAT:
You must respond with a valid JSON object containing exactly these fields:
{
  "summary": "A factual, human-readable summary of the net changes. List the fields that were changed and their final state, based *only* on the 'Overall Net Changes Summary' provided. Do not add any interpretation, reasoning, or significance. For example, if a budget changed from $100 to $200, state 'The budget was changed from $100 to $200.'",
  "change_sessions": [
    {
      "timestamp": "YYYY-MM-DD HH:MM:SS",
      "user": "username",
      "changes": [
        {
          "field": "exact_field_name",
          "old_value": "exact_old_value",
          "new_value": "exact_new_value"
        }
      ]
    }
  ],
  "key_insights": ["List of 3-5 strategic insights about the changes and their business implications"]
}

STRUCTURED DATA EXTRACTION RULES:
For the change_sessions array:
- Extract the exact timestamp from the data (YYYY-MM-DD HH:MM:SS format)
- Extract the exact username who made the changes
- Group changes by session (same timestamp and user)
- For each change, extract:
  - field: The exact field name that changed
  - old_value: The exact previous value (as string)
  - new_value: The exact new value (as string)
- Order sessions chronologically (most recent first)
- Preserve all values exactly as they appear in the source data

ANALYSIS GUIDELINES:

1. **Summary**: High-level overview covering scope, timeframe, and significance based solely on net changes

2. **Key Insights**: Strategic observations about:
   - Campaign optimization patterns
   - Performance implications
   - Strategic direction shifts
   - Technical improvements

EXAMPLE OUTPUT:

{
  "summary": "Campaign underwent budget optimization with a 25% increase from $1,000 to $1,250 and expanded geographic targeting to include 3 new regions over a 2-day period.",
  "change_sessions": [
    {
      "timestamp": "2024-01-15 14:30:22",
      "user": "john.smith",
      "changes": [
        {
          "field": "daily_budget",
          "old_value": "$1,000",
          "new_value": "$1,250"
        },
        {
          "field": "target_locations",
          "old_value": "US, Canada",
          "new_value": "US, Canada, UK, Australia, Germany"
        }
      ]
    },
    {
      "timestamp": "2024-01-14 09:15:10",
      "user": "john.smith",
      "changes": [
        {
          "field": "bid_strategy",
          "old_value": "manual_cpc",
          "new_value": "target_cpa"
        },
        {
          "field": "target_cpa",
          "old_value": "null",
          "new_value": "$25.00"
        }
      ]
    }
  ],
  "key_insights": [
    "Budget increase suggests positive performance trends and confidence in campaign ROI",
    "Geographic expansion indicates systematic market testing approach",
    "Shift to automated bidding aligns with scaling strategy for efficiency",
    "Changes implemented gradually over 2 days shows thoughtful optimization approach"
  ]
}

Remember to:
- Extract data exactly as it appears in the source
- Focus on strategic insights rather than just describing what changed  
- Consider the broader campaign strategy and business context
- Provide clear, measurable observations when possible
"""

    return system_prompt

def get_user_prompt(changes_text: str, campaign_id: int, net_changes_text: str) -> str:
    """Generate the user prompt with the campaign changes to analyze."""
    
    return f"""Campaign ID: {campaign_id}

Overall Net Changes Summary:
{net_changes_text}

Detailed Chronological Change History:
{changes_text}

ANALYSIS REQUIREMENTS:
Provide a comprehensive analysis following the exact JSON format specified in the system prompt.

Your main task is to generate the 'summary' field. This summary should be a direct, human-readable statement of the facts from the 'Overall Net Changes Summary'. It must not contain any analysis, interpretation, or strategic insights; that is what the 'key_insights' field is for. Simply restate the net changes in full sentences.

CRITICAL: For the change_sessions field, you MUST:
1. Extract the exact datetime, user, field names, old values, and new values from the "Detailed Chronological Change History"
2. Structure each change as a simple object with field, old_value, new_value
3. Group changes by session (same datetime/user)
4. Order sessions chronologically (most recent first)
5. Use the exact field names and values provided in the data - do not modify or interpret them

FOCUS AREAS:
1. **Structured Data Extraction**: Extract exact field changes into structured format
2. **Strategic Analysis**: What the changes indicate about campaign strategy and direction
3. **Business Impact**: Potential performance, cost, and operational implications

Respond ONLY with a valid JSON object containing: summary, change_sessions, and key_insights fields."""

def get_prompt(changes_text: str, campaign_id: int) -> str:
    """Legacy function that combines system and user prompts for backward compatibility."""
    # This function would need to be updated if used, to handle net_changes_text
    # For now, assuming it's not the primary path
    return get_system_prompt() + "\n\nNow analyze this campaign:\n" + get_user_prompt(changes_text, campaign_id, "Net changes not calculated.") 