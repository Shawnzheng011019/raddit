import React, { useState, useEffect } from 'react';
import PostCard from '../components/PostCard';
import recommendationService from '../services/recommendationService';

const HomePage = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRecommendedPosts = async () => {
      try {
        // For demo purposes, we'll use a default user ID
        const userId = '1';
        const recommendedPosts = await recommendationService.getHomeRecommendations(userId);
        setPosts(recommendedPosts);
      } catch (error) {
        console.error('Error fetching recommended posts:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendedPosts();
  }, []);

  if (loading) {
    return &lt;div className="text-center py-8"&gt;Loading posts...&lt;/div&gt;;
  }

  return (
    &lt;div className="space-y-4"&gt;
      &lt;h2 className="text-xl font-bold mb-4"&gt;Recommended Posts&lt;/h2&gt;
      {posts.length === 0 ? (
        &lt;div className="text-center py-8"&gt;
          &lt;p&gt;No posts found. Try again later.&lt;/p&gt;
        &lt;/div&gt;
      ) : (
        posts.map((post) =&gt; (
          &lt;PostCard key={post.id} post={post} /&gt;
        ))
      )}
    &lt;/div&gt;
  );
};

export default HomePage;