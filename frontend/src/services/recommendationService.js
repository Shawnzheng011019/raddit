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
          content: 'This is a sample post to demonstrate the recommendation system.',
          author: 'Admin',
          timestamp: new Date().toISOString()
        },
        {
          id: '2',
          title: 'How to use the recommendation system',
          content: 'The system uses a Two-Tower model for recall and Wide & Deep model for ranking.',
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
  }
};

export default recommendationService;