import { useState } from 'react'
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertTriangle, 
  Download, 
  FileText,
  Hospital,
  CreditCard,
  User,
  Calendar,
  DollarSign,
  ChevronDown,
  ChevronUp
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'

const ResultsDisplay = ({ results, onDownloadPDF }) => {
  const [expandedSections, setExpandedSections] = useState({
    documents: true,
    validation: true,
    decision: true
  })

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'rejected':
        return <XCircle className="h-5 w-5 text-red-600" />
      case 'pending':
        return <Clock className="h-5 w-5 text-yellow-600" />
      default:
        return <AlertTriangle className="h-5 w-5 text-gray-600" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved':
        return 'bg-green-50 text-green-700 border-green-200'
      case 'rejected':
        return 'bg-red-50 text-red-700 border-red-200'
      case 'pending':
        return 'bg-yellow-50 text-yellow-700 border-yellow-200'
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200'
    }
  }

  const getDocumentIcon = (type) => {
    switch (type) {
      case 'hospital_bill':
        return <Hospital className="h-5 w-5 text-blue-600" />
      case 'discharge_summary':
        return <FileText className="h-5 w-5 text-green-600" />
      case 'insurance_card':
        return <CreditCard className="h-5 w-5 text-purple-600" />
      default:
        return <FileText className="h-5 w-5 text-gray-600" />
    }
  }

  const formatCurrency = (amount) => {
    if (!amount) return 'N/A'
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
  }

  const formatDocumentType = (type) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ')
  }

  if (!results) return null

  return (
    <div className="space-y-6">
      {/* Header with Download Button */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Claim Processing Results</h2>
          <p className="text-muted-foreground">
            Processed {Object.keys(results.documents || {}).length} documents
          </p>
        </div>
        <Button onClick={onDownloadPDF} className="gap-2">
          <Download className="h-4 w-4" />
          Download PDF Report
        </Button>
      </div>

      {/* Claim Decision */}
      <Card className="border-l-4 border-l-primary">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              {getStatusIcon(results.claim_decision?.status)}
              Claim Decision
            </CardTitle>
            <Badge className={getStatusColor(results.claim_decision?.status)}>
              {results.claim_decision?.status?.toUpperCase()}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <h4 className="font-semibold mb-2">Decision Reason</h4>
              <p className="text-muted-foreground">{results.claim_decision?.reason}</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-semibold mb-1">Confidence Score</h4>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-primary h-2 rounded-full transition-all duration-300"
                      style={{ width: `${(results.claim_decision?.confidence || 0) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium">
                    {((results.claim_decision?.confidence || 0) * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
              
              {results.claim_decision?.recommended_amount && (
                <div>
                  <h4 className="font-semibold mb-1">Recommended Amount</h4>
                  <p className="text-lg font-bold text-green-600">
                    {formatCurrency(results.claim_decision.recommended_amount)}
                  </p>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Documents */}
      <Card>
        <Collapsible 
          open={expandedSections.documents} 
          onOpenChange={() => toggleSection('documents')}
        >
          <CollapsibleTrigger asChild>
            <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors">
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Processed Documents
                </span>
                {expandedSections.documents ? 
                  <ChevronUp className="h-4 w-4" /> : 
                  <ChevronDown className="h-4 w-4" />
                }
              </CardTitle>
            </CardHeader>
          </CollapsibleTrigger>
          
          <CollapsibleContent>
            <CardContent>
              <div className="space-y-4">
                {Object.entries(results.documents || {}).map(([key, doc]) => (
                  <Card key={key} className="border-l-4 border-l-blue-500">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-2">
                          {getDocumentIcon(doc.type)}
                          <h4 className="font-semibold">{formatDocumentType(doc.type)}</h4>
                        </div>
                        <Badge variant="outline">
                          {(doc.confidence * 100).toFixed(1)}% confidence
                        </Badge>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 text-sm">
                        {doc.data?.hospital_name && (
                          <div className="flex items-center gap-2">
                            <Hospital className="h-4 w-4 text-muted-foreground" />
                            <span>{doc.data.hospital_name}</span>
                          </div>
                        )}
                        
                        {doc.data?.patient_name && (
                          <div className="flex items-center gap-2">
                            <User className="h-4 w-4 text-muted-foreground" />
                            <span>{doc.data.patient_name}</span>
                          </div>
                        )}
                        
                        {doc.data?.total_amount && (
                          <div className="flex items-center gap-2">
                            <DollarSign className="h-4 w-4 text-muted-foreground" />
                            <span>{formatCurrency(doc.data.total_amount)}</span>
                          </div>
                        )}
                        
                        {doc.data?.admission_date && (
                          <div className="flex items-center gap-2">
                            <Calendar className="h-4 w-4 text-muted-foreground" />
                            <span>Admitted: {doc.data.admission_date}</span>
                          </div>
                        )}
                        
                        {doc.data?.discharge_date && (
                          <div className="flex items-center gap-2">
                            <Calendar className="h-4 w-4 text-muted-foreground" />
                            <span>Discharged: {doc.data.discharge_date}</span>
                          </div>
                        )}
                        
                        {doc.data?.diagnosis && (
                          <div className="flex items-center gap-2">
                            <FileText className="h-4 w-4 text-muted-foreground" />
                            <span>{doc.data.diagnosis}</span>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </CollapsibleContent>
        </Collapsible>
      </Card>

      {/* Validation Results */}
      <Card>
        <Collapsible 
          open={expandedSections.validation} 
          onOpenChange={() => toggleSection('validation')}
        >
          <CollapsibleTrigger asChild>
            <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors">
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5" />
                  Validation Results
                </span>
                {expandedSections.validation ? 
                  <ChevronUp className="h-4 w-4" /> : 
                  <ChevronDown className="h-4 w-4" />
                }
              </CardTitle>
            </CardHeader>
          </CollapsibleTrigger>
          
          <CollapsibleContent>
            <CardContent>
              <div className="space-y-4">
                {/* Missing Documents */}
                {results.validation?.missing_documents?.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2 text-red-600">Missing Documents</h4>
                    <div className="space-y-2">
                      {results.validation.missing_documents.map((missing, index) => (
                        <div key={index} className="flex items-center gap-2 text-sm">
                          <XCircle className="h-4 w-4 text-red-500" />
                          <span>{missing}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Discrepancies */}
                {results.validation?.discrepancies?.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2 text-yellow-600">Discrepancies Found</h4>
                    <div className="space-y-2">
                      {results.validation.discrepancies.map((discrepancy, index) => (
                        <div key={index} className="flex items-center gap-2 text-sm">
                          <AlertTriangle className="h-4 w-4 text-yellow-500" />
                          <span>{discrepancy}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Warnings */}
                {results.validation?.warnings?.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2 text-blue-600">Warnings</h4>
                    <div className="space-y-2">
                      {results.validation.warnings.map((warning, index) => (
                        <div key={index} className="flex items-center gap-2 text-sm">
                          <AlertTriangle className="h-4 w-4 text-blue-500" />
                          <span>{warning}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* All Clear */}
                {(!results.validation?.missing_documents?.length && 
                  !results.validation?.discrepancies?.length && 
                  !results.validation?.warnings?.length) && (
                  <div className="flex items-center gap-2 text-green-600">
                    <CheckCircle className="h-5 w-5" />
                    <span>All validation checks passed successfully</span>
                  </div>
                )}
              </div>
            </CardContent>
          </CollapsibleContent>
        </Collapsible>
      </Card>
    </div>
  )
}

export default ResultsDisplay

