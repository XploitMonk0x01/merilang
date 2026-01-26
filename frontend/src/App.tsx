import { Link } from 'react-router-dom'
import Prism from './components/Prism'
import Playground from './components/Playground'
import ScrollStack, { ScrollStackItem } from './components/ScrollStack'
import './index.css'

function App() {
  return (
    <div className="landing">
      {/* Header */}
      <header className="header">
        <div className="logo">
          meri<span>lang</span>
        </div>
        <nav className="nav">
          <Link to="/docs">Documentation</Link>
          <Link to="/blog">Blog</Link>
          <a href="https://github.com/XploitMonk0x01/merilang" target="_blank" rel="noopener">GitHub</a>
        </nav>
      </header>

      {/* Hero */}
      <section className="hero">
        <div className="hero-bg">
          <Prism
            animationType="rotate"
            timeScale={0.5}
            height={3.5}
            baseWidth={5.5}
            scale={3.6}
            hueShift={0}
            colorFrequency={1}
            noise={0}
            glow={1}
          />
        </div>

        <div className="hero-content">
          <span className="hero-tag">Open Source</span>
          <h1 className="hero-title">
            Code in your <span className="meri">meri</span> bhasha
          </h1>
          <p className="hero-subtitle">
            A desi programming language with Hindi keywords. Simple syntax,
            full OOP support, and helpful error messages—built for learning.
          </p>
          <div className="hero-actions">
            <Link to="/docs" className="btn btn-primary">
              Get Started
            </Link>
            <a href="https://github.com/XploitMonk0x01/merilang" className="btn btn-secondary" target="_blank" rel="noopener">
              View on GitHub
            </a>
          </div>
        </div>
      </section>

      {/* Playground */}
      <section className="playground-section">
        <Playground />
      </section>

      {/* Features Section with ScrollStack */}
      <section className="features-section">
        <div className="features-header">
          <h2>Why MeriLang?</h2>
          <p>
            Programming education often feels inaccessible due to language barriers.
            MeriLang bridges this gap using Hindi keywords.
          </p>
        </div>

        <div className="scroll-stack-wrapper">
          <ScrollStack
            useWindowScroll={false}
            itemDistance={60}
            itemStackDistance={20}
            blurAmount={1.5}
            baseScale={0.94}
          >
            <ScrollStackItem itemClassName="feature-scroll-card">
              <div className="feature-scroll-icon">📝</div>
              <div className="feature-scroll-content">
                <h3>Hindi Syntax</h3>
                <p>Learn programming with familiar Hindi keywords like <code>dikhao</code>, <code>agar</code>, <code>jabtak</code>, and <code>vidhi</code>.</p>
              </div>
            </ScrollStackItem>

            <ScrollStackItem itemClassName="feature-scroll-card">
              <div className="feature-scroll-icon">🎯</div>
              <div className="feature-scroll-content">
                <h3>Full OOP Support</h3>
                <p>Classes, inheritance, and methods with keywords like <code>class</code>, <code>naya</code>, <code>yeh</code>, and <code>badhaao</code>.</p>
              </div>
            </ScrollStackItem>

            <ScrollStackItem itemClassName="feature-scroll-card">
              <div className="feature-scroll-icon">🛡️</div>
              <div className="feature-scroll-content">
                <h3>Error Handling</h3>
                <p>Try-catch-finally blocks with <code>koshish</code>, <code>pakdo</code>, <code>akhir</code> for robust code.</p>
              </div>
            </ScrollStackItem>

            <ScrollStackItem itemClassName="feature-scroll-card">
              <div className="feature-scroll-icon">📦</div>
              <div className="feature-scroll-content">
                <h3>Module System</h3>
                <p>Import and reuse code across files with the <code>lao</code> keyword.</p>
              </div>
            </ScrollStackItem>

            <ScrollStackItem itemClassName="feature-scroll-card">
              <div className="feature-scroll-icon">⚡</div>
              <div className="feature-scroll-content">
                <h3>Interactive REPL</h3>
                <p>Test code snippets instantly without creating files.</p>
              </div>
            </ScrollStackItem>

            <ScrollStackItem itemClassName="feature-scroll-card">
              <div className="feature-scroll-icon">💡</div>
              <div className="feature-scroll-content">
                <h3>Helpful Errors</h3>
                <p>Clear error messages with line numbers to help you debug quickly.</p>
              </div>
            </ScrollStackItem>
          </ScrollStack>
        </div>
      </section>

      {/* Developers Section */}
      <section className="developers-section">
        <h2>Meet the Developers</h2>
        <p className="developers-subtitle">
          Built with ❤️ by passionate developers for the Indian programming community
        </p>

        <div className="developers-grid">
          <a href="https://github.com/XploitMonk0x01" target="_blank" rel="noopener" className="developer-card">
            <img
              src="https://github.com/XploitMonk0x01.png"
              alt="XploitMonk0x01"
              className="developer-avatar"
            />
            <h3>XploitMonk0x01</h3>
            <p>Creator & Lead Developer</p>
            <span className="developer-github">
              <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
              </svg>
              @XploitMonk0x01
            </span>
          </a>

          <a href="https://github.com/amanverma-00" target="_blank" rel="noopener" className="developer-card">
            <img
              src="https://github.com/amanverma-00.png"
              alt="amanverma-00"
              className="developer-avatar"
            />
            <h3>Aman Verma</h3>
            <p>Core Contributor and designer</p>
            <span className="developer-github">
              <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
              </svg>
              @amanverma-00
            </span>
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-content">
          <div className="footer-brand">
            <span className="footer-logo">meri<span>lang</span></span>
            <p>A desi programming language for Indian learners</p>
          </div>
          <div className="footer-links">
            <div className="footer-col">
              <h4>Learn</h4>
              <Link to="/docs">Documentation</Link>
              <Link to="/docs/quick-start">Quick Start</Link>
              <Link to="/docs/installation">Installation</Link>
            </div>
            <div className="footer-col">
              <h4>Community</h4>
              <a href="https://github.com/XploitMonk0x01/merilang" target="_blank" rel="noopener">GitHub</a>
              <Link to="/blog">Blog</Link>
              <a href="https://github.com/XploitMonk0x01/merilang/issues" target="_blank" rel="noopener">Issues</a>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <code>pip install merilang</code>
          <p>Made with ❤️ for the meri community</p>
        </div>
      </footer>
    </div>
  )
}

export default App
