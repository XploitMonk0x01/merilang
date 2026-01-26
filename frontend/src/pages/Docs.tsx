import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'

// Documentation content sections
const sections = {
    'getting-started': {
        title: 'Getting Started',
        items: [
            { id: 'installation', title: 'Installation' },
            { id: 'quick-start', title: 'Quick Start' },
            { id: 'repl', title: 'Interactive REPL' },
        ]
    },
    'language-basics': {
        title: 'Language Basics',
        items: [
            { id: 'program-structure', title: 'Program Structure' },
            { id: 'variables', title: 'Variables' },
            { id: 'data-types', title: 'Data Types' },
            { id: 'operators', title: 'Operators' },
        ]
    },
    'control-flow': {
        title: 'Control Flow',
        items: [
            { id: 'conditionals', title: 'Conditionals' },
            { id: 'loops', title: 'Loops' },
        ]
    },
    'functions': {
        title: 'Functions',
        items: [
            { id: 'defining-functions', title: 'Defining Functions' },
            { id: 'built-in-functions', title: 'Built-in Functions' },
        ]
    },
    'oop': {
        title: 'Object-Oriented',
        items: [
            { id: 'classes', title: 'Classes' },
            { id: 'inheritance', title: 'Inheritance' },
        ]
    },
    'advanced': {
        title: 'Advanced',
        items: [
            { id: 'error-handling', title: 'Error Handling' },
            { id: 'file-io', title: 'File I/O' },
            { id: 'modules', title: 'Modules' },
        ]
    },
}

// Documentation content
const content: Record<string, { title: string; description: string; steps: { title: string; description?: string; code?: string }[] }> = {
    'installation': {
        title: 'Installation',
        description: 'Get up and running with MeriLang in minutes.',
        steps: [
            {
                title: 'Install via pip',
                description: 'The recommended way to install MeriLang is using pip.',
                code: `pip install merilang`
            },
            {
                title: 'Or install from source',
                description: 'Clone the repository and install in development mode.',
                code: `git clone https://github.com/XploitMonk0x01/merilang.git
cd merilang
pip install -e .`
            },
            {
                title: 'Verify installation',
                description: 'Check that MeriLang is installed correctly.',
                code: `merilang --version
# or use the short alias
ml --version`
            }
        ]
    },
    'quick-start': {
        title: 'Quick Start',
        description: 'Write and run your first MeriLang program.',
        steps: [
            {
                title: 'Create a file',
                description: 'Create a new file called hello.meri with the following content:',
                code: `shuru
dikhao "Namaste, Duniya!"
khatam`
            },
            {
                title: 'Run your program',
                description: 'Execute the file using the MeriLang CLI.',
                code: `merilang hello.meri
# or
ml hello.meri`
            },
            {
                title: 'See the output',
                code: `Namaste, Duniya!`
            }
        ]
    },
    'repl': {
        title: 'Interactive REPL',
        description: 'Test code snippets interactively without creating files.',
        steps: [
            {
                title: 'Start the REPL',
                code: `merilang
# or
ml`
            },
            {
                title: 'Try some expressions',
                code: `MeriLang v1.0.2 Interactive REPL
Type 'exit' or press Ctrl+C to quit

>>> x = 42
>>> dikhao x
42
>>> dikhao x * 2
84`
            }
        ]
    },
    'program-structure': {
        title: 'Program Structure',
        description: 'Every MeriLang program has a defined structure.',
        steps: [
            {
                title: 'Basic structure',
                description: 'Programs start with shuru (begin) and end with khatam (end).',
                code: `shuru
// Your code goes here
khatam`
            },
            {
                title: 'Comments',
                description: 'Use // for single-line comments.',
                code: `shuru
// This is a comment
dikhao "Hello"  // Inline comment
khatam`
            }
        ]
    },
    'variables': {
        title: 'Variables',
        description: 'Variables store data for use in your programs.',
        steps: [
            {
                title: 'Declaring variables',
                description: 'Simply assign a value to create a variable.',
                code: `shuru
x = 42              // Integer
pi = 3.14           // Float
naam = "Rajwant"    // String
is_valid = sahi     // Boolean (true)
is_false = galat    // Boolean (false)
khatam`
            }
        ]
    },
    'data-types': {
        title: 'Data Types',
        description: 'MeriLang supports several built-in data types.',
        steps: [
            {
                title: 'Numbers',
                code: `age = 25        // Integer
pi = 3.14159    // Float`
            },
            {
                title: 'Strings',
                code: `name = "Rajesh"
greeting = "नमस्ते"  // Hindi text supported`
            },
            {
                title: 'Booleans',
                code: `is_active = sahi   // true
is_done = galat    // false`
            },
            {
                title: 'Lists',
                code: `numbers = [1, 2, 3, 4, 5]
names = ["Amit", "Priya", "Rahul"]`
            }
        ]
    },
    'operators': {
        title: 'Operators',
        description: 'Arithmetic and comparison operators.',
        steps: [
            {
                title: 'Arithmetic operators',
                code: `a = 10 + 5   // Addition: 15
b = 10 - 5   // Subtraction: 5
c = 10 * 5   // Multiplication: 50
d = 10 / 5   // Division: 2
e = 10 % 3   // Modulo: 1`
            },
            {
                title: 'Comparison operators',
                code: `x > y    // Greater than
x < y    // Less than
x >= y   // Greater or equal
x <= y   // Less or equal
x == y   // Equal
x != y   // Not equal`
            }
        ]
    },
    'conditionals': {
        title: 'Conditionals',
        description: 'Control program flow with if-else statements.',
        steps: [
            {
                title: 'If-else syntax',
                description: 'Use agar for if, warna for else, and bas to close.',
                code: `shuru
age = 25

agar age >= 18 {
    dikhao "Adult"
} warna {
    dikhao "Minor"
} bas
khatam`
            }
        ]
    },
    'loops': {
        title: 'Loops',
        description: 'Repeat code with for and while loops.',
        steps: [
            {
                title: 'For loop',
                description: 'Use chalao with se (from) and tak (to).',
                code: `shuru
chalao i se 0 tak 5 {
    dikhao i
}
khatam`
            },
            {
                title: 'While loop',
                description: 'Use jabtak for while, band to close.',
                code: `shuru
count = 0
jabtak count < 5 {
    dikhao count
    count = count + 1
} band
khatam`
            }
        ]
    },
    'defining-functions': {
        title: 'Defining Functions',
        description: 'Create reusable code blocks with functions.',
        steps: [
            {
                title: 'Function syntax',
                description: 'Use vidhi to define, vapas to return, samapt to close.',
                code: `shuru
vidhi add(a, b) {
    vapas a + b
} samapt

result = add(5, 3)
dikhao result  // Output: 8
khatam`
            },
            {
                title: 'Using bulayo',
                description: 'Alternatively use bulayo keyword to call functions.',
                code: `bulayo add(10, 20)`
            }
        ]
    },
    'built-in-functions': {
        title: 'Built-in Functions',
        description: 'MeriLang provides many built-in functions.',
        steps: [
            {
                title: 'List operations',
                code: `length(list)     // Get length
append(list, x)  // Add element
pop(list, i)     // Remove at index
sort(list)       // Sorted copy
reverse(list)    // Reversed copy
sum(list)        // Sum elements`
            },
            {
                title: 'String operations',
                code: `upper(str)              // Uppercase
lower(str)              // Lowercase
split(str, sep)         // Split to list
join(list, sep)         // Join to string
replace(str, old, new)  // Replace`
            },
            {
                title: 'Type conversions',
                code: `type(value)  // Get type name
str(42)      // "42"
int("42")    // 42
float("3.14")// 3.14`
            }
        ]
    },
    'classes': {
        title: 'Classes',
        description: 'Define custom types with classes.',
        steps: [
            {
                title: 'Class definition',
                description: 'Use class keyword, yeh for this reference.',
                code: `shuru
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
khatam`
            }
        ]
    },
    'inheritance': {
        title: 'Inheritance',
        description: 'Extend classes using inheritance.',
        steps: [
            {
                title: 'Extending a class',
                description: 'Use badhaao keyword to inherit.',
                code: `shuru
class Student badhaao Person {
    vidhi __init__(naam, umar, school) {
        yeh.naam = naam
        yeh.umar = umar
        yeh.school = school
    }
    samapt

    vidhi study() {
        dikhao yeh.naam + " is studying"
    }
    samapt
}

s = naya Student("Priya", 20, "Delhi Univ")
s.greet()   // Inherited method
s.study()   // Own method
khatam`
            }
        ]
    },
    'error-handling': {
        title: 'Error Handling',
        description: 'Handle errors gracefully with try-catch.',
        steps: [
            {
                title: 'Try-catch-finally',
                description: 'Use koshish (try), pakdo (catch), akhir (finally).',
                code: `shuru
koshish {
    x = 10 / 0
}
pakdo err {
    dikhao "Error: " + err
}
akhir {
    dikhao "Cleanup done"
}
khatam`
            },
            {
                title: 'Throwing exceptions',
                description: 'Use fenko to throw custom errors.',
                code: `vidhi validate(age) {
    agar age < 0 {
        fenko "Age cannot be negative"
    }
    bas
    vapas sahi
} samapt`
            }
        ]
    },
    'file-io': {
        title: 'File I/O',
        description: 'Read from and write to files.',
        steps: [
            {
                title: 'Writing files',
                description: 'Use likho keyword.',
                code: `likho "output.txt" "Hello, MeriLang!"`
            },
            {
                title: 'Reading files',
                description: 'Use padho_file function.',
                code: `content = padho_file("output.txt")
dikhao content`
            }
        ]
    },
    'modules': {
        title: 'Modules',
        description: 'Organize code across multiple files.',
        steps: [
            {
                title: 'Creating a module',
                description: 'Create mylib.meri:',
                code: `// mylib.meri
shuru
vidhi helper(x) {
    vapas x * 2
} samapt
khatam`
            },
            {
                title: 'Importing a module',
                description: 'Use lao keyword to import.',
                code: `// main.meri
shuru
lao "mylib"
result = helper(21)
dikhao result  // 42
khatam`
            }
        ]
    },
}

// Copy button code block component
function CodeBlock({ code }: { code: string }) {
    const [copied, setCopied] = useState(false)

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(code)
            setCopied(true)
            setTimeout(() => setCopied(false), 2000)
        } catch (err) {
            console.error('Failed to copy:', err)
        }
    }

    return (
        <div className="code-block-wrapper">
            <button className="copy-btn" onClick={handleCopy} title="Copy to clipboard">
                {copied ? (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="20 6 9 17 4 12" />
                    </svg>
                ) : (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                    </svg>
                )}
                <span>{copied ? 'Copied!' : 'Copy'}</span>
            </button>
            <pre className="code-block">
                <code>{code}</code>
            </pre>
        </div>
    )
}

function Sidebar({ activeSection }: { activeSection: string }) {
    const [expanded, setExpanded] = useState<Record<string, boolean>>(() => {
        // Find which section contains the active item and expand it
        const initial: Record<string, boolean> = {}
        for (const [key, section] of Object.entries(sections)) {
            initial[key] = section.items.some(item => item.id === activeSection)
        }
        return initial
    })

    const toggle = (key: string) => {
        setExpanded(prev => ({ ...prev, [key]: !prev[key] }))
    }

    return (
        <aside className="docs-sidebar">
            <div className="sidebar-header">
                <Link to="/" className="sidebar-logo">
                    meri<span>lang</span>
                </Link>
            </div>
            <nav className="sidebar-nav">
                {Object.entries(sections).map(([key, section]) => (
                    <div key={key} className="sidebar-section">
                        <button
                            className={`sidebar-section-title ${expanded[key] ? 'expanded' : ''}`}
                            onClick={() => toggle(key)}
                        >
                            {section.title}
                            <svg className="chevron" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                            </svg>
                        </button>
                        {expanded[key] && (
                            <ul className="sidebar-items">
                                {section.items.map(item => (
                                    <li key={item.id}>
                                        <Link
                                            to={`/docs/${item.id}`}
                                            className={`sidebar-link ${activeSection === item.id ? 'active' : ''}`}
                                        >
                                            {item.title}
                                        </Link>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>
                ))}
            </nav>
        </aside>
    )
}

function DocContent({ sectionId }: { sectionId: string }) {
    const doc = content[sectionId]

    if (!doc) {
        return (
            <div className="doc-content">
                <h1>Documentation</h1>
                <p>Select a topic from the sidebar to get started.</p>
            </div>
        )
    }

    return (
        <article className="doc-content">
            <header className="doc-header">
                <h1>{doc.title}</h1>
                <p className="doc-description">{doc.description}</p>
            </header>

            <div className="doc-steps">
                {doc.steps.map((step, index) => (
                    <section key={index} className="doc-step">
                        <div className="step-number">{index + 1}</div>
                        <div className="step-content">
                            <h3>{step.title}</h3>
                            {step.description && <p>{step.description}</p>}
                            {step.code && <CodeBlock code={step.code} />}
                        </div>
                    </section>
                ))}
            </div>
        </article>
    )
}

export default function Docs() {
    const location = useLocation()
    const path = location.pathname.replace('/docs/', '').replace('/docs', '')
    const activeSection = path || 'installation'

    return (
        <div className="docs-layout">
            <Sidebar activeSection={activeSection} />
            <main className="docs-main">
                <DocContent sectionId={activeSection} />
            </main>
        </div>
    )
}
