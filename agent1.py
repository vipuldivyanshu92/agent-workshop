from agents import function_tool, HostedMCPTool, Agent, ModelSettings, TResponseInputItem, Runner, RunConfig
from pydantic import BaseModel
import asyncio

# Tool definitions
@function_tool
def get_retention_offers(customer_id: str, account_type: str, current_plan: str, tenure_months, recent_complaints):
  pass

mcp = HostedMCPTool(tool_config={
  "type": "mcp",
  "server_label": "laslda",
  "allowed_tools": [
    "getInsightsHistorical",
    "blockUsersDms",
    "createDmByConversationId",
    "getSpacesByIds",
    "streamLikesFirehose",
    "getPostsQuotedPosts",
    "streamPostsFirehoseEn",
    "unpinList",
    "deleteNotes",
    "getPostsCountsAll",
    "searchPostsRecent",
    "streamPostsFirehoseKo",
    "getCommunitiesById",
    "unmuteUser",
    "getListsPosts",
    "getUsersMe",
    "getUsersByUsernames",
    "getPostsCountsRecent",
    "getOpenApiSpec",
    "getPostsLikingUsers",
    "streamLikesSample10",
    "searchCommunities",
    "getListsFollowers",
    "unfollowUser",
    "deletePosts",
    "getPostsById",
    "getUsersFollowing",
    "followUser",
    "searchCommunityNotesWritten",
    "streamUsersCompliance",
    "getUsersLikedPosts",
    "getSpacesByCreatorIds",
    "getInsights28Hr",
    "deleteLists",
    "getListsById",
    "updateLists",
    "getDirectMessagesEvents",
    "getTrendsByWoeid",
    "getUsersFollowers",
    "likePost",
    "getUsersTimeline",
    "getComplianceJobsById",
    "streamLabelsCompliance",
    "getUsersBookmarkFolders",
    "deleteAccountActivitySubscription",
    "finalizeMediaUpload",
    "createMediaMetadata",
    "streamPostsSample",
    "streamPostsFirehoseJa",
    "getMediaByMediaKey",
    "getUsersBookmarks",
    "createUsersBookmark",
    "updateRules",
    "getRules",
    "getComplianceJobs",
    "createComplianceJobs",
    "appendMediaUpload",
    "initializeMediaUpload",
    "streamLikesCompliance",
    "deleteDmEvents",
    "getDirectMessagesEventsById",
    "streamPostsSample10",
    "getMediaUploadStatus",
    "mediaUpload",
    "unblockUsersDms",
    "getTrendsPersonalizedTrends",
    "validateAccountActivitySubscription",
    "createAccountActivitySubscription",
    "searchSpaces",
    "getUsersOwnedLists",
    "getWebhooks",
    "createWebhooks",
    "createDmByParticipantId",
    "streamPostsFirehose",
    "deleteUsersBookmark",
    "getUsersRepostsOfMe",
    "streamPosts",
    "streamPostsCompliance",
    "getPostsAnalytics",
    "hidePostsReply",
    "getUsersMuting",
    "muteUser",
    "unrepostPost",
    "getUsersByIds",
    "getSpacesById",
    "getSpacesBuyers",
    "createLists",
    "createNotes",
    "streamPostsFirehosePt",
    "getMediaAnalytics",
    "getUsage",
    "repostPost",
    "getDmEventsByParticipantId",
    "getUsersPinnedLists",
    "pinList",
    "deleteAllConnections",
    "getSpacesPosts",
    "createAccountActivityReplayJob",
    "getAccountActivitySubscriptionCount",
    "searchUsers",
    "getUsersBookmarksByFolderId",
    "createDmConversations",
    "getPostsByIds",
    "createPosts",
    "deleteWebhooks",
    "validateWebhooks",
    "getPostsRepostedBy",
    "getDmConversationsIdDmEvents",
    "getMediaByMediaKeys",
    "getListsMembers",
    "addListsMember",
    "searchPostsAll",
    "getUsersBlocking",
    "unfollowList",
    "removeListsMemberByUserId",
    "getUsersByUsername",
    "getUsersListMemberships",
    "getUsersById",
    "getUsersMentions",
    "getUsersFollowedLists",
    "followList",
    "unlikePost",
    "searchEligiblePosts",
    "getRuleCounts",
    "getAccountActivitySubscriptions",
    "getUsersPosts",
    "deleteMediaSubtitles",
    "createMediaSubtitles",
    "getPostsReposts"
  ],
  "authorization": "REDACTED",
  "require_approval": "never",
  "server_url": "https://xmcp.mcp.openapps.ai/mcp"
})
class ClassificationAgentSchema(BaseModel):
  classification: str


classification_agent = Agent(
  name="Classification agent",
  instructions="""Classify the user’s intent into one of the following categories: \"return_item\", \"cancel_subscription\", or \"get_information\". 

1. Any device-related return requests should route to return_item.
2. Any retention or cancellation risk, including any request for discounts should route to cancel_subscription.
3. Any other requests should go to get_information.""",
  model="gpt-4.1-mini",
  output_type=ClassificationAgentSchema,
  model_settings=ModelSettings(
    temperature=1,
    top_p=1,
    max_tokens=2048,
    store=True
  )
)


return_agent = Agent(
  name="Return agent",
  instructions="""Offer a replacement device with free shipping.
""",
  model="gpt-4.1-mini",
  model_settings=ModelSettings(
    temperature=1,
    top_p=1,
    max_tokens=2048,
    store=True
  )
)


retention_agent = Agent(
  name="Retention Agent",
  instructions="You are a customer retention conversational agent whose goal is to prevent subscription cancellations. Ask for their current plan and reason for dissatisfaction. Use the get_retention_offers to identify return options. For now, just say there is a 20% offer available for 1 year.",
  model="gpt-4.1-mini",
  tools=[
    get_retention_offers
  ],
  model_settings=ModelSettings(
    temperature=1,
    top_p=1,
    parallel_tool_calls=True,
    max_tokens=2048,
    store=True
  )
)


information_agent = Agent(
  name="Information agent",
  instructions="""You are an information agent for answering informational queries. Your aim is to provide clear, concise responses to user questions. Use the policy below to assemble your answer.

Company Name: HorizonTel Communications Industry: Telecommunications Region: North America
📋 Policy Summary: Mobile Service Plan Adjustments
Policy ID: MOB-PLN-2025-03 Effective Date: March 1, 2025 Applies To: All residential and small business mobile customers
Purpose: To ensure customers have transparent and flexible options when modifying or upgrading their existing mobile service plans.
🔄 Plan Changes & Upgrades
Eligibility: Customers must have an active account in good standing (no outstanding balance > $50).
Upgrade Rules:
Device upgrades are permitted once every 12 months if the customer is on an eligible plan.
Early upgrades incur a $99 early-change fee unless the new plan’s monthly cost is higher by at least $15.
Downgrades: Customers can switch to a lower-tier plan at any time; changes take effect at the next billing cycle.
CS Rep Tip: When customers request plan changes, confirm their next billing cycle and remind them that prorated charges may apply. Always check for active device installment agreements before confirming a downgrade.
💰 Billing & Credits
Billing Cycle: Monthly, aligned with the activation date.
Credit Adjustments:
Overcharges under $10 are automatically credited to the next bill.
For amounts >$10, open a “Billing Adjustment – Tier 2” ticket for supervisor review.
Refund Policy:
Refunds are issued to the original payment method within 7–10 business days.
For prepaid accounts, credits are applied to the balance—no cash refunds.
CS Rep Tip: If a customer reports a billing discrepancy within 30 days, you can issue an immediate one-time goodwill credit (up to $25) without manager approval.
🛜 Network & Outage Handling
Planned Maintenance: Customers receive SMS alerts for outages >1 hour.
Unplanned Outages:
Check the internal “Network Status Dashboard” before escalating.
If multiple customers in a region report the same issue, tag the ticket as “Regional Event – Network Ops.”
Compensation: Customers experiencing service interruption exceeding 24 consecutive hours are eligible for a 1-day service credit upon request.
📞 Retention & Cancellations
Notice Period: 30 days for postpaid accounts; immediate for prepaid.
Retention Offers:
Agents may offer up to 20% off the next 3 billing cycles if the customer cites “cost concerns.”
Retention codes must be logged under “RET-SAVE20.”
Cancellation Fee:
Applies only to term contracts (usually $199 flat rate).
Fee waived for verified relocation to non-serviceable area.
CS Rep Tip: Before processing a cancellation, review alternative retention offers—customers frequently stay when offered a temporary discount or bonus data package.
🧾 Documentation Checklist for CS Reps
Verify customer ID and account number.
Check account standing (billing, contracts, upgrades).
Record all interactions in the CRM ticket.
Confirm next billing cycle date for any changes.
Apply standard note template:
“Customer requested [plan/billing/support] change. Informed of applicable fees, next cycle adjustment, and confirmation reference #[ticket].”
⚠️ Compliance & Privacy
All interactions must comply with CCPA and FCC privacy standards.
Do not record or store personal payment information outside the secure billing system.
Use the “Secure Verification Flow” for identity confirmation before discussing account details.
🧠 Example""",
  model="gpt-4.1-mini",
  tools=[
    mcp
  ],
  model_settings=ModelSettings(
    temperature=1,
    top_p=1,
    max_tokens=2048,
    store=True
  )
)


def approval_request(message: str):
  # TODO: Implement
  return True

class WorkflowInput(BaseModel):
  input_as_text: str


# Main code entrypoint
async def run_workflow(workflow_input: WorkflowInput):
  state = {

  }
  workflow = workflow_input.model_dump()
  conversation_history: list[TResponseInputItem] = [
    {
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": workflow["input_as_text"]
        }
      ]
    }
  ]
  classification_agent_result_temp = await Runner.run(
    classification_agent,
    input=[
      *conversation_history
    ],
    run_config=RunConfig(trace_metadata={
      "__trace_source__": "agent-builder",
      "workflow_id": "wf_68e6dd71872481909eb60bccb551c14e088758ac0b559890"
    })
  )

  conversation_history.extend([item.to_input_item() for item in classification_agent_result_temp.new_items])

  classification_agent_result = {
    "output_text": classification_agent_result_temp.final_output.json(),
    "output_parsed": classification_agent_result_temp.final_output.model_dump()
  }
  if classification_agent_result["output_parsed"]["classification"] == "return_item":
    return_agent_result_temp = await Runner.run(
      return_agent,
      input=[
        *conversation_history
      ],
      run_config=RunConfig(trace_metadata={
        "__trace_source__": "agent-builder",
        "workflow_id": "wf_68e6dd71872481909eb60bccb551c14e088758ac0b559890"
      })
    )

    conversation_history.extend([item.to_input_item() for item in return_agent_result_temp.new_items])

    return_agent_result = {
      "output_text": return_agent_result_temp.final_output_as(str)
    }
    approval_message = "Does this work for you?"

    if approval_request(approval_message):
        end_result = {
          "message": "Your return is on the way."
        }
        return end_result
    else:
        end_result = {
          "message": "What else can I help you with?"
        }
        return end_result
  elif classification_agent_result["output_parsed"]["classification"] == "cancel_subscription":
    retention_agent_result_temp = await Runner.run(
      retention_agent,
      input=[
        *conversation_history
      ],
      run_config=RunConfig(trace_metadata={
        "__trace_source__": "agent-builder",
        "workflow_id": "wf_68e6dd71872481909eb60bccb551c14e088758ac0b559890"
      })
    )

    conversation_history.extend([item.to_input_item() for item in retention_agent_result_temp.new_items])

    retention_agent_result = {
      "output_text": retention_agent_result_temp.final_output_as(str)
    }
  elif classification_agent_result["output_parsed"]["classification"] == "get_information":
    information_agent_result_temp = await Runner.run(
      information_agent,
      input=[
        *conversation_history
      ],
      run_config=RunConfig(trace_metadata={
        "__trace_source__": "agent-builder",
        "workflow_id": "wf_68e6dd71872481909eb60bccb551c14e088758ac0b559890"
      })
    )

    conversation_history.extend([item.to_input_item() for item in information_agent_result_temp.new_items])

    information_agent_result = {
      "output_text": information_agent_result_temp.final_output_as(str)
    }
  else:
    return classification_agent_result


if __name__ == "__main__":
  asyncio.run(run_workflow(WorkflowInput(input_as_text="I want to return my phone")))