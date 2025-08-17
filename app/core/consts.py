from enum import Enum


class OrderPaymentMethod(str, Enum):
    cash = "cash"
    card = "card"


# iOS Policy Content
IOS_POLICY = """
#Privacy Policy

**Effective date:** 2025-08-16

This Privacy Policy describes how the Fairy Tales application ("Application", "we", "our", or "us") collects, uses, and protects your information.  
The Application is intended for parents and does not collect any information from or about children.

## 1. Information We Collect
When you sign in to your account, we collect:
- Apple ID identifier (through Apple Sign In authentication)
- Email address (if provided by Apple, optional)
- Name (if provided by Apple, for display purposes only)

Additionally, the Application collects:
- Generated fairy tale stories that you create
- Error reports and technical logs to improve stability
- Usage analytics (e.g., which features are used)

No information about children is collected.

## 2. How We Use Your Information
We use the collected information to:
- Create and maintain your account through Apple Sign In
- Authenticate you securely via Apple's authentication system
- Store and provide access to your generated stories
- Improve the Application through analytics and error reporting
- Process subscription payments through Apple's in-app purchase system

## 3. Generated Stories
When you create a story, it is stored securely on our servers in Google Cloud (Europe).  
Stories are linked only to your account and are not accessible to other users.

## 4. Third-Party Services
We use:
- **Apple Sign In** — for authentication
- **OpenAI API** — to generate stories based on your prompts. No personal information is sent to OpenAI, only the text of your request.
- **Google Cloud** — for data storage and hosting in the EU
- **Crash and analytics tools** — for technical monitoring (without personal data)

We do not share your personal data with advertisers.

## 5. Payments
All subscriptions are processed exclusively through **Apple’s in-app purchase system**.  
We do not store or process your payment information.

## 6. Data Retention and Deletion
- Your account data and generated stories are stored until you request deletion.
- You can request complete deletion of your account and all associated data by contacting us at **gds.grey@gmail.com**.
- Technical logs are stored for a limited time for troubleshooting and then deleted.

## 7. Security
Your authentication is handled securely through Apple's Sign In system - we do not store passwords.  
We use encryption and security best practices to protect your data on our servers.  
However, no system is 100% secure, and we cannot guarantee absolute security.

## 8. Changes to This Policy
We may update this Privacy Policy from time to time.  
You will be notified of significant changes within the Application or via email.

## 9. Contact Us
If you have any questions about privacy or this policy, please contact us:  
**Email:** gds.grey@gmail.com
**Developer:** Siarhei Samoshyn
"""

# Terms of Use Content
TERMS_OF_USE = """
# Terms of Use

**Effective date:** 2025-08-16

These Terms of Use ("Terms") govern your use of the Fairy Tales application ("Application", "we", "our", or "us"). By downloading, accessing, or using the Application, you agree to be bound by these Terms. If you do not agree, please do not use the Application.

## 1. Eligibility
The Application is intended for parents. You must be at least 18 years old to create an account and use the Application.

## 2. Account Registration
To access the Application, you must sign in using Apple Sign In.  
You are responsible for maintaining the security of your Apple ID and for all activities under your account.

## 3. Subscription and Payment
- The Application offers paid subscriptions processed exclusively through **Apple’s in-app purchase system**.
- Subscriptions automatically renew unless canceled at least 24 hours before the end of the current billing period.
- You can manage or cancel your subscription via your Apple ID account settings.
- We do not provide refunds for unused subscription periods unless required by law.

## 4. Generated Content
- You may use the Application to create and store stories.
- Stories you generate are stored on our servers and linked to your account.
- You retain the rights to the stories you create, but grant us a license to store and process them for the purpose of providing the service.

## 5. Acceptable Use
You agree **not to**:
- Use the Application for any illegal or harmful purpose
- Attempt to gain unauthorized access to any part of the Application or its servers
- Use the Application to create or share content that is offensive, discriminatory, or violates laws

We reserve the right to suspend or terminate accounts that violate these rules.

## 6. Third-Party Services
The Application integrates with:
- **Apple Sign In** for authentication
- **OpenAI API** for generating stories (only prompts are sent, no personal data)
- **Google Cloud** for secure hosting in Europe

## 7. Limitation of Liability
The Application is provided “AS IS” without warranties of any kind.  
We are not responsible for any damages resulting from the use or inability to use the Application.

## 8. Changes to These Terms
We may update these Terms from time to time.  
Continued use of the Application after changes means you accept the new Terms.

## 9. Contact Us
If you have questions about these Terms, contact us at:  
**Email:** gds.grey@gmail.com
"""
