// services/recommendationService.js
import axios from 'axios';

const API_BASE_URL = '/api';

const recommendationService = {
  // Get home page recommendations
  async getHomeRecommendations(userId) {
    try {
      const response = await axios.get(`${API_BASE_URL}/recommend/home`, {
        params: { user_id: userId }
      });
      return response.data.posts || [];
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      // Return mock data for demo purposes
      return [
        {
          id: '1',
          title: 'Welcome to Raddit!',
          content: 'This is a sample post to demonstrate the interest-based recommendation system.',
          author: 'Admin',
          timestamp: new Date().toISOString(),
          primary_interest: {
            id: 1,
            name: 'Technology',
            category: 'Technology'
          },
          relevance_score: 0.9
        },
        {
          id: '2',
          title: 'How to use the recommendation system',
          content: 'The system now uses your selected interests to provide personalized content.',
          author: 'Admin',
          timestamp: new Date().toISOString(),
          primary_interest: {
            id: 2,
            name: 'AI & Machine Learning',
            category: 'Technology'
          },
          relevance_score: 0.8
        }
      ];
    }
  },

  // Get initial recommendations for new users
  async getInitialRecommendations(userId) {
    try {
      const response = await axios.get(`${API_BASE_URL}/recommend/initial`, {
        params: { user_id: userId }
      });
      return response.data.posts || [];
    } catch (error) {
      console.error('Error fetching initial recommendations:', error);
      return this.getHomeRecommendations(userId);
    }
  },

  // Get popular recommendations as fallback
  async getPopularRecommendations(limit = 20) {
    try {
      const response = await axios.get(`${API_BASE_URL}/recommend/popular`, {
        params: { limit }
      });
      return response.data.posts || [];
    } catch (error) {
      console.error('Error fetching popular recommendations:', error);
      return [
        {
          id: '1',
          title: 'Popular Post 1',
          content: 'This is a popular post that everyone might like.',
          author: 'Admin',
          timestamp: new Date().toISOString()
        }
      ];
    }
  },

  // Record user event (click, view, upvote, etc.)
  async recordUserEvent(eventData) {
    try {
      await axios.post(`${API_BASE_URL}/user/event`, eventData);
    } catch (error) {
      console.error('Error recording user event:', error);
    }
  },

  // Get user interests
  async getUserInterests(userId) {
    try {
      const response = await axios.get(`${API_BASE_URL}/auth/user/${userId}/interests`);
      return response.data;
    } catch (error) {
      console.error('Error fetching user interests:', error);
      return [];
    }
  },

  // Get all available interests
  async getAllInterests() {
    try {
      const response = await axios.get(`${API_BASE_URL}/auth/interests`);
      return response.data;
    } catch (error) {
      console.error('Error fetching interests:', error);
      return [];
    }
  }
};

export default recommendationService;