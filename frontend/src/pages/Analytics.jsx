import React, { useState, useEffect } from 'react';
import { TrendingUp, DollarSign, Home, Users, Calendar, Eye, Star, Filter, Download, BarChart3, PieChartIcon } from 'lucide-react';
import api from '../api/axios';
import './Analytics.css';

const Analytics = () => {
  const [analyticsData, setAnalyticsData] = useState({
    overview: {
      total_properties: 0,
      total_bookings: 0,
      total_revenue: 0,
      occupancy_rate: 0,
      average_rating: 0,
      total_views: 0
    },
    revenueData: [],
    bookingData: [],
    propertyPerformance: [],
    topProperties: [],
    recentActivity: []
  });
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30');
  const [activeChart, setActiveChart] = useState('revenue');

  useEffect(() => {
    fetchAnalyticsData();
  }, [timeRange]);

  const fetchAnalyticsData = async () => {
    try {
      const res = await api.get(`/analytics/dashboard/?time_range=${timeRange}`);
      setAnalyticsData(res.data);
    } catch (error) {
      console.error('Error fetching analytics data:', error);
      // Mock data for demonstration
      setAnalyticsData({
        overview: {
          total_properties: 5,
          total_bookings: 47,
          total_revenue: 45850,
          occupancy_rate: 78,
          average_rating: 4.6,
          total_views: 1234
        },
        revenueData: [
          { date: 'Jan', revenue: 3200, bookings: 12 },
          { date: 'Feb', revenue: 4100, bookings: 15 },
          { date: 'Mar', revenue: 3800, bookings: 14 },
          { date: 'Apr', revenue: 5200, bookings: 18 },
          { date: 'May', revenue: 4900, bookings: 17 },
          { date: 'Jun', revenue: 6100, bookings: 21 }
        ],
        bookingData: [
          { date: 'Week 1', bookings: 8, cancellations: 1 },
          { date: 'Week 2', bookings: 12, cancellations: 2 },
          { date: 'Week 3', bookings: 15, cancellations: 1 },
          { date: 'Week 4', bookings: 12, cancellations: 0 }
        ],
        propertyPerformance: [
          { name: 'Ocean Breeze Villa', occupancy: 85, revenue: 12400, rating: 4.8 },
          { name: 'Mountain View Cabin', occupancy: 72, revenue: 9800, rating: 4.6 },
          { name: 'City Center Studio', occupancy: 91, revenue: 8900, rating: 4.9 },
          { name: 'Lake House Retreat', occupancy: 68, revenue: 7600, rating: 4.4 },
          { name: 'Garden Cottage', occupancy: 79, revenue: 7150, rating: 4.7 }
        ],
        topProperties: [
          { name: 'Ocean Breeze Villa', views: 456, bookings: 21, revenue: 12400 },
          { name: 'City Center Studio', views: 389, bookings: 18, revenue: 8900 },
          { name: 'Mountain View Cabin', views: 234, bookings: 15, revenue: 9800 }
        ],
        recentActivity: [
          { type: 'booking', property: 'Ocean Breeze Villa', guest: 'John Doe', amount: 1200, time: '2 hours ago' },
          { type: 'review', property: 'City Center Studio', guest: 'Jane Smith', rating: 5, time: '4 hours ago' },
          { type: 'booking', property: 'Mountain View Cabin', guest: 'Mike Johnson', amount: 980, time: '6 hours ago' },
          { type: 'view', property: 'Lake House Retreat', guest: 'Sarah Wilson', time: '8 hours ago' }
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  const exportData = () => {
    // In a real implementation, this would generate and download a CSV/Excel report
    alert('Analytics report would be downloaded here');
  };

  const COLORS = ['#667eea', '#764ba2', '#f59e0b', '#10b981', '#ef4444'];

  if (loading) {
    return (
      <div className="analytics-container">
        <div className="loader">Loading analytics data...</div>
      </div>
    );
  }

  const { overview, topProperties, recentActivity } = analyticsData;

  return (
    <div className="analytics-container">
      <div className="analytics-header">
        <div className="header-content">
          <h1>Analytics Dashboard</h1>
          <p>Track your property performance and business metrics</p>
        </div>
        <div className="header-actions">
          <select value={timeRange} onChange={(e) => setTimeRange(e.target.value)} className="time-range-select">
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 3 months</option>
            <option value="365">Last year</option>
          </select>
          <button className="btn-secondary" onClick={exportData}>
            <Download /> Export Report
          </button>
        </div>
      </div>

      <div className="overview-cards">
        <div className="stat-card">
          <div className="stat-icon">
            <Home />
          </div>
          <div className="stat-content">
            <h3>{overview.total_properties}</h3>
            <p>Total Properties</p>
            <span className="stat-change positive">+2 this month</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <Calendar />
          </div>
          <div className="stat-content">
            <h3>{overview.total_bookings}</h3>
            <p>Total Bookings</p>
            <span className="stat-change positive">+15% vs last period</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <DollarSign />
          </div>
          <div className="stat-content">
            <h3>${overview.total_revenue.toLocaleString()}</h3>
            <p>Total Revenue</p>
            <span className="stat-change positive">+23% vs last period</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <Users />
          </div>
          <div className="stat-content">
            <h3>{overview.occupancy_rate}%</h3>
            <p>Occupancy Rate</p>
            <span className="stat-change neutral">Same as last period</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <Star />
          </div>
          <div className="stat-content">
            <h3>{overview.average_rating}</h3>
            <p>Average Rating</p>
            <span className="stat-change positive">+0.2 vs last period</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <Eye />
          </div>
          <div className="stat-content">
            <h3>{overview.total_views.toLocaleString()}</h3>
            <p>Total Views</p>
            <span className="stat-change positive">+45% vs last period</span>
          </div>
        </div>
      </div>

      <div className="charts-section">
        <div className="chart-controls">
          <div className="chart-tabs">
            <button
              className={`chart-tab ${activeChart === 'revenue' ? 'active' : ''}`}
              onClick={() => setActiveChart('revenue')}
            >
              <BarChart3 size={16} /> Revenue Trends
            </button>
            <button
              className={`chart-tab ${activeChart === 'bookings' ? 'active' : ''}`}
              onClick={() => setActiveChart('bookings')}
            >
              <TrendingUp size={16} /> Booking Analytics
            </button>
            <button
              className={`chart-tab ${activeChart === 'performance' ? 'active' : ''}`}
              onClick={() => setActiveChart('performance')}
            >
              <PieChartIcon size={16} /> Property Performance
            </button>
          </div>
        </div>

        <div className="charts-grid">
          {activeChart === 'revenue' && (
            <>
              <div className="chart-card">
                <h3>Revenue Overview</h3>
                <div className="chart-placeholder">
                  <BarChart3 size={48} />
                  <p>Revenue chart visualization</p>
                  <small>Charts will be displayed when recharts library is installed</small>
                </div>
              </div>
              <div className="chart-card">
                <h3>Bookings vs Revenue</h3>
                <div className="chart-placeholder">
                  <TrendingUp size={48} />
                  <p>Booking analytics chart</p>
                  <small>Charts will be displayed when recharts library is installed</small>
                </div>
              </div>
            </>
          )}

          {activeChart === 'bookings' && (
            <>
              <div className="chart-card">
                <h3>Weekly Booking Trends</h3>
                <div className="chart-placeholder">
                  <Calendar size={48} />
                  <p>Weekly booking trends</p>
                  <small>Charts will be displayed when recharts library is installed</small>
                </div>
              </div>
              <div className="chart-card">
                <h3>Occupancy Rate</h3>
                <div className="occupancy-metrics">
                  <div className="occupancy-item">
                    <div className="occupancy-label">Current Occupancy</div>
                    <div className="occupancy-value">{overview.occupancy_rate}%</div>
                    <div className="occupancy-bar">
                      <div className="occupancy-fill" style={{ width: `${overview.occupancy_rate}%` }}></div>
                    </div>
                  </div>
                  <div className="occupancy-stats">
                    <div className="stat">
                      <span>Available Days</span>
                      <strong>23</strong>
                    </div>
                    <div className="stat">
                      <span>Booked Days</span>
                      <strong>89</strong>
                    </div>
                    <div className="stat">
                      <span>Blocked Days</span>
                      <strong>5</strong>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}

          {activeChart === 'performance' && (
            <>
              <div className="chart-card">
                <h3>Property Performance</h3>
                <div className="chart-placeholder">
                  <BarChart3 size={48} />
                  <p>Property performance comparison</p>
                  <small>Charts will be displayed when recharts library is installed</small>
                </div>
              </div>
              <div className="chart-card">
                <h3>Revenue Distribution</h3>
                <div className="chart-placeholder">
                  <PieChartIcon size={48} />
                  <p>Revenue distribution by property</p>
                  <small>Charts will be displayed when recharts library is installed</small>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      <div className="analytics-grid">
        <div className="top-properties">
          <h3>Top Performing Properties</h3>
          <div className="properties-list">
            {topProperties.map((property, index) => (
              <div key={index} className="property-item">
                <div className="property-rank">{index + 1}</div>
                <div className="property-info">
                  <h4>{property.name}</h4>
                  <div className="property-stats">
                    <span><Eye size={14} /> {property.views} views</span>
                    <span><Calendar size={14} /> {property.bookings} bookings</span>
                  </div>
                </div>
                <div className="property-revenue">
                  <strong>${property.revenue.toLocaleString()}</strong>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="recent-activity">
          <h3>Recent Activity</h3>
          <div className="activity-list">
            {recentActivity.map((activity, index) => (
              <div key={index} className="activity-item">
                <div className={`activity-icon ${activity.type}`}>
                  {activity.type === 'booking' && <Calendar size={16} />}
                  {activity.type === 'review' && <Star size={16} />}
                  {activity.type === 'view' && <Eye size={16} />}
                </div>
                <div className="activity-content">
                  <p>
                    <strong>{activity.guest}</strong>
                    {activity.type === 'booking' && ` booked ${activity.property} for $${activity.amount}`}
                    {activity.type === 'review' && ` left a ${activity.rating}-star review for ${activity.property}`}
                    {activity.type === 'view' && ` viewed ${activity.property}`}
                  </p>
                  <span className="activity-time">{activity.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
