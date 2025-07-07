import { useState } from 'react'
import { Toaster } from '@/components/ui/toaster'
import { useToast } from '@/hooks/use-toast'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Heart, Shield, Brain, FileText, ArrowRight } from 'lucide-react'
import FileUpload from './components/FileUpload'
import LoadingState from './components/LoadingState'
import ResultsDisplay from './components/ResultsDisplay'
import './App.css'

function App() {
  const [files, setFiles] = useState([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [results, setResults] = useState(null)
  const [loadingStage, setLoadingStage] = useState('processing')
  const [loadingProgress, setLoadingProgress] = useState(0)
  const { toast } = useToast()

  const handleFilesChange = (newFiles) => {
    setFiles(newFiles)
    if (results) {
      setResults(null) // Clear previous results when new files are added
    }
  }

  const simulateProgress = () => {
    const stages = ['uploading', 'classifying', 'extracting', 'validating', 'deciding']
    let currentStage = 0
    let progress = 0

    const interval = setInterval(() => {
      progress += Math.random() * 15 + 5 // Random progress between 5-20%
      
      if (progress >= 100) {
        progress = 100
        clearInterval(interval)
        return
      }

      // Change stage based on progress
      const stageIndex = Math.floor((progress / 100) * stages.length)
      if (stageIndex < stages.length) {
        setLoadingStage(stages[stageIndex])
      }
      
      setLoadingProgress(Math.min(progress, 95)) // Keep at 95% until actual completion
    }, 800)

    return interval
  }

  const processFiles = async () => {
    if (files.length === 0) {
      toast({
        title: "No files selected",
        description: "Please upload at least one PDF file to process.",
        variant: "destructive"
      })
      return
    }

    setIsProcessing(true)
    setResults(null)
    setLoadingProgress(0)
    
    const progressInterval = simulateProgress()

    try {
      const formData = new FormData()
      files.forEach(file => {
        formData.append('files', file)
      })

      const response = await fetch('https://5000-i7exjbniwzpb6reox9az2-7ee497ef.manusvm.computer/process-claim', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to process claim')
      }

      const result = await response.json()
      
      // Complete the progress
      clearInterval(progressInterval)
      setLoadingProgress(100)
      
      // Small delay to show completion
      setTimeout(() => {
        setResults(result)
        setIsProcessing(false)
        
        toast({
          title: "Processing Complete",
          description: `Successfully processed ${files.length} document(s). Decision: ${result.claim_decision?.status?.toUpperCase()}`,
        })
      }, 500)

    } catch (error) {
      clearInterval(progressInterval)
      setIsProcessing(false)
      setLoadingProgress(0)
      
      toast({
        title: "Processing Failed",
        description: error.message,
        variant: "destructive"
      })
    }
  }

  const downloadPDF = async () => {
    if (!results) return

    try {
      const response = await fetch('https://5000-i7exjbniwzpb6reox9az2-7ee497ef.manusvm.computer/generate-pdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(results)
      })

      if (!response.ok) {
        throw new Error('Failed to generate PDF')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `claim-processing-result-${new Date().toISOString().split('T')[0]}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast({
        title: "PDF Downloaded",
        description: "Your claim processing report has been downloaded successfully.",
      })
    } catch (error) {
      toast({
        title: "Download Failed",
        description: "Failed to generate PDF report. Please try again.",
        variant: "destructive"
      })
    }
  }

  const clearAll = () => {
    setFiles([])
    setResults(null)
    setIsProcessing(false)
    setLoadingProgress(0)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
                <Heart className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold">HealthPay AI</h1>
                <p className="text-sm text-muted-foreground">Medical Claim Processor</p>
              </div>
            </div>
            <Badge variant="outline" className="gap-1">
              <Shield className="h-3 w-3" />
              Secure & HIPAA Compliant
            </Badge>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        {!results && !isProcessing && (
          <div className="text-center mb-12">
            <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-primary/10">
              <Brain className="h-10 w-10 text-primary" />
            </div>
            <h2 className="text-3xl font-bold mb-4">AI-Powered Medical Claim Processing</h2>
            <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
              Upload your medical documents and let our advanced AI agents analyze, validate, 
              and process your insurance claim with precision and speed.
            </p>
            
            {/* Features */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 max-w-4xl mx-auto">
              <Card className="text-center">
                <CardContent className="p-6">
                  <FileText className="h-8 w-8 text-blue-600 mx-auto mb-3" />
                  <h3 className="font-semibold mb-2">Document Analysis</h3>
                  <p className="text-sm text-muted-foreground">
                    Automatically classify and extract data from bills, summaries, and insurance cards
                  </p>
                </CardContent>
              </Card>
              
              <Card className="text-center">
                <CardContent className="p-6">
                  <Shield className="h-8 w-8 text-green-600 mx-auto mb-3" />
                  <h3 className="font-semibold mb-2">Smart Validation</h3>
                  <p className="text-sm text-muted-foreground">
                    Cross-check information for consistency and completeness across documents
                  </p>
                </CardContent>
              </Card>
              
              <Card className="text-center">
                <CardContent className="p-6">
                  <Brain className="h-8 w-8 text-purple-600 mx-auto mb-3" />
                  <h3 className="font-semibold mb-2">AI Decision Engine</h3>
                  <p className="text-sm text-muted-foreground">
                    Get instant approval/rejection decisions with detailed reasoning and confidence scores
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          {!isProcessing && !results && (
            <div className="space-y-8">
              <FileUpload 
                onFilesChange={handleFilesChange} 
                isProcessing={isProcessing}
              />
              
              {files.length > 0 && (
                <div className="flex justify-center gap-4">
                  <Button 
                    onClick={processFiles}
                    size="lg"
                    className="gap-2"
                    disabled={isProcessing}
                  >
                    <Brain className="h-4 w-4" />
                    Process Claim
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                  
                  <Button 
                    variant="outline" 
                    onClick={clearAll}
                    size="lg"
                  >
                    Clear All
                  </Button>
                </div>
              )}
            </div>
          )}

          {isProcessing && (
            <div className="flex justify-center">
              <LoadingState 
                stage={loadingStage} 
                progress={loadingProgress} 
              />
            </div>
          )}

          {results && !isProcessing && (
            <div className="space-y-6">
              <ResultsDisplay 
                results={results} 
                onDownloadPDF={downloadPDF}
              />
              
              <div className="flex justify-center">
                <Button 
                  variant="outline" 
                  onClick={clearAll}
                  size="lg"
                >
                  Process New Claim
                </Button>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t bg-white/80 backdrop-blur-sm mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-sm text-muted-foreground">
            <p>© 2024 HealthPay AI. Powered by advanced AI agents and machine learning.</p>
            <p className="mt-2">Secure, fast, and accurate medical claim processing.</p>
          </div>
        </div>
      </footer>

      <Toaster />
    </div>
  )
}

export default App

