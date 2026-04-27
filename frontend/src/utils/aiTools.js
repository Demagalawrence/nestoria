/**
 * AI Assistant Tools for Hostel Booking
 * Uganda-specific tools to help students and people book hostels
 */

import { z } from 'zod';

// Tool schemas for AI assistant
export const aiTools = [
  {
    name: "search_hostels",
    description: "Search for hostels based on location, price, university, or preferences",
    parameters: z.object({
      location: z.string().optional().describe("Location in Uganda (e.g., Kampala, Makerere, Kikoni)"),
      max_price: z.number().optional().describe("Maximum price in UGX"),
      university: z.string().optional().describe("University name (e.g., Makerere, Kyambogo, Bugema)"),
      room_type: z.string().optional().describe("Room type preference (single, shared, apartment)"),
      amenities: z.array(z.string()).optional().describe("Required amenities (WiFi, parking, security, etc.)"),
      gender: z.string().optional().describe("Gender preference (male, female, mixed)"),
      distance_to_university: z.number().optional().describe("Maximum distance to university in km"),
      available_from: z.string().optional().describe("Available from date (YYYY-MM-DD)"),
      duration: z.string().optional().describe("Duration of stay (monthly, semester, yearly)")
    }),
    execute: async (params) => {
      try {
        const response = await fetch('/api/hostels/search/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(params)
        });
        
        if (!response.ok) {
          throw new Error('Failed to search hostels');
        }
        
        const data = await response.json();
        return {
          success: true,
          hostels: data.results || data,
          count: data.count || data.length,
          message: `Found ${data.count || data.length} hostels matching your criteria`
        };
      } catch (error) {
        return {
          success: false,
          error: error.message,
          message: "I couldn't search for hostels right now. Please try again."
        };
      }
    }
  },
  
  {
    name: "get_hostel_details",
    description: "Get detailed information about a specific hostel",
    parameters: z.object({
      hostel_id: z.string().required().describe("Hostel ID to get details for")
    }),
    execute: async (params) => {
      try {
        const response = await fetch(`/api/hostels/${params.hostel_id}/`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (!response.ok) {
          throw new Error('Failed to get hostel details');
        }
        
        const hostel = await response.json();
        return {
          success: true,
          hostel,
          message: `Here are the details for ${hostel.name}`
        };
      } catch (error) {
        return {
          success: false,
          error: error.message,
          message: "I couldn't get the hostel details. Please try again."
        };
      }
    }
  },
  
  {
    name: "check_availability",
    description: "Check if a hostel has rooms available for specific dates",
    parameters: z.object({
      hostel_id: z.string().required().describe("Hostel ID"),
      check_in: z.string().required().describe("Check-in date (YYYY-MM-DD)"),
      check_out: z.string().required().describe("Check-out date (YYYY-MM-DD)"),
      room_type: z.string().optional().describe("Room type preference"),
      guests: z.number().optional().describe("Number of guests")
    }),
    execute: async (params) => {
      try {
        const response = await fetch(`/api/hostels/${params.hostel_id}/availability/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(params)
        });
        
        if (!response.ok) {
          throw new Error('Failed to check availability');
        }
        
        const data = await response.json();
        return {
          success: true,
          available: data.available,
          rooms: data.rooms,
          prices: data.prices,
          message: data.available ? 
            `Rooms are available from ${params.check_in} to ${params.check_out}` :
            `No rooms available for the selected dates`
        };
      } catch (error) {
        return {
          success: false,
          error: error.message,
          message: "I couldn't check availability. Please try again."
        };
      }
    }
  },
  
  {
    name: "calculate_booking_cost",
    description: "Calculate total cost for booking including fees and taxes",
    parameters: z.object({
      hostel_id: z.string().required().describe("Hostel ID"),
      room_type: z.string().required().describe("Room type"),
      check_in: z.string().required().describe("Check-in date (YYYY-MM-DD)"),
      check_out: z.string().required().describe("Check-out date (YYYY-MM-DD)"),
      guests: z.number().optional().describe("Number of guests"),
      payment_method: z.string().optional().describe("Payment method (mobile_money, credit_card, cash)")
    }),
    execute: async (params) => {
      try {
        const response = await fetch('/api/bookings/calculate-cost/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(params)
        });
        
        if (!response.ok) {
          throw new Error('Failed to calculate cost');
        }
        
        const data = await response.json();
        return {
          success: true,
          cost_breakdown: {
            base_price: data.base_price,
            service_fee: data.service_fee,
            cleaning_fee: data.cleaning_fee,
            security_deposit: data.security_deposit,
            total: data.total,
            currency: 'UGX'
          },
          payment_options: data.payment_options,
          message: `Total cost: UGX ${data.total.toLocaleString()}`
        };
      } catch (error) {
        return {
          success: false,
          error: error.message,
          message: "I couldn't calculate the booking cost. Please try again."
        };
      }
    }
  },
  
  {
    name: "create_booking",
    description: "Create a hostel booking reservation",
    parameters: z.object({
      hostel_id: z.string().required().describe("Hostel ID"),
      room_type: z.string().required().describe("Room type"),
      check_in: z.string().required().describe("Check-in date (YYYY-MM-DD)"),
      check_out: z.string().required().describe("Check-out date (YYYY-MM-DD)"),
      guests: z.number().required().describe("Number of guests"),
      guest_info: z.object({
        name: z.string().required().describe("Guest full name"),
        email: z.string().required().describe("Guest email"),
        phone: z.string().required().describe("Guest phone number"),
        university: z.string().optional().describe("University name"),
        student_id: z.string().optional().describe("Student ID number")
      }).required().describe("Guest information"),
      special_requests: z.string().optional().describe("Special requests or preferences")
    }),
    execute: async (params) => {
      try {
        const response = await fetch('/api/bookings/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(params)
        });
        
        if (!response.ok) {
          throw new Error('Failed to create booking');
        }
        
        const booking = await response.json();
        return {
          success: true,
          booking,
          booking_id: booking.id,
          confirmation_code: booking.confirmation_code,
          message: `Booking created successfully! Your confirmation code is ${booking.confirmation_code}`
        };
      } catch (error) {
        return {
          success: false,
          error: error.message,
          message: "I couldn't create the booking. Please check your information and try again."
        };
      }
    }
  },
  
  {
    name: "get_university_info",
    description: "Get information about universities in Uganda and nearby hostels",
    parameters: z.object({
      university: z.string().required().describe("University name")
    }),
    execute: async (params) => {
      const universityData = {
        "makerere": {
          name: "Makerere University",
          location: "Kampala",
          popular_areas: ["Kikoni", "Wandegeya", "Bwaise", "Kasubi"],
          average_hostel_price: 150000,
          student_population: 40000,
          nearby_hostels_count: 156,
          description: "Uganda's premier university with excellent transport links"
        },
        "kyambogo": {
          name: "Kyambogo University",
          location: "Kampala",
          popular_areas: ["Kyambogo", "Banda", "Ntinda"],
          average_hostel_price: 120000,
          student_population: 25000,
          nearby_hostels_count: 89,
          description: "Modern university with growing hostel options"
        },
        "bugema": {
          name: "Bugema University",
          location: "Luweero",
          popular_areas: ["Bugema", "Wobulenzi", "Zirobwe"],
          average_hostel_price: 80000,
          student_population: 8000,
          nearby_hostels_count: 34,
          description: "Peaceful learning environment with affordable hostels"
        },
        "ucu": {
          name: "Uganda Christian University",
          location: "Mukono",
          popular_areas: ["Mukono", "Seeta", "Najjembe"],
          average_hostel_price: 180000,
          student_population: 15000,
          nearby_hostels_count: 67,
          description: "Private university with quality hostel facilities"
        },
        "must": {
          name: "Mbarara University of Science and Technology",
          location: "Mbarara",
          popular_areas: ["Mbarara", "Kakoba", "Ruharo"],
          average_hostel_price: 100000,
          student_population: 12000,
          nearby_hostels_count: 45,
          description: "Leading science university with modern accommodations"
        }
      };
      
      const data = universityData[params.university.toLowerCase()];
      
      if (!data) {
        return {
          success: false,
          error: "University not found",
          message: "I don't have information about that university. Try Makerere, Kyambogo, Bugema, UCU, or MUST."
        };
      }
      
      return {
        success: true,
        university: data,
        message: `Here's information about ${data.name}`
      };
    }
  },
  
  {
    name: "get_area_info",
    description: "Get information about areas and neighborhoods in Uganda",
    parameters: z.object({
      area: z.string().required().describe("Area name in Uganda")
    }),
    execute: async (params) => {
      const areaData = {
        "kikoni": {
          name: "Kikoni",
          location: "Kampala",
          description: "Popular student area near Makerere University",
          advantages: ["Walking distance to Makerere", "Affordable prices", "Many amenities"],
          average_price: 150000,
          transport_options: ["Boda boda", "Taxi", "Walking"],
          security_level: "Good",
          popular_with: "Makerere students"
        },
        "wandegeya": {
          name: "Wandegeya",
          location: "Kampala",
          description: "Vibrant student area with lots of entertainment",
          advantages: ["Great nightlife", "Many restaurants", "Shopping centers"],
          average_price: 180000,
          transport_options: ["Boda boda", "Taxi", "Minibus"],
          security_level: "Good",
          popular_with: "Makerere and Kyambogo students"
        },
        "bwaise": {
          name: "Bwaise",
          location: "Kampala",
          description: "Budget-friendly area with good transport links",
          advantages: ["Very affordable", "Good transport", "Local markets"],
          average_price: 100000,
          transport_options: ["Boda boda", "Taxi", "Minibus"],
          security_level: "Fair",
          popular_with: "Budget-conscious students"
        },
        "mukono": {
          name: "Mukono",
          location: "Mukono District",
          description: "Quiet town home to Uganda Christian University",
          advantages: ["Peaceful environment", "Clean air", "Lower cost of living"],
          average_price: 120000,
          transport_options: ["Taxi", "Private transport"],
          security_level: "Excellent",
          popular_with: "UCU students"
        },
        "mbarara": {
          name: "Mbarara",
          location: "Mbarara District",
          description: "Growing city home to MUST",
          advantages: ["Modern facilities", "Good security", "Affordable living"],
          average_price: 100000,
          transport_options: ["Taxi", "Boda boda", "Minibus"],
          security_level: "Good",
          popular_with: "MUST students"
        }
      };
      
      const data = areaData[params.area.toLowerCase()];
      
      if (!data) {
        return {
          success: false,
          error: "Area not found",
          message: "I don't have information about that area. Try Kikoni, Wandegeya, Bwaise, Mukono, or Mbarara."
        };
      }
      
      return {
        success: true,
        area: data,
        message: `Here's information about ${data.name}`
      };
    }
  },
  
  {
    name: "compare_hostels",
    description: "Compare multiple hostels side by side",
    parameters: z.object({
      hostel_ids: z.array(z.string()).required().describe("Array of hostel IDs to compare"),
      criteria: z.array(z.string()).optional().describe("Comparison criteria (price, location, amenities, etc.)")
    }),
    execute: async (params) => {
      try {
        const response = await fetch('/api/hostels/compare/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(params)
        });
        
        if (!response.ok) {
          throw new Error('Failed to compare hostels');
        }
        
        const comparison = await response.json();
        return {
          success: true,
          comparison,
          message: `Comparing ${params.hostel_ids.length} hostels`
        };
      } catch (error) {
        return {
          success: false,
          error: error.message,
          message: "I couldn't compare the hostels. Please try again."
        };
      }
    }
  },
  
  {
    name: "get_booking_status",
    description: "Check the status of an existing booking",
    parameters: z.object({
      booking_id: z.string().required().describe("Booking ID or confirmation code"),
      phone_number: z.string().optional().describe("Phone number for verification")
    }),
    execute: async (params) => {
      try {
        const response = await fetch(`/api/bookings/${params.booking_id}/status/`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (!response.ok) {
          throw new Error('Failed to get booking status');
        }
        
        const booking = await response.json();
        return {
          success: true,
          booking,
          status: booking.status,
          message: `Your booking is ${booking.status}`
        };
      } catch (error) {
        return {
          success: false,
          error: error.message,
          message: "I couldn't find your booking. Please check your booking ID."
        };
      }
    }
  },
  
  {
    name: "get_payment_methods",
    description: "Get available payment methods for Uganda",
    parameters: z.object({}),
    execute: async () => {
      return {
        success: true,
        payment_methods: [
          {
            name: "Mobile Money",
            providers: [
              { name: "MTN MoMo", code: "MTN_MOMO", ussd: "*165*4#", fee: "2.5% + UGX 500" },
              { name: "Airtel Money", code: "AIRTEL_MONEY", ussd: "*185#", fee: "2.0% + UGX 400" },
              { name: "Stanbic Mobile", code: "STANBIC_MOBILE", ussd: "*290#", fee: "1.5% + UGX 1,000" },
              { name: "Centenary Mobile", code: "CENTENARY_MOBILE", ussd: "*237#", fee: "2.0% + UGX 800" },
              { name: "DFCU Mobile", code: "DFCU_MOBILE", ussd: "*287#", fee: "1.8% + UGX 600" }
            ]
          },
          {
            name: "Credit Cards",
            providers: [
              { name: "Stripe", fee: "2.9% + UGX 1,500", cards: ["Visa", "Mastercard", "Amex"] },
              { name: "Flutterwave", fee: "3.2% + UGX 1,200", cards: ["Visa", "Mastercard", "UnionPay"] },
              { name: "Paystack", fee: "2.5% + UGX 1,000", cards: ["Visa", "Mastercard", "UnionPay"] },
              { name: "DPO Uganda", fee: "3.0% + UGX 800", cards: ["Visa", "Mastercard"] }
            ]
          },
          {
            name: "Cash",
            providers: [
              { name: "Bank Deposit", fee: "UGX 2,000", description: "Direct bank deposit" },
              { name: "Agent Payment", fee: "UGX 1,500", description: "Pay at any RentHu agent" }
            ]
          }
        ],
        message: "Available payment methods in Uganda"
      };
    }
  },
  
  {
    name: "get_booking_tips",
    description: "Get helpful tips for booking hostels in Uganda",
    parameters: z.object({
      topic: z.string().optional().describe("Specific topic (budget, location, safety, etc.)")
    }),
    execute: async (params) => {
      const tips = {
        budget: [
          "Book early to get better prices",
          "Consider shared rooms to save money",
          "Look for hostels slightly further from campus",
          "Check for student discounts",
          "Compare prices across different areas"
        ],
        location: [
          "Consider transport costs when choosing location",
          "Check security ratings of the area",
          "Look for nearby amenities (markets, hospitals)",
          "Consider distance to your university",
          "Check public transport availability"
        ],
        safety: [
          "Choose hostels with good security",
          "Check reviews from other students",
          "Verify the hostel is registered",
          "Know the emergency contacts",
          "Keep your valuables secure"
        ],
        payment: [
          "Use secure payment methods",
          "Get receipts for all payments",
          "Be wary of unusually low prices",
          "Verify the hostel before paying",
          "Use mobile money for small deposits"
        ],
        general: [
          "Read recent reviews from other students",
          "Check photos and virtual tours",
          "Understand the cancellation policy",
          "Know what's included in the price",
          "Keep contact information handy"
        ]
      };
      
      const topicTips = params.topic ? tips[params.topic.toLowerCase()] : tips.general;
      
      return {
        success: true,
        tips: topicTips,
        topic: params.topic || "general",
        message: `Here are some helpful tips for ${params.topic || 'general'} booking`
      };
    }
  }
];

export default aiTools;
