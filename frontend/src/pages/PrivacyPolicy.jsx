import React from 'react';
import { Link } from 'react-router-dom';
import './PrivacyPolicy.css';

const PrivacyPolicy = () => {
  return (
    <div className="privacy-page">
      <div className="privacy-container">
        <div className="privacy-header">
          <h1>Privacy Policy</h1>
          <p className="privacy-subtitle">Last updated: April 28, 2026</p>
          <Link to="/register" className="back-to-register">← Back to Registration</Link>
        </div>

        <div className="privacy-content">
          <section className="privacy-section">
            <h2>1. Information We Collect</h2>
            <h3>1.1 Personal Information</h3>
            <p>When you register or use our service, we may collect:</p>
            <ul>
              <li><strong>Name and contact information:</strong> Full name, email address, phone number</li>
              <li><strong>Account credentials:</strong> Username and password</li>
              <li><strong>Demographic information:</strong> Age, location preferences</li>
              <li><strong>Government ID:</strong> For identity verification purposes</li>
            </ul>

            <h3>1.2 Property Information</h3>
            <p>For property owners and agents:</p>
            <ul>
              <li>Property details and descriptions</li>
              <li>Property images and videos</li>
              <li>Pricing and availability information</li>
              <li>Location data</li>
            </ul>

            <h3>1.3 Usage Information</h3>
            <p>We automatically collect:</p>
            <ul>
              <li>IP address and device information</li>
              <li>Browser type and operating system</li>
              <li>Pages visited and time spent</li>
              <li>Search queries and filters used</li>
              <li>Reservation and payment history</li>
            </ul>
          </section>

          <section className="privacy-section">
            <h2>2. How We Use Your Information</h2>
            <h3>2.1 Service Provision</h3>
            <ul>
              <li>To create and manage your account</li>
              <li>To process reservations and payments</li>
              <li>To connect you with properties and tenants</li>
              <li>To provide customer support</li>
            </ul>

            <h3>2.2 Communication</h3>
            <ul>
              <li>To send reservation confirmations and updates</li>
              <li>To respond to your inquiries</li>
              <li>To send important service announcements</li>
              <li>To provide marketing communications (with consent)</li>
            </ul>

            <h3>2.3 Service Improvement</h3>
            <ul>
              <li>To analyze usage patterns and improve our platform</li>
              <li>To personalize your experience</li>
              <li>To prevent fraud and ensure security</li>
              <li>To comply with legal obligations</li>
            </ul>
          </section>

          <section className="privacy-section">
            <h2>3. Information Sharing</h2>
            <h3>3.1 When We Share Information</h3>
            <p>We may share your information in the following circumstances:</p>
            <ul>
              <li><strong>With other users:</strong> When you engage in transactions or communications</li>
              <li><strong>Property owners/agents:</strong> Your reservation details and contact information</li>
              <li><strong>Service providers:</strong> Payment processors, verification services</li>
              <li><strong>Legal requirements:</strong> When required by law or court order</li>
              <li><strong>Business transfers:</strong> In case of merger, acquisition, or sale</li>
            </ul>

            <h3>3.2 What We Don't Share</h3>
            <ul>
              <li>We never sell your personal information to third parties</li>
              <li>We don't share your data for advertising without consent</li>
              <li>We don't share more information than necessary for transactions</li>
            </ul>
          </section>

          <section className="privacy-section">
            <h2>4. Data Security</h2>
            <p>We implement appropriate security measures to protect your information:</p>
            <ul>
              <li><strong>Encryption:</strong> SSL/TLS encryption for data transmission</li>
              <li><strong>Access controls:</strong> Limited access to personal data</li>
              <li><strong>Regular audits:</strong> Security assessments and updates</li>
              <li><strong>Secure storage:</strong> Protected databases and servers</li>
            </ul>
            <p>However, no method of transmission over the internet is 100% secure.</p>
          </section>

          <section className="privacy-section">
            <h2>5. Cookies and Tracking</h2>
            <h3>5.1 Cookies</h3>
            <p>We use cookies to:</p>
            <ul>
              <li>Keep you logged in</li>
              <li>Remember your preferences</li>
              <li>Analyze website traffic</li>
              <li>Personalize content</li>
            </ul>

            <h3>5.2 Google reCAPTCHA</h3>
            <p>
              We use Google reCAPTCHA to protect against spam and abuse. This service may collect 
              your IP address and other device information. See Google's Privacy Policy for details.
            </p>
          </section>

          <section className="privacy-section">
            <h2>6. Your Rights</h2>
            <h3>6.1 Access and Correction</h3>
            <p>You have the right to:</p>
            <ul>
              <li>Access your personal information</li>
              <li>Correct inaccurate information</li>
              <li>Request deletion of your account</li>
              <li>Export your data</li>
            </ul>

            <h3>6.2 Marketing Preferences</h3>
            <p>You can:</p>
            <ul>
              <li>Opt out of marketing emails</li>
              <li>Unsubscribe from SMS notifications</li>
              <li>Manage notification preferences</li>
            </ul>
          </section>

          <section className="privacy-section">
            <h2>7. Data Retention</h2>
            <p>We retain your information for as long as necessary to:</p>
            <ul>
              <li>Fulfill the purposes for which it was collected</li>
              <li>Comply with legal obligations</li>
              <li>Resolve disputes and enforce agreements</li>
              <li>Fulfill legitimate business interests</li>
            </ul>
          </section>

          <section className="privacy-section">
            <h2>8. Children's Privacy</h2>
            <p>
              Our service is not intended for children under 18. We do not knowingly collect 
              personal information from children under 18. If we become aware of such collection, 
              we will take steps to delete the information.
            </p>
          </section>

          <section className="privacy-section">
            <h2>9. International Data Transfers</h2>
            <p>
              Your information may be transferred to and processed in countries other than Uganda. 
              We ensure appropriate safeguards are in place for international data transfers.
            </p>
          </section>

          <section className="privacy-section">
            <h2>10. Changes to This Policy</h2>
            <p>
              We may update this Privacy Policy from time to time. We will notify you of 
              any changes by posting the new policy on this page and updating the "Last updated" date.
            </p>
          </section>

          <section className="privacy-section">
            <h2>11. Contact Us</h2>
            <p>
              If you have any questions about this Privacy Policy or want to exercise your rights, please contact us:
            </p>
            <div className="contact-info">
              <p><strong>Email:</strong> privacy@renthu.ug</p>
              <p><strong>Phone:</strong> +256 700 000 000</p>
              <p><strong>Address:</strong> Kampala, Uganda</p>
              <p><strong>Attn:</strong> Data Protection Officer</p>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPolicy;
