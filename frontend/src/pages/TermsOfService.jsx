import React from 'react';
import { Link } from 'react-router-dom';
import './TermsOfService.css';

const TermsOfService = () => {
  return (
    <div className="terms-page">
      <div className="terms-container">
        <div className="terms-header">
          <h1>Terms of Service</h1>
          <p className="terms-subtitle">Last updated: April 28, 2026</p>
          <Link to="/register" className="back-to-register">← Back to Registration</Link>
        </div>

        <div className="terms-content">
          <section className="terms-section">
            <h2>1. Acceptance of Terms</h2>
            <p>
              By accessing and using RentHu Uganda ("the Service"), you accept and agree to be bound by the terms and provision of this agreement. 
              If you do not agree to abide by the above, please do not use this service.
            </p>
          </section>

          <section className="terms-section">
            <h2>2. Description of Service</h2>
            <p>
              RentHu Uganda is a real estate rental platform that connects property owners, agents, and tenants in Uganda. 
              Our service includes property listings, reservation management, payment processing, and tenant-landlord communication tools.
            </p>
          </section>

          <section className="terms-section">
            <h2>3. User Accounts</h2>
            <h3>3.1 Registration</h3>
            <p>
              You must provide accurate, current, and complete information as prompted by our registration form. 
              You are responsible for maintaining the confidentiality of your account credentials.
            </p>
            
            <h3>3.2 Account Security</h3>
            <p>
              You are responsible for all activities that occur under your account. You must notify us immediately 
              of any unauthorized use of your account.
            </p>
            
            <h3>3.3 Account Termination</h3>
            <p>
              We reserve the right to suspend or terminate your account for violation of these terms or for any other reason at our discretion.
            </p>
          </section>

          <section className="terms-section">
            <h2>4. Property Listings</h2>
            <h3>4.1 Property Owner Responsibilities</h3>
            <ul>
              <li>Provide accurate and complete property information</li>
              <li>Ensure properties meet legal and safety requirements</li>
              <li>Maintain properties in good condition</li>
              <li>Respond to reservation inquiries promptly</li>
            </ul>
            
            <h3>4.2 Prohibited Listings</h3>
            <ul>
              <li>Properties that violate local laws or regulations</li>
              <li>Misleading or fraudulent property descriptions</li>
              <li>Properties that are unsafe or uninhabitable</li>
              <li>Discriminatory rental practices</li>
            </ul>
          </section>

          <section className="terms-section">
            <h2>5. Reservations and Payments</h2>
            <h3>5.1 Reservation Process</h3>
            <p>
              All reservations must be made through our platform. Direct reservations outside our system are not covered by our protection policies.
            </p>
            
            <h3>5.2 Payment Terms</h3>
            <ul>
              <li>Security deposits are typically 1-2 months' rent</li>
              <li>First month's rent is due before check-in</li>
              <li>Payments are processed through our secure payment system</li>
              <li>Refunds are subject to our cancellation policy</li>
            </ul>
            
            <h3>5.3 Cancellation Policy</h3>
            <ul>
              <li>30+ days before check-in: Full refund</li>
              <li>14-30 days before check-in: 80% refund</li>
              <li>7-14 days before check-in: 50% refund</li>
              <li>Less than 7 days: No refund</li>
            </ul>
          </section>

          <section className="terms-section">
            <h2>6. User Conduct</h2>
            <h3>6.1 Prohibited Activities</h3>
            <ul>
              <li>Using the service for illegal activities</li>
              <li>Harassing, threatening, or abusive behavior</li>
              <li>Posting false or misleading information</li>
              <li>Attempting to gain unauthorized access to our systems</li>
              <li>Violating any applicable laws or regulations</li>
            </ul>
          </section>

          <section className="terms-section">
            <h2>7. Privacy and Data Protection</h2>
            <p>
              Your privacy is important to us. Please review our Privacy Policy to understand how we collect, use, and protect your information. 
              By using our service, you consent to the collection and use of information as described in our Privacy Policy.
            </p>
          </section>

          <section className="terms-section">
            <h2>8. Intellectual Property</h2>
            <p>
              All content, features, and functionality of the Service are owned by RentHu Uganda and are protected by 
              international copyright, trademark, and other intellectual property laws.
            </p>
          </section>

          <section className="terms-section">
            <h2>9. Limitation of Liability</h2>
            <p>
              RentHu Uganda shall not be liable for any indirect, incidental, special, consequential, or punitive damages, 
              including without limitation, loss of profits, data, use, goodwill, or other intangible losses.
            </p>
          </section>

          <section className="terms-section">
            <h2>10. Governing Law</h2>
            <p>
              These terms shall be interpreted and governed by the laws of Uganda. Any disputes arising from these terms 
              shall be resolved in the courts of Uganda.
            </p>
          </section>

          <section className="terms-section">
            <h2>11. Changes to Terms</h2>
            <p>
              We reserve the right to modify these terms at any time. Changes will be effective immediately upon posting. 
              Your continued use of the service constitutes acceptance of any changes.
            </p>
          </section>

          <section className="terms-section">
            <h2>12. Contact Information</h2>
            <p>
              If you have any questions about these Terms of Service, please contact us at:
            </p>
            <div className="contact-info">
              <p><strong>Email:</strong> support@renthu.ug</p>
              <p><strong>Phone:</strong> +256 700 000 000</p>
              <p><strong>Address:</strong> Kampala, Uganda</p>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

export default TermsOfService;
