import React from 'react';
import { Link } from 'react-router-dom';

const PostCard = ({ post }) =&gt; {
  const handlePostClick = async () =&gt; {
    // Record click event when user clicks on a post
    try {
      const response = await fetch('/api/user/event', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: '1',
          event_type: 'click',
          post_id: post.id
        })
      });
    } catch (error) {
      console.error('Error recording click event:', error);
    }
  };

  return (
    &lt;Link to={`/post/${post.id}`} onClick={handlePostClick}&gt;
      &lt;div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer"&gt;
        &lt;h3 className="text-xl font-bold mb-2"&gt;{post.title}&lt;/h3&gt;
        &lt;p className="text-gray-700 mb-4"&gt;
          {post.content.length &gt; 150 ? `${post.content.substring(0, 150)}...` : post.content}
        &lt;/p&gt;
        &lt;div className="flex items-center text-gray-600"&gt;
          &lt;span className="mr-4"&gt;By {post.author}&lt;/span&gt;
          &lt;span&gt;{new Date(post.timestamp).toLocaleDateString()}&lt;/span&gt;
        &lt;/div&gt;
      &lt;/div&gt;
    &lt;/Link&gt;
  );
};

export default PostCard;