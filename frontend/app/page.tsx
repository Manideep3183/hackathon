'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import DocumentForm from '@/components/DocumentForm'
import AnswerDisplay from '@/components/AnswerDisplay'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import apiClient from '@/lib/api'
import { HackRXRequest, HackRXResponse, ErrorResponse } from '@/types/api'
import { Brain, AlertCircle, Settings, RefreshCw } from 'lucide-react'

export default function HomePage() {
  const [results, setResults] = useState<HackRXResponse | null>(null)
  const [error, setError] = useState<ErrorResponse | null>(null)
  const [bearerToken, setBearerToken] = useState('')
  const [showSettings, setShowSettings] = useState(false)

  // Mutation for processing documents
  const processMutation = useMutation({
    mutationFn: async (data: HackRXRequest): Promise<HackRXResponse> => {
      if (!bearerToken) {
        throw {
          success: false,
          error: 'Bearer token required',
          details: 'Please enter your API bearer token in settings',
        } as ErrorResponse
      }
      
      apiClient.setBearerToken(bearerToken)
      return await apiClient.processDocument(data)
    },
    onSuccess: (data) => {
      setResults(data)
      setError(null)
    },
    onError: (error: ErrorResponse) => {
      setError(error)
      setResults(null)
    },
  })

  const handleFormSubmit = (formData: { documentUrl: string; questions: { question: string }[] }) => {
    const request: HackRXRequest = {
      document_url: formData.documentUrl,
      questions: formData.questions,
    }
    processMutation.mutate(request)
  }

  const handleNewQuery = () => {
    setResults(null)
    setError(null)
    processMutation.reset()
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Brain className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold gradient-text">Aura</h1>
                <p className="text-xs text-gray-500">Powered by Google Gemini</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowSettings(!showSettings)}
              >
                <Settings className="h-4 w-4 mr-1" />
                Settings
              </Button>
              {results && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleNewQuery}
                >
                  <RefreshCw className="h-4 w-4 mr-1" />
                  New Query
                </Button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Settings Panel */}
      {showSettings && (
        <div className="bg-yellow-50 border-b border-yellow-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">API Configuration</CardTitle>
                <CardDescription>
                  Enter your API bearer token to authenticate requests
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-2">
                  <Input
                    type="password"
                    placeholder="Bearer token..."
                    value={bearerToken}
                    onChange={(e) => setBearerToken(e.target.value)}
                    className="flex-1"
                  />
                  <Button
                    variant="outline"
                    onClick={() => setShowSettings(false)}
                  >
                    Done
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-full">
          {/* Left Panel - Form */}
          <div className="space-y-6">
            {!results && (
              <div className="text-center space-y-4 mb-8">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center mx-auto">
                  <Brain className="h-8 w-8 text-white" />
                </div>
                <div>
                  <h2 className="text-3xl font-bold text-gray-900 mb-2">
                    Ask Questions About Your Documents
                  </h2>
                  <p className="text-lg text-gray-600">
                    Upload any document and get instant, intelligent answers powered by Google Gemini AI
                  </p>
                </div>
              </div>
            )}

            <DocumentForm
              onSubmit={handleFormSubmit}
              isProcessing={processMutation.isPending}
            />

            {/* Error Display */}
            {error && (
              <Card className="border-destructive bg-destructive/5">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-destructive">
                    <AlertCircle className="h-5 w-5" />
                    Error
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-destructive font-medium mb-2">
                    {error.error}
                  </p>
                  {error.details && (
                    <p className="text-sm text-muted-foreground">
                      {error.details}
                    </p>
                  )}
                </CardContent>
              </Card>
            )}
          </div>

          {/* Right Panel - Results */}
          <div className="lg:border-l lg:border-gray-200 lg:pl-8">
            {processMutation.isPending && (
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center space-y-4">
                    <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
                    <div>
                      <h3 className="text-lg font-semibold">Processing Document</h3>
                      <p className="text-sm text-muted-foreground">
                        This may take a few moments...
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {results && (
              <AnswerDisplay
                answers={results.answers}
                documentUrl={results.document_url}
                processingTime={results.processing_time_ms}
              />
            )}

            {!results && !processMutation.isPending && !error && (
              <Card className="h-96 flex items-center justify-center">
                <CardContent>
                  <div className="text-center text-muted-foreground">
                    <Brain className="h-12 w-12 mx-auto mb-4 opacity-20" />
                    <p>Results will appear here after processing</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white/80 backdrop-blur-sm border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-500">
            <p>Aura - Intelligent Document Query System</p>
            <p>Powered by Google Gemini AI | Built with Next.js & FastAPI</p>
          </div>
        </div>
      </footer>
    </div>
  )
}