<!-- BEGIN AWS Agent Toolkit rules -->
# AWS Guidance for the new AWS experience

This user has signed up for the new AWS experience. This experience lets you sign into AWS using a social provider and requires the following additional context.

Where this guidance conflicts with the project's own instructions, the project's instructions take precedence.

## Context

### Terminology

- Say "project" instead of "account" — a project contains an AWS account and settings for sharing with other collaborators.
- Say "team member" instead of "IAM user" — users are invited by email, not created or federated in IAM.
- Say "AWS Settings" when referring to management tasks at https://settings.aws.com/ (project management, billing, team members, spend limits). Users view their actual AWS resources in the AWS Management Console.
- Say "selected Region" when referring to the user's Region — not "home Region".
- The user has a managed IAM experience. This includes managed service control policies (SCPs) and resource control policies (RCPs) that govern AWS usage. They still need IAM policies to let services work with each other. For questions about SCPs or RCPs, see https://docs.aws.amazon.com/accounts/latest/reference/scps-and-rcps-for-projects.html.

### Constraints

- All projects share a single AWS Region determined by the user's contact address. Resources cannot be created in other Regions.
- Create all Regional resources in the project's assigned Region.
- AWS WAF and CloudWatch Logs resources may be created in `us-east-1` only when a global resource requires a connection to them. Do not use `us-east-1` for other reasons.
- For resource inventory, check both the selected Region and `us-east-1` for CloudWatch Logs or WAF resources.
- Do not create Lambda, API Gateway, or other Regional resources outside the project Region.
- Direct users to confirm their Region in AWS Settings > View all projects > Overview > Additional Info > Region. If unavailable, check `~/.aws/config`.
- Do not use Lambda@Edge, CloudFormation StackSets, cross-Region actions, cross-Region replication, multi-Region KMS keys, or Route 53 cross-Region routing.
- CloudFront is global and may be created in `us-east-1`, pointing to a project-Region Lambda function URL or API Gateway. Lambda and API Gateway must remain in the project Region.
- Do not assign roles to team members unless absolutely necessary.
- If resources become inaccessible, ask whether a spend limit is configured. Direct spend-status checks to AWS Settings > Billing.
- Before starting a task, check whether a relevant AWS skill is available. Load the skill with `retrieve_skill` and prefer its guidance.

### Help level

Ask the user: "How much guidance would you like from me? Low (I only flag security risks), medium (I ask a couple of clarifying questions if something seems off), or high (I explain what I'm doing, suggest alternatives, and flag best practices)."

Current help level: **HIGH**.

- **LOW:** Follow constraints, execute the request, and only ask questions for security vulnerabilities.
- **MEDIUM:** Execute the request and ask up to two clarifying questions for ambiguity or potential issues.
- **HIGH:** Explain each step before executing, suggest alternatives, and flag best practices while still executing the user's choice.
<!-- END AWS Agent Toolkit rules -->
