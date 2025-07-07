import { useState, useCallback } from 'react'
import { Upload, FileText, X, CheckCircle, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'

const FileUpload = ({ onFilesChange, isProcessing }) => {
  const [files, setFiles] = useState([])
  const [dragActive, setDragActive] = useState(false)

  const handleFiles = useCallback((newFiles) => {
    const validFiles = Array.from(newFiles).filter(file => 
      file.type === 'application/pdf' && file.size <= 10 * 1024 * 1024 // 10MB limit
    )
    
    setFiles(prev => {
      const updated = [...prev, ...validFiles]
      onFilesChange(updated)
      return updated
    })
  }, [onFilesChange])

  const removeFile = useCallback((index) => {
    setFiles(prev => {
      const updated = prev.filter((_, i) => i !== index)
      onFilesChange(updated)
      return updated
    })
  }, [onFilesChange])

  const handleDrag = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files)
    }
  }, [handleFiles])

  const handleChange = useCallback((e) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files)
    }
  }, [handleFiles])

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <Card className={`transition-all duration-200 ${
        dragActive ? 'border-primary bg-primary/5' : 'border-dashed border-muted-foreground/25'
      }`}>
        <CardContent className="p-8">
          <div
            className="text-center"
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
              <Upload className="h-8 w-8 text-primary" />
            </div>
            
            <h3 className="mb-2 text-lg font-semibold">Upload Medical Documents</h3>
            <p className="mb-4 text-sm text-muted-foreground">
              Drag and drop your PDF files here, or click to browse
            </p>
            
            <input
              type="file"
              multiple
              accept=".pdf"
              onChange={handleChange}
              className="hidden"
              id="file-upload"
              disabled={isProcessing}
            />
            
            <Button 
              asChild 
              variant="outline" 
              className="mb-4"
              disabled={isProcessing}
            >
              <label htmlFor="file-upload" className="cursor-pointer">
                Select PDF Files
              </label>
            </Button>
            
            <div className="text-xs text-muted-foreground">
              <p>Supported: Hospital bills, discharge summaries, insurance cards</p>
              <p>Maximum file size: 10MB per file</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* File List */}
      {files.length > 0 && (
        <Card>
          <CardContent className="p-6">
            <h4 className="mb-4 font-semibold">Uploaded Files ({files.length})</h4>
            <div className="space-y-3">
              {files.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between rounded-lg border p-3"
                >
                  <div className="flex items-center space-x-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-red-50">
                      <FileText className="h-5 w-5 text-red-600" />
                    </div>
                    <div>
                      <p className="font-medium text-sm">{file.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {!isProcessing && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeFile(index)}
                        className="h-8 w-8 p-0"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    )}
                    {isProcessing && (
                      <div className="flex items-center space-x-2">
                        <div className="h-2 w-2 animate-pulse rounded-full bg-blue-500"></div>
                        <span className="text-xs text-muted-foreground">Processing...</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default FileUpload

