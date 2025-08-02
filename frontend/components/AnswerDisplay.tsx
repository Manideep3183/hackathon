'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { AnswerResponse } from '@/types/api'
import { formatConfidence, getConfidenceColor, formatProcessingTime } from '@/lib/utils'
import { MessageSquare, Clock, TrendingUp, Eye, EyeOff } from 'lucide-react'
import { useState } from 'react'

interface AnswerDisplayProps {
  answers: AnswerResponse[]
  documentUrl: string
  processingTime?: number
}

interface AnswerCardProps {
  answer: AnswerResponse
  index: number
}

function AnswerCard({ answer, index }: AnswerCardProps) {
  const [showSources, setShowSources] = useState(false)
  
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-2 flex-1">
            <MessageSquare className="h-5 w-5 mt-0.5 shrink-0 text-primary" />
            <span className="text-base font-medium leading-6">
              {answer.question}
            </span>
          </div>
          {answer.confidence !== undefined && (
            <div className="flex items-center gap-1 shrink-0">
              <TrendingUp className="h-4 w-4" />
              <span className={`text-sm font-medium ${getConfidenceColor(answer.confidence)}`}>
                {formatConfidence(answer.confidence)}
              </span>
            </div>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Answer Text */}
        <div className="prose prose-sm max-w-none">
          <p className="text-foreground leading-relaxed whitespace-pre-wrap">
            {answer.answer}
          </p>
        </div>

        {/* Sources Section */}
        {answer.sources && answer.sources.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-medium text-muted-foreground">
                Sources ({answer.sources.length})
              </h4>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowSources(!showSources)}
                className="h-8 px-2"
              >
                {showSources ? (
                  <>
                    <EyeOff className="h-4 w-4 mr-1" />
                    Hide
                  </>
                ) : (
                  <>
                    <Eye className="h-4 w-4 mr-1" />
                    Show
                  </>
                )}
              </Button>
            </div>

            {showSources && (
              <div className="space-y-2">
                {answer.sources.map((source, sourceIndex) => (
                  <div
                    key={sourceIndex}
                    className="p-3 bg-muted rounded-md border-l-4 border-primary/20"
                  >
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {source}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default function AnswerDisplay({ answers, documentUrl, processingTime }: AnswerDisplayProps) {
  if (!answers || answers.length === 0) {
    return null
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <h2 className="text-2xl font-bold">Results</h2>
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <span>Document: {new URL(documentUrl).pathname.split('/').pop()}</span>
          {processingTime && (
            <div className="flex items-center gap-1">
              <Clock className="h-4 w-4" />
              <span>Processed in {formatProcessingTime(processingTime)}</span>
            </div>
          )}
        </div>
      </div>

      {/* Answers */}
      <div className="space-y-4">
        {answers.map((answer, index) => (
          <AnswerCard key={index} answer={answer} index={index} />
        ))}
      </div>

      {/* Summary */}
      <Card className="bg-muted/50">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium">
              {answers.length} question{answers.length !== 1 ? 's' : ''} answered
            </span>
            <span className="text-muted-foreground">
              Average confidence: {
                formatConfidence(
                  answers.reduce((acc, answer) => acc + (answer.confidence || 0), 0) / answers.length
                )
              }
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}