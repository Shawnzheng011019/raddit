import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import recommendationService from '../services/recommendationService';

const PostDetailPage = () => {
  const { id } = useParams();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPost = async () => {
      try {
        // This would normally fetch the post details from the backend
        // For demo, we'll simulate a post
        const mockPost = {
          id,
          title: `Post ${id}`,
          content: `This is the content of post ${id}. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.`,
          author: 'User123',
          timestamp: new Date().toISOString(),
          upvotes: Math.floor(Math.random() * 100),
        };
        setPost(mockPost);
        
        // Record the view event
        await recommendationService.recordUserEvent({
          user_id: '1',
          event_type: 'view',
          post_id: id
        });
      } catch (error) {
        console.error('Error fetching post:', error);
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchPost();
    }
  }, [id]);

  if (loading) {
    return &lt;div className="text-center py-8"&gt;Loading post...&lt;/div&gt;;
  }

  if (!post) {
    return &lt;div className="text-center py-8"&gt;Post not found.&lt;/div&gt;;
  }

  return (
    &lt;div className="max-w-2xl mx-auto"&gt;
      &lt;div className="bg-white rounded-lg shadow-md p-6 mb-6"&gt;
        &lt;h1 className="text-2xl font-bold mb-2"&gt;{post.title}&lt;/h1&gt;
        &lt;div className="flex items-center text-gray-600 mb-4"&gt;
          &lt;span className="mr-4"&gt;By {post.author}&lt;/span&gt;
          &lt;span&gt;{new Date(post.timestamp).toLocaleDateString()}&lt;/span&gt;
        &lt;/div&gt;
        &lt;div className="prose max-w-none mb-6"&gt;
          &lt;p&gt;{post.content}&lt;/p&gt;
        &lt;/div&gt;
        &lt;div className="flex items-center"&gt;
          &lt;button 
            className="flex items-center text-gray-600 hover:text-red-600"
            onClick={async () =&gt; {
              await recommendationService.recordUserEvent({
                user_id: '1',
                event_type: 'upvote',
                post_id: id
              });
            }}
          &gt;
            &lt;svg className="w-5 h-5 mr-1" fill="currentColor" viewBox="0 0 20 20"&gt;
              &lt;path fillRule="evenodd" d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" /&gt;
            &lt;/svg&gt;
            Upvote ({post.upvotes})
          &lt;/button&gt;
        &lt;/div&gt;
      &lt;/div&gt;
    &lt;/div&gt;
  );
};

export default PostDetailPage;