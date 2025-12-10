import { useEffect, useRef } from 'react'
import { DiffEditor } from '@monaco-editor/react'
import type { editor } from 'monaco-editor'

interface MonacoDiffViewerProps {
  original: string
  modified: string
  language?: string
  height?: string
  readOnly?: boolean
}

export function MonacoDiffViewer({
  original,
  modified,
  language = 'php',
  height = '600px',
  readOnly = true,
}: MonacoDiffViewerProps) {
  const editorRef = useRef<editor.IStandaloneDiffEditor | null>(null)

  function handleEditorDidMount(editor: editor.IStandaloneDiffEditor) {
    editorRef.current = editor
  }

  useEffect(() => {
    // Configure Monaco theme
    if (editorRef.current) {
      editorRef.current.updateOptions({
        readOnly,
        renderSideBySide: true,
        minimap: { enabled: true },
      })
    }
  }, [readOnly])

  return (
    <div className="rounded-lg overflow-hidden border border-glass-border">
      <DiffEditor
        height={height}
        language={language}
        original={original}
        modified={modified}
        onMount={handleEditorDidMount}
        theme="vs-dark"
        options={{
          readOnly,
          renderSideBySide: true,
          minimap: { enabled: true },
          fontSize: 13,
          fontFamily: 'JetBrains Mono, monospace',
          lineNumbers: 'on',
          scrollBeyondLastLine: false,
          automaticLayout: true,
          wordWrap: 'on',
          renderLineHighlight: 'all',
          scrollbar: {
            vertical: 'visible',
            horizontal: 'visible',
            useShadows: false,
            verticalScrollbarSize: 10,
            horizontalScrollbarSize: 10,
          },
        }}
      />
    </div>
  )
}

