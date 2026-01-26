import { useState } from 'react'

const defaultCode = `shuru
// Variables
naam = "Duniya"
count = 0

// Loop example
jabtak count < 3 {
    dikhao "Namaste, " + naam
    count = count + 1
} band

// Function example
vidhi greet(person) {
    vapas "Hello, " + person
} samapt

result = greet("Developer")
dikhao result
khatam`

export default function Playground({ initialCode = defaultCode }: { initialCode?: string }) {
    const [code, setCode] = useState(initialCode)
    const [copied, setCopied] = useState(false)

    const handleRun = () => {
        alert('Run functionality coming soon!\n\nFor now, use:\npip install merilang\nml yourfile.meri')
    }

    const handleClear = () => {
        setCode('')
    }

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(code)
            setCopied(true)
            setTimeout(() => setCopied(false), 2000)
        } catch (err) {
            console.error('Failed to copy:', err)
        }
    }

    const lines = code.split('\n')

    return (
        <div className="playground">
            <div className="playground-header">
                <h3>Playground</h3>
                <div className="playground-actions">
                    <button onClick={handleCopy} className="playground-btn copy">
                        {copied ? 'Copied!' : 'Copy'}
                    </button>
                    <button onClick={handleRun} className="playground-btn run">
                        Run
                    </button>
                    <button onClick={handleClear} className="playground-btn clear">
                        Clear
                    </button>
                </div>
            </div>
            <div className="playground-editor">
                <div className="line-numbers">
                    {lines.map((_, i) => (
                        <span key={i}>{i + 1}</span>
                    ))}
                </div>
                <textarea
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    spellCheck={false}
                    className="code-input"
                />
            </div>
        </div>
    )
}
