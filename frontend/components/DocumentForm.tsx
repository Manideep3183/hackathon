'use client'

import { useState } from 'react'
import { useForm, useFieldArray } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Plus, Trash2, FileText, Send } from 'lucide-react'
import { isValidUrl } from '@/lib/utils'

const formSchema = z.object({
  documentUrl: z.string().url('Please enter a valid URL'),
  questions: z.array(
    z.object({
      question: z.string().min(1, 'Question cannot be empty').max(1000, 'Question too long'),
    })
  ).min(1, 'At least one question is required').max(10, 'Maximum 10 questions allowed'),
})

type FormData = z.infer<typeof formSchema>

interface DocumentFormProps {
  onSubmit: (data: FormData) => void
  isProcessing: boolean
}

export default function DocumentForm({ onSubmit, isProcessing }: DocumentFormProps) {
  const {
    register,
    handleSubmit,
    control,
    formState: { errors, isValid },
    watch,
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      documentUrl: '',
      questions: [{ question: '' }],
    },
    mode: 'onChange',
  })

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'questions',
  })

  const watchedUrl = watch('documentUrl')

  const addQuestion = () => {
    if (fields.length < 10) {
      append({ question: '' })
    }
  }

  const removeQuestion = (index: number) => {
    if (fields.length > 1) {
      remove(index)
    }
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Document Query
        </CardTitle>
        <CardDescription>
          Enter a document URL and questions to get AI-powered answers
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Document URL Input */}
          <div className="space-y-2">
            <label htmlFor="documentUrl" className="text-sm font-medium">
              Document URL
            </label>
            <Input
              id="documentUrl"
              type="url"
              placeholder="https://example.com/document.pdf"
              {...register('documentUrl')}
              className={errors.documentUrl ? 'border-destructive' : ''}
              disabled={isProcessing}
            />
            {errors.documentUrl && (
              <p className="text-sm text-destructive">{errors.documentUrl.message}</p>
            )}
            {watchedUrl && isValidUrl(watchedUrl) && (
              <p className="text-sm text-green-600 flex items-center gap-1">
                ✓ Valid URL format
              </p>
            )}
          </div>

          {/* Questions Section */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium">
                Questions ({fields.length}/10)
              </label>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={addQuestion}
                disabled={fields.length >= 10 || isProcessing}
                className="h-8"
              >
                <Plus className="h-4 w-4 mr-1" />
                Add Question
              </Button>
            </div>

            <div className="space-y-3">
              {fields.map((field, index) => (
                <div key={field.id} className="flex gap-2">
                  <div className="flex-1">
                    <Input
                      placeholder={`Question ${index + 1}...`}
                      {...register(`questions.${index}.question`)}
                      className={
                        errors.questions?.[index]?.question ? 'border-destructive' : ''
                      }
                      disabled={isProcessing}
                    />
                    {errors.questions?.[index]?.question && (
                      <p className="text-sm text-destructive mt-1">
                        {errors.questions[index]?.question?.message}
                      </p>
                    )}
                  </div>
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    onClick={() => removeQuestion(index)}
                    disabled={fields.length <= 1 || isProcessing}
                    className="h-10 w-10 shrink-0"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>

            {errors.questions && (
              <p className="text-sm text-destructive">{errors.questions.message}</p>
            )}
          </div>

          {/* Submit Button */}
          <Button
            type="submit"
            className="w-full"
            disabled={!isValid || isProcessing}
            size="lg"
          >
            {isProcessing ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Processing...
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Send className="h-4 w-4" />
                Process Document
              </div>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}