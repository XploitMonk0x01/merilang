import React from 'react'
import { Link } from 'react-router-dom'

// Blog posts data
const posts = [
    {
        id: 'v1-0-2-release',
        date: '2025-01-20',
        title: 'MeriLang v1.0.2 Released',
        excerpt: 'Bug fixes and stability improvements for the interpreter and REPL experience.',
        category: 'Release',
        content: `
We're excited to announce the release of MeriLang v1.0.2! This update focuses on bug fixes and stability improvements.

## What's New

- **Improved REPL**: Better error messages and line number reporting
- **Bug Fixes**: Fixed edge cases in string concatenation
- **Performance**: Faster execution of recursive functions

## How to Update

\`\`\`bash
pip install --upgrade merilang
\`\`\`

Thank you to everyone who reported bugs and contributed to this release!
    `.trim()
    },
    {
        id: 'introducing-oop',
        date: '2025-01-15',
        title: 'Introducing Object-Oriented Programming',
        excerpt: 'MeriLang now supports classes, inheritance, and methods with Hindi keywords.',
        category: 'Feature',
        content: `
Object-oriented programming is now fully supported in MeriLang! Create classes using familiar Hindi keywords.

## New Keywords

- \`class\` - Define a class
- \`naya\` - Create a new instance
- \`yeh\` - Reference to current instance (like \`this\`)
- \`badhaao\` - Extend a class (inheritance)

## Example

\`\`\`merilang
shuru
class Person {
    vidhi __init__(naam, umar) {
        yeh.naam = naam
        yeh.umar = umar
    }
    samapt

    vidhi greet() {
        dikhao "Namaste, " + yeh.naam
    }
    samapt
}

p = naya Person("Rajesh", 25)
p.greet()
khatam
\`\`\`

Check out the [documentation](/docs/classes) for more details!
    `.trim()
    },
    {
        id: 'error-handling-guide',
        date: '2025-01-10',
        title: 'Error Handling Best Practices',
        excerpt: 'Learn how to write robust MeriLang code with try-catch-finally blocks.',
        category: 'Tutorial',
        content: `
Error handling is essential for writing reliable programs. MeriLang provides try-catch-finally blocks with Hindi keywords.

## Keywords

- \`koshish\` - Try block
- \`pakdo\` - Catch block  
- \`akhir\` - Finally block
- \`fenko\` - Throw an exception

## Example

\`\`\`merilang
shuru
koshish {
    x = 10 / 0
}
pakdo err {
    dikhao "Error: " + err
}
akhir {
    dikhao "Cleanup done"
}
khatam
\`\`\`

Always use error handling when working with file I/O, network operations, or user input.
    `.trim()
    },
    {
        id: 'meri-lang-v1-launch',
        date: '2025-01-01',
        title: 'Announcing MeriLang v1.0',
        excerpt: 'The first stable release of MeriLang - a desi programming language with Hindi keywords.',
        category: 'Announcement',
        content: `
We're thrilled to announce the first stable release of MeriLang! 🎉

## What is MeriLang?

MeriLang is a programming language designed for Indian learners, using Hindi keywords to make programming more accessible and intuitive.

## Features

- **Simple Syntax**: Easy-to-learn syntax with meri keywords
- **Full Programming Language**: Variables, functions, loops, conditionals
- **Object-Oriented**: Classes, inheritance, methods
- **Error Handling**: Try-catch-finally blocks
- **Interactive REPL**: Test code snippets interactively
- **Module System**: Import and reuse code

## Get Started

\`\`\`bash
pip install merilang
\`\`\`

Create your first program:

\`\`\`merilang
shuru
dikhao "Namaste, Duniya!"
khatam
\`\`\`

Thank you for being part of this journey. Let's make programming accessible to everyone!
    `.trim()
    }
]

function formatDate(dateStr: string) {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    })
}

function getCategoryColor(category: string) {
    switch (category) {
        case 'Release': return 'category-release'
        case 'Feature': return 'category-feature'
        case 'Tutorial': return 'category-tutorial'
        case 'Announcement': return 'category-announcement'
        default: return ''
    }
}

export default function Blog() {
    return (
        <div className="blog-layout">
            <header className="blog-header">
                <Link to="/" className="blog-logo">
                    meri<span>lang</span>
                </Link>
                <nav className="blog-nav">
                    <Link to="/docs">Documentation</Link>
                    <Link to="/blog" className="active">Blog</Link>
                    <a href="https://github.com/XploitMonk0x01/merilang" target="_blank" rel="noopener">GitHub</a>
                </nav>
            </header>

            <main className="blog-main">
                <div className="blog-hero">
                    <h1>Blog</h1>
                    <p>Updates, releases, and tutorials for MeriLang</p>
                </div>

                <div className="blog-posts">
                    {posts.map(post => (
                        <article key={post.id} className="blog-card">
                            <div className="blog-card-meta">
                                <span className={`blog-category ${getCategoryColor(post.category)}`}>
                                    {post.category}
                                </span>
                                <time dateTime={post.date}>{formatDate(post.date)}</time>
                            </div>
                            <h2>{post.title}</h2>
                            <p>{post.excerpt}</p>
                            <Link to={`/blog/${post.id}`} className="blog-read-more">
                                Read more →
                            </Link>
                        </article>
                    ))}
                </div>
            </main>

            <footer className="blog-footer">
                <p>Made with ❤️ for the meri community</p>
            </footer>
        </div>
    )
}

// Individual blog post page
export function BlogPost({ postId }: { postId: string }) {
    const post = posts.find(p => p.id === postId)

    if (!post) {
        return (
            <div className="blog-layout">
                <header className="blog-header">
                    <Link to="/" className="blog-logo">
                        meri<span>lang</span>
                    </Link>
                    <nav className="blog-nav">
                        <Link to="/docs">Documentation</Link>
                        <Link to="/blog">Blog</Link>
                        <a href="https://github.com/XploitMonk0x01/merilang" target="_blank" rel="noopener">GitHub</a>
                    </nav>
                </header>
                <main className="blog-main">
                    <div className="blog-post-content">
                        <h1>Post not found</h1>
                        <p>The blog post you're looking for doesn't exist.</p>
                        <Link to="/blog" className="btn btn-primary">Back to Blog</Link>
                    </div>
                </main>
            </div>
        )
    }

    // Simple markdown-like rendering
    const renderContent = (content: string) => {
        const lines = content.split('\n')
        const elements: React.ReactElement[] = []
        let inCodeBlock = false
        let codeContent = ''

        lines.forEach((line, i) => {
            if (line.startsWith('```')) {
                if (inCodeBlock) {
                    elements.push(
                        <pre key={`code-${i}`} className="code-block">
                            <code>{codeContent.trim()}</code>
                        </pre>
                    )
                    codeContent = ''
                    inCodeBlock = false
                } else {
                    inCodeBlock = true
                }
            } else if (inCodeBlock) {
                codeContent += line + '\n'
            } else if (line.startsWith('## ')) {
                elements.push(<h2 key={i}>{line.slice(3)}</h2>)
            } else if (line.startsWith('- ')) {
                elements.push(<li key={i}>{renderInline(line.slice(2))}</li>)
            } else if (line.trim() === '') {
                // Skip empty lines
            } else {
                elements.push(<p key={i}>{renderInline(line)}</p>)
            }
        })

        return elements
    }

    const renderInline = (text: string) => {
        // Handle inline code
        const parts = text.split(/(`[^`]+`)/)
        return parts.map((part, i) => {
            if (part.startsWith('`') && part.endsWith('`')) {
                return <code key={i}>{part.slice(1, -1)}</code>
            }
            // Handle links
            const linkMatch = part.match(/\[([^\]]+)\]\(([^)]+)\)/)
            if (linkMatch) {
                const before = part.slice(0, linkMatch.index)
                const after = part.slice((linkMatch.index || 0) + linkMatch[0].length)
                return (
                    <span key={i}>
                        {before}
                        <Link to={linkMatch[2]}>{linkMatch[1]}</Link>
                        {after}
                    </span>
                )
            }
            // Handle bold
            const boldParts = part.split(/(\*\*[^*]+\*\*)/)
            return boldParts.map((bp, j) => {
                if (bp.startsWith('**') && bp.endsWith('**')) {
                    return <strong key={j}>{bp.slice(2, -2)}</strong>
                }
                return bp
            })
        })
    }

    return (
        <div className="blog-layout">
            <header className="blog-header">
                <Link to="/" className="blog-logo">
                    meri<span>lang</span>
                </Link>
                <nav className="blog-nav">
                    <Link to="/docs">Documentation</Link>
                    <Link to="/blog">Blog</Link>
                    <a href="https://github.com/XploitMonk0x01/merilang" target="_blank" rel="noopener">GitHub</a>
                </nav>
            </header>

            <main className="blog-main">
                <article className="blog-post-content">
                    <Link to="/blog" className="blog-back">← Back to Blog</Link>

                    <div className="blog-post-meta">
                        <span className={`blog-category ${getCategoryColor(post.category)}`}>
                            {post.category}
                        </span>
                        <time dateTime={post.date}>{formatDate(post.date)}</time>
                    </div>

                    <h1>{post.title}</h1>

                    <div className="blog-post-body">
                        {renderContent(post.content)}
                    </div>
                </article>
            </main>

            <footer className="blog-footer">
                <p>Made with ❤️ for the meri community</p>
            </footer>
        </div>
    )
}
