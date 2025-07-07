import { Loader2, FileText, Search, CheckCircle, Brain } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'

const LoadingState = ({ stage = 'processing', progress = 0 }) => {
  const stages = [
    { id: 'uploading', label: 'Uploading documents', icon: FileText },
    { id: 'classifying', label: 'Classifying documents', icon: Search },
    { id: 'extracting', label: 'Extracting data', icon: Brain },
    { id: 'validating', label: 'Validating information', icon: CheckCircle },
    { id: 'deciding', label: 'Making decision', icon: Brain }
  ]

  const currentStageIndex = stages.findIndex(s => s.id === stage)
  const currentStage = stages[currentStageIndex] || stages[0]
  const Icon = currentStage.icon

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardContent className="p-8 text-center">
        <div className="mb-6">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
            <Icon className="h-8 w-8 text-primary animate-pulse" />
          </div>
          <h3 className="text-lg font-semibold mb-2">Processing Your Claim</h3>
          <p className="text-muted-foreground text-sm">{currentStage.label}...</p>
        </div>

        <div className="space-y-4">
          <Progress value={progress} className="w-full" />
          <p className="text-xs text-muted-foreground">
            {progress}% complete
          </p>
        </div>

        <div className="mt-6 space-y-2">
          {stages.map((stageItem, index) => (
            <div 
              key={stageItem.id}
              className={`flex items-center gap-2 text-sm ${
                index < currentStageIndex 
                  ? 'text-green-600' 
                  : index === currentStageIndex 
                    ? 'text-primary' 
                    : 'text-muted-foreground'
              }`}
            >
              {index < currentStageIndex ? (
                <CheckCircle className="h-4 w-4" />
              ) : index === currentStageIndex ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <div className="h-4 w-4 rounded-full border-2 border-muted-foreground/30" />
              )}
              <span>{stageItem.label}</span>
            </div>
          ))}
        </div>

        <div className="mt-6 text-xs text-muted-foreground">
          <p>This may take a few moments depending on document complexity</p>
        </div>
      </CardContent>
    </Card>
  )
}

export default LoadingState

