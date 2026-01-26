import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route, useParams } from 'react-router-dom'
import App from './App.tsx'
import Docs from './pages/Docs.tsx'
import Blog, { BlogPost } from './pages/Blog.tsx'
import './index.css'

function BlogPostWrapper() {
  const { postId } = useParams()
  return <BlogPost postId={postId || ''} />
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/docs/*" element={<Docs />} />
        <Route path="/blog" element={<Blog />} />
        <Route path="/blog/:postId" element={<BlogPostWrapper />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
