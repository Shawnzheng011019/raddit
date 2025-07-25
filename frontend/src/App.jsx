import { useState, useEffect } from 'react'
import './App.css'
import HomePage from './pages/HomePage'
import PostDetailPage from './pages/PostDetailPage'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'

function App() {
  return (
    &lt;Router&gt;
      &lt;div className="App"&gt;
        &lt;header className="bg-blue-600 text-white p-4"&gt;
          &lt;h1 className="text-2xl font-bold"&gt;Raddit&lt;/h1&gt;
        &lt;/header&gt;
        &lt;main className="container mx-auto p-4"&gt;
          &lt;Routes&gt;
            &lt;Route path="/" element={&lt;HomePage /&gt;} /&gt;
            &lt;Route path="/post/:id" element={&lt;PostDetailPage /&gt;} /&gt;
          &lt;/Routes&gt;
        &lt;/main&gt;
      &lt;/div&gt;
    &lt;/Router&gt;
  )
}

export default App