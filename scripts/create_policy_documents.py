from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
POLICY_DIR = BASE_DIR / "rag" / "policy_documents"
POLICY_DIR.mkdir(parents=True, exist_ok=True)


POLICIES = {
    "aml_escalation_policy.md": """# AML Escalation Policy

## Purpose
This policy defines when suspicious financial activity must be escalated to the AML review team.

## Suspicious Patterns
Transactions may require AML review when they show one or more of the following patterns:
- Multiple high-value transactions within a short period.
- Repeated transfers just below internal review thresholds.
- Activity involving high-risk merchant categories.
- Sudden increase in transaction volume compared with customer history.
- Cross-border transactions inconsistent with the customer's normal behaviour.
- Transactions involving unknown or unclear merchant information.

## High-Risk Merchant Categories
The following merchant categories require additional monitoring:
- CRYPTO
- GAMING
- UNKNOWN
- CASH_WITHDRAWAL
- ONLINE_MARKETPLACE

## Escalation Thresholds
A transaction should be escalated when:
- The amount is greater than 2,500 EUR or equivalent and the customer risk rating is HIGH.
- Three or more suspicious transactions occur within seven days.
- The customer has failed or expired KYC and performs high-value activity.
- The transaction involves a high-risk merchant category and unusual location.

## AML Review Criteria
Send the case to AML review when:
- Transaction behaviour cannot be explained by customer profile.
- Source of funds appears unclear.
- Customer activity is inconsistent with account age or income indicators.
- The case includes repeated suspicious indicators across multiple channels.

## Human Review Requirement
Automated systems may flag suspicious behaviour, but final AML escalation decisions must be reviewed by a trained analyst.
""",

    "chargeback_policy.md": """# Chargeback Policy

## Purpose
This policy explains how customer transaction disputes and chargeback requests should be assessed.

## Eligible Dispute Reasons
A customer may raise a chargeback request when:
- Goods or services were not received.
- The transaction was not authorised by the customer.
- The merchant charged the customer twice.
- The amount charged differs from the agreed amount.
- The refund was promised but not received.

## Time Limits
Chargeback requests should generally be raised within 120 days of the transaction date unless card scheme rules allow a longer period.

## Evidence Required
The customer should provide:
- Transaction reference.
- Explanation of dispute.
- Merchant communication if available.
- Receipt, invoice, or order confirmation.
- Proof of attempted resolution with merchant.

## Provisional Refund Conditions
A provisional refund may be considered when:
- The customer has a strong dispute reason.
- Evidence supports unauthorised activity.
- The merchant has not responded within the required timeframe.
- The customer is vulnerable or financially impacted.

## Rejection Conditions
A chargeback may be rejected when:
- The customer authorised the transaction.
- The dispute is outside the allowed time limit.
- The merchant provides valid fulfilment evidence.
- The customer has insufficient evidence.
- The issue is a product dissatisfaction matter not covered by dispute rules.

## Human Review Requirement
High-value disputes and vulnerable customer cases must be reviewed by a human analyst before final decision.
""",

    "kyc_review_policy.md": """# KYC Review Policy

## Purpose
This policy defines how customer identity verification issues should be reviewed.

## Required Documents
Acceptable KYC documents may include:
- Passport.
- National identity card.
- Driving licence.
- Proof of address.
- Bank statement or utility bill.
- Business registration document for SME customers.

## Expired KYC Process
If a customer's KYC has expired:
- Restrict high-risk transactions if required.
- Request updated documents.
- Notify the customer clearly.
- Allow a reasonable submission window.
- Escalate if the customer continues high-risk activity.

## Failed Verification Handling
If verification fails:
- Check document quality and expiry date.
- Compare customer details with submitted documents.
- Request resubmission if the failure appears accidental.
- Escalate if fraud indicators are present.
- Restrict account access if identity risk is high.

## High-Risk Customer Treatment
High-risk customers require enhanced due diligence when:
- They transact with high-risk merchants.
- Their behaviour changes suddenly.
- Their documents fail validation.
- They perform large cross-border transactions.

## Manual Review Requirement
KYC failures should not be rejected automatically when document quality, name mismatch, or address mismatch may have a reasonable explanation.
""",

    "fraud_investigation_policy.md": """# Fraud Investigation Policy

## Purpose
This policy defines when suspicious account or transaction behaviour should be investigated by the fraud team.

## New Device Login Rules
A new device login may require review when:
- It is followed by a high-value transaction.
- It occurs from a new country or unusual location.
- It is followed by password reset or contact detail changes.
- The device has not been used before by the customer.

## Failed Login Attempts
Escalate when:
- There are five or more failed login attempts within one hour.
- Failed attempts are followed by a successful login from a new device.
- Failed attempts occur across multiple locations.
- Account recovery is triggered repeatedly.

## Suspicious Transactions
Fraud investigation is required when:
- A transaction is high-value and unusual for the customer.
- The transaction uses a new device or new location.
- The merchant category is high-risk.
- Several transactions are attempted in a short time.
- The customer reports the activity as unauthorised.

## Account Freeze Conditions
Temporarily freeze the account when:
- Account takeover is strongly suspected.
- Customer funds are at immediate risk.
- Multiple fraud indicators are present.
- The customer confirms unauthorised access.
- Regulatory or compliance rules require immediate action.

## Fraud Team Escalation
Escalate to fraud team when automated checks cannot confidently resolve the case.
""",

    "complaint_sla_policy.md": """# Complaint SLA Policy

## Purpose
This policy defines response and resolution expectations for customer complaints.

## Complaint Priority
Complaint priority should be assigned as:
- LOW: General dissatisfaction or minor service issue.
- MEDIUM: Financial inconvenience or repeated service failure.
- HIGH: Customer financial loss, regulatory issue, or unresolved dispute.
- CRITICAL: Vulnerable customer, fraud impact, severe financial harm, or legal escalation.

## Response Times
Initial response targets:
- LOW: Within 3 business days.
- MEDIUM: Within 2 business days.
- HIGH: Within 1 business day.
- CRITICAL: Same business day.

## Escalation Timeframes
Escalate when:
- A high-priority complaint remains unresolved after 2 business days.
- A customer reports financial distress.
- The complaint involves fraud, AML, KYC, or chargeback failure.
- The same complaint is reopened multiple times.

## Vulnerable Customer Handling
When vulnerability is identified:
- Use careful and clear communication.
- Avoid unnecessary technical language.
- Offer human support.
- Prioritise resolution.
- Document support actions clearly.

## Final Response
Final responses must explain the decision, evidence considered, next steps, and appeal route where applicable.
""",

    "vulnerable_customer_policy.md": """# Vulnerable Customer Policy

## Purpose
This policy explains how customers showing signs of vulnerability should be supported.

## Signs of Vulnerability
A customer may be vulnerable when they show:
- Financial distress.
- Confusion about transactions.
- Difficulty understanding decisions.
- Health, age, disability, or personal crisis indicators.
- Repeated complaints or urgent support requests.
- Signs of coercion or third-party control.

## Communication Rules
When dealing with vulnerable customers:
- Use simple, respectful language.
- Avoid pressure.
- Give the customer time to respond.
- Confirm understanding.
- Offer alternative communication channels.
- Avoid unnecessary repetition of sensitive questions.

## Human Escalation
Escalate to a human specialist when:
- The customer appears distressed.
- The issue involves fraud or financial loss.
- The customer cannot complete digital steps.
- The case requires judgement beyond automated rules.

## Support-First Handling
The priority is to protect the customer from harm while still following compliance and risk controls.

## Documentation
Record vulnerability indicators carefully without making unsupported medical or personal assumptions.
""",

    "account_takeover_policy.md": """# Account Takeover Policy

## Purpose
This policy defines how possible account takeover activity should be identified and handled.

## Account Takeover Indicators
Possible account takeover indicators include:
- Login from a new device.
- Login from an unusual location.
- Password reset followed by transaction activity.
- Email or phone number change before payment attempt.
- Multiple failed login attempts.
- Customer reports loss of account access.

## Device and Location Anomalies
Flag activity when:
- A customer logs in from a new country.
- Device fingerprint is unknown.
- IP address is inconsistent with usual customer behaviour.
- A new device is used for a high-value transaction.

## Password Reset Risk
Password reset should be treated as high risk when:
- It occurs shortly before a large transaction.
- It is combined with contact detail changes.
- The customer has recent failed login attempts.
- The account has high balance or high transaction limits.

## Urgent Account Lock Rules
Lock or restrict the account when:
- Customer confirms unauthorised access.
- High-value transaction is attempted from a new device.
- Multiple takeover indicators appear together.
- Fraud team requests immediate restriction.

## Review Requirement
Account locks must be reviewed promptly to avoid unnecessary customer harm.
""",

    "refund_decision_policy.md": """# Refund Decision Policy

## Purpose
This policy defines when refunds can be approved, rejected, or sent for further review.

## Refund Approval Conditions
A refund may be approved when:
- The customer was charged incorrectly.
- The merchant confirms non-delivery.
- Duplicate payment is confirmed.
- The transaction failed but funds were debited.
- Fraud investigation supports customer claim.

## Refund Rejection Conditions
A refund may be rejected when:
- The customer authorised the transaction.
- Merchant evidence proves fulfilment.
- The claim is outside allowed policy timeframe.
- The customer has already received refund or chargeback.
- Evidence is insufficient and no risk indicators are present.

## More Evidence Required
Request more evidence when:
- Customer explanation is unclear.
- Merchant response is missing.
- Transaction status does not match customer claim.
- There are conflicting system records.
- The amount or merchant cannot be verified.

## Human Review Rules
Human review is required when:
- Refund amount is high.
- Customer is vulnerable.
- Fraud or account takeover is suspected.
- AML or KYC concerns are linked to the transaction.
- Automated decision confidence is low.

## Decision Logging
Every refund decision must include reason, evidence, reviewer, and final outcome.
""",
}


def main() -> None:
    for filename, content in POLICIES.items():
        path = POLICY_DIR / filename
        path.write_text(content.strip() + "\n", encoding="utf-8")
        print(f"Created: {path}")

    print(f"\nPolicy document creation complete. Total files: {len(POLICIES)}")


if __name__ == "__main__":
    main()