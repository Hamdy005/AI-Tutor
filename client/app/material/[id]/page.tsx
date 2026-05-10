'use client'

import { useState, useRef, useEffect, use } from 'react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import {
  GraduationCap,
  ArrowLeft,
  FileText,
  Link as LinkIcon,
  Sparkles,
  MessageSquare,
  Brain,
  Loader2,
  Send,
  RefreshCw,
  CheckCircle2,
  XCircle,
  ChevronRight,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Slider } from '@/components/ui/slider'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Skeleton } from '@/components/ui/skeleton'
import { toast } from 'sonner'
import { UserDropdown } from '@/components/user-dropdown'
import type { Material, ChatMessage, QuizQuestion, QuizResult } from '@/lib/api'

// Mock data
const mockMaterial: Material = {
  id: '1',
  title: 'Introduction to Machine Learning',
  source_type: 'pdf',
  status: 'ready',
  created_at: '2024-01-15T10:30:00Z',
  updated_at: '2024-01-15T10:35:00Z',
}

const mockSummary = `Machine Learning (ML) is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. This document covers the fundamental concepts of ML, including:

**Key Concepts:**
- **Supervised Learning**: Training models on labeled data to make predictions
- **Unsupervised Learning**: Finding patterns in unlabeled data
- **Reinforcement Learning**: Learning through trial and error with rewards

**Common Algorithms:**
1. Linear Regression for continuous predictions
2. Decision Trees for classification tasks
3. Neural Networks for complex pattern recognition

**Applications:**
Machine learning is used in image recognition, natural language processing, recommendation systems, and autonomous vehicles. The field continues to evolve rapidly with new architectures and techniques being developed.

**Getting Started:**
To begin with ML, start with understanding basic statistics, linear algebra, and Python programming. Popular frameworks include TensorFlow, PyTorch, and scikit-learn.`

const sourceTypeConfig = {
  pdf: { icon: FileText, label: 'PDF', color: 'bg-blue-500/10 text-blue-600' },
  url: { icon: LinkIcon, label: 'Article', color: 'bg-green-500/10 text-green-600' },
}

export default function MaterialDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const router = useRouter()
  const searchParams = useSearchParams()
  const activeTab = searchParams.get('tab') || 'summary'

  const [material] = useState<Material>(mockMaterial)
  const sourceType = sourceTypeConfig[material.source_type]
  const SourceIcon = sourceType.icon

  const handleTabChange = (value: string) => {
    router.push(`/material/${id}?tab=${value}`, { scroll: false })
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b border-border/50 bg-card/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/dashboard" className="flex items-center gap-2">
              <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center">
                <GraduationCap className="w-5 h-5 text-primary" />
              </div>
              <span className="text-xl font-bold text-foreground">AI Tutor</span>
            </Link>
            <UserDropdown />
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back button and title */}
        <div className="mb-6">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push('/dashboard')}
            className="mb-4 -ml-2"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Materials
          </Button>
          
          <div className="flex items-start gap-4">
            <div className={`p-3 rounded-xl ${sourceType.color}`}>
              <SourceIcon className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-foreground">
                {material.title}
              </h1>
              <div className="flex items-center gap-2 mt-2">
                <Badge variant="secondary" className={sourceType.color}>
                  {sourceType.label}
                </Badge>
                <span className="text-sm text-muted-foreground">
                  Added {new Date(material.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={handleTabChange} className="mt-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="summary" className="gap-2">
              <Sparkles className="h-4 w-4" />
              <span className="hidden sm:inline">Summary</span>
            </TabsTrigger>
            <TabsTrigger value="chat" className="gap-2">
              <MessageSquare className="h-4 w-4" />
              <span className="hidden sm:inline">Chat</span>
            </TabsTrigger>
            <TabsTrigger value="quiz" className="gap-2">
              <Brain className="h-4 w-4" />
              <span className="hidden sm:inline">Quiz</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="summary" className="mt-6">
            <SummaryTab materialId={id} />
          </TabsContent>

          <TabsContent value="chat" className="mt-6">
            <ChatTab materialId={id} />
          </TabsContent>

          <TabsContent value="quiz" className="mt-6">
            <QuizTab materialId={id} sourceType={material.source_type} />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}

// Summary Tab Component
function SummaryTab({ materialId }: { materialId: string }) {
  const [summary, setSummary] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)

  const generateSummary = async () => {
    setIsGenerating(true)
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 2000))
      setSummary(mockSummary)
      toast.success('Summary generated!')
    } catch {
      toast.error('Failed to generate summary')
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {!summary ? (
        <Card className="text-center py-12">
          <CardContent>
            <div className="w-16 h-16 mx-auto bg-primary/10 rounded-2xl flex items-center justify-center mb-6">
              <Sparkles className="w-8 h-8 text-primary" />
            </div>
            <h3 className="text-xl font-semibold text-foreground mb-2">
              Generate AI Summary
            </h3>
            <p className="text-muted-foreground mb-6 max-w-md mx-auto">
              Let AI analyze your material and create a comprehensive summary with key points and insights.
            </p>
            <Button onClick={generateSummary} disabled={isGenerating} size="lg">
              {isGenerating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Generate Summary
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>AI-Generated Summary</CardTitle>
              <CardDescription>
                Key points and insights from your material
              </CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={generateSummary} disabled={isGenerating}>
              <RefreshCw className={`mr-2 h-4 w-4 ${isGenerating ? 'animate-spin' : ''}`} />
              Regenerate
            </Button>
          </CardHeader>
          <CardContent>
            <div className="prose prose-slate dark:prose-invert max-w-none">
              {summary.split('\n').map((paragraph, index) => {
                if (paragraph.startsWith('**') && paragraph.endsWith('**')) {
                  return (
                    <h3 key={index} className="text-lg font-semibold mt-6 mb-2 text-foreground">
                      {paragraph.replace(/\*\*/g, '')}
                    </h3>
                  )
                }
                if (paragraph.startsWith('- **')) {
                  const content = paragraph.replace(/^- \*\*/, '').replace(/\*\*:/, ':')
                  const [title, ...rest] = content.split(':')
                  return (
                    <p key={index} className="flex items-start gap-2 text-foreground">
                      <ChevronRight className="h-4 w-4 mt-1 text-primary flex-shrink-0" />
                      <span>
                        <strong>{title}:</strong>
                        {rest.join(':')}
                      </span>
                    </p>
                  )
                }
                if (paragraph.match(/^\d+\./)) {
                  return (
                    <p key={index} className="ml-4 text-foreground">
                      {paragraph}
                    </p>
                  )
                }
                return paragraph ? (
                  <p key={index} className="text-foreground leading-relaxed">
                    {paragraph}
                  </p>
                ) : null
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </motion.div>
  )
}

// Chat Tab Component
function ChatTab({ materialId }: { materialId: string }) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      // Simulate API response
      await new Promise((resolve) => setTimeout(resolve, 1500))

      const aiResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `That's a great question about "${userMessage.content.slice(0, 30)}..."! 

Based on the material, here's what I can tell you:

Machine learning algorithms learn patterns from data to make predictions or decisions. The key aspects include:

1. **Data Processing**: Preparing and cleaning your dataset
2. **Model Selection**: Choosing the right algorithm for your task
3. **Training**: Feeding data to the model to learn patterns
4. **Evaluation**: Testing the model's performance

Would you like me to elaborate on any of these points?`,
        timestamp: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, aiResponse])
    } catch {
      toast.error('Failed to send message')
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <Card className="h-[600px] flex flex-col">
        <CardHeader className="border-b">
          <CardTitle className="text-lg">Chat with AI Tutor</CardTitle>
          <CardDescription>
            Ask questions about your learning material
          </CardDescription>
        </CardHeader>
        
        <ScrollArea ref={scrollRef} className="flex-1 p-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center py-8">
              <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mb-4">
                <MessageSquare className="w-8 h-8 text-primary" />
              </div>
              <h3 className="font-semibold text-foreground mb-2">
                Start a conversation
              </h3>
              <p className="text-sm text-muted-foreground max-w-sm">
                Ask any question about your material and get detailed explanations from the AI tutor.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <AnimatePresence>
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                        message.role === 'user'
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted text-foreground'
                      }`}
                    >
                      <p className="whitespace-pre-wrap text-sm leading-relaxed">
                        {message.content}
                      </p>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex justify-start"
                >
                  <div className="bg-muted rounded-2xl px-4 py-3">
                    <div className="flex gap-1">
                      <span className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <span className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <span className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          )}
        </ScrollArea>
        
        <div className="p-4 border-t">
          <form
            onSubmit={(e) => {
              e.preventDefault()
              handleSend()
            }}
            className="flex gap-2"
          >
            <Input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question..."
              disabled={isLoading}
              className="flex-1"
            />
            <Button type="submit" disabled={!input.trim() || isLoading}>
              <Send className="h-4 w-4" />
              <span className="sr-only">Send message</span>
            </Button>
          </form>
        </div>
      </Card>
    </motion.div>
  )
}

// Quiz Tab Component
function QuizTab({ materialId, sourceType }: { materialId: string; sourceType: string }) {
  const [difficulty, setDifficulty] = useState<'easy' | 'medium' | 'hard'>('medium')
  const [questionCount, setQuestionCount] = useState(5)
  const [isGenerating, setIsGenerating] = useState(false)
  const [questions, setQuestions] = useState<QuizQuestion[]>([])
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [result, setResult] = useState<QuizResult | null>(null)

  const generateQuiz = async () => {
    setIsGenerating(true)
    setResult(null)
    setAnswers({})
    
    try {
      await new Promise((resolve) => setTimeout(resolve, 2000))
      
      // Mock questions
      const mockQuestions: QuizQuestion[] = [
        {
          id: '1',
          type: 'mcq',
          question: 'What is the main difference between supervised and unsupervised learning?',
          options: [
            'Supervised learning uses labeled data, unsupervised does not',
            'Unsupervised learning is faster',
            'Supervised learning only works with images',
            'There is no difference',
          ],
          correct_answer: 'Supervised learning uses labeled data, unsupervised does not',
        },
        {
          id: '2',
          type: 'mcq',
          question: 'Which algorithm is commonly used for classification tasks?',
          options: ['Linear Regression', 'Decision Trees', 'K-means Clustering', 'PCA'],
          correct_answer: 'Decision Trees',
        },
        {
          id: '3',
          type: 'true_false',
          question: 'Neural networks can only be used for image recognition.',
          correct_answer: 'false',
        },
        {
          id: '4',
          type: 'mcq',
          question: 'What is reinforcement learning?',
          options: [
            'Learning from labeled examples',
            'Learning through trial and error with rewards',
            'Clustering similar data points',
            'Reducing data dimensions',
          ],
          correct_answer: 'Learning through trial and error with rewards',
        },
        {
          id: '5',
          type: 'true_false',
          question: 'TensorFlow and PyTorch are popular machine learning frameworks.',
          correct_answer: 'true',
        },
      ].slice(0, questionCount)
      
      setQuestions(mockQuestions)
      toast.success('Quiz generated!')
    } catch {
      toast.error('Failed to generate quiz')
    } finally {
      setIsGenerating(false)
    }
  }

  const submitQuiz = () => {
    const results: QuizResult['answers'] = questions.map((q) => ({
      question_id: q.id,
      user_answer: answers[q.id] || '',
      correct_answer: q.correct_answer,
      is_correct: answers[q.id] === q.correct_answer,
    }))

    const correct = results.filter((r) => r.is_correct).length

    setResult({
      total: questions.length,
      correct,
      incorrect: questions.length - correct,
      score: Math.round((correct / questions.length) * 100),
      answers: results,
    })

    toast.success(`Quiz completed! Score: ${Math.round((correct / questions.length) * 100)}%`)
  }

  const resetQuiz = () => {
    setQuestions([])
    setAnswers({})
    setResult(null)
  }

  if (questions.length > 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-6"
      >
        {result ? (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {result.score >= 70 ? (
                  <CheckCircle2 className="h-6 w-6 text-green-500" />
                ) : (
                  <XCircle className="h-6 w-6 text-red-500" />
                )}
                Quiz Results
              </CardTitle>
              <CardDescription>
                You scored {result.correct} out of {result.total} questions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="text-center p-4 bg-muted rounded-xl">
                  <p className="text-3xl font-bold text-foreground">{result.score}%</p>
                  <p className="text-sm text-muted-foreground">Score</p>
                </div>
                <div className="text-center p-4 bg-green-500/10 rounded-xl">
                  <p className="text-3xl font-bold text-green-600">{result.correct}</p>
                  <p className="text-sm text-muted-foreground">Correct</p>
                </div>
                <div className="text-center p-4 bg-red-500/10 rounded-xl">
                  <p className="text-3xl font-bold text-red-600">{result.incorrect}</p>
                  <p className="text-sm text-muted-foreground">Incorrect</p>
                </div>
              </div>
              
              <div className="space-y-4">
                {questions.map((question, index) => {
                  const answer = result.answers.find((a) => a.question_id === question.id)
                  return (
                    <div
                      key={question.id}
                      className={`p-4 rounded-xl border ${
                        answer?.is_correct ? 'border-green-500/30 bg-green-500/5' : 'border-red-500/30 bg-red-500/5'
                      }`}
                    >
                      <div className="flex items-start gap-2">
                        {answer?.is_correct ? (
                          <CheckCircle2 className="h-5 w-5 text-green-500 mt-0.5" />
                        ) : (
                          <XCircle className="h-5 w-5 text-red-500 mt-0.5" />
                        )}
                        <div>
                          <p className="font-medium text-foreground">
                            {index + 1}. {question.question}
                          </p>
                          <p className="text-sm text-muted-foreground mt-1">
                            Your answer: {answer?.user_answer || 'Not answered'}
                          </p>
                          {!answer?.is_correct && (
                            <p className="text-sm text-green-600 mt-1">
                              Correct answer: {question.correct_answer}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
              
              <Button onClick={resetQuiz} className="w-full mt-6">
                Try Another Quiz
              </Button>
            </CardContent>
          </Card>
        ) : (
          <>
            <Card>
              <CardHeader>
                <CardTitle>Quiz</CardTitle>
                <CardDescription>
                  {questions.length} questions | {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)} difficulty
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {questions.map((question, index) => (
                  <div key={question.id} className="space-y-3">
                    <p className="font-medium text-foreground">
                      {index + 1}. {question.question}
                    </p>
                    
                    {question.type === 'mcq' ? (
                      <RadioGroup
                        value={answers[question.id] || ''}
                        onValueChange={(value) =>
                          setAnswers((prev) => ({ ...prev, [question.id]: value }))
                        }
                        className="space-y-2"
                      >
                        {question.options?.map((option, optIndex) => (
                          <div key={optIndex} className="flex items-center space-x-2">
                            <RadioGroupItem
                              value={option}
                              id={`${question.id}-${optIndex}`}
                            />
                            <Label
                              htmlFor={`${question.id}-${optIndex}`}
                              className="cursor-pointer flex-1"
                            >
                              {option}
                            </Label>
                          </div>
                        ))}
                      </RadioGroup>
                    ) : (
                      <RadioGroup
                        value={answers[question.id] || ''}
                        onValueChange={(value) =>
                          setAnswers((prev) => ({ ...prev, [question.id]: value }))
                        }
                        className="flex gap-4"
                      >
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="true" id={`${question.id}-true`} />
                          <Label htmlFor={`${question.id}-true`} className="cursor-pointer">
                            True
                          </Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="false" id={`${question.id}-false`} />
                          <Label htmlFor={`${question.id}-false`} className="cursor-pointer">
                            False
                          </Label>
                        </div>
                      </RadioGroup>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
            
            <Button
              onClick={submitQuiz}
              disabled={Object.keys(answers).length !== questions.length}
              className="w-full"
              size="lg"
            >
              Submit Answers
            </Button>
          </>
        )}
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <Card>
        <CardHeader>
          <CardTitle>Generate Quiz</CardTitle>
          <CardDescription>
            Configure your quiz settings and test your knowledge
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-3">
            <Label>Difficulty Level</Label>
            <div className="flex gap-2">
              {(['easy', 'medium', 'hard'] as const).map((level) => (
                <Button
                  key={level}
                  variant={difficulty === level ? 'default' : 'outline'}
                  onClick={() => setDifficulty(level)}
                  className="flex-1"
                >
                  {level.charAt(0).toUpperCase() + level.slice(1)}
                </Button>
              ))}
            </div>
          </div>
          
          <div className="space-y-3">
            <div className="flex justify-between">
              <Label>Number of Questions</Label>
              <span className="text-sm text-muted-foreground">{questionCount}</span>
            </div>
            <Slider
              value={[questionCount]}
              onValueChange={([value]) => setQuestionCount(value)}
              min={3}
              max={20}
              step={1}
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>3</span>
              <span>20</span>
            </div>
          </div>
          
          <div className="space-y-3">
            <Label>Source</Label>
            <div className="p-3 bg-muted rounded-xl flex items-center gap-3">
              {sourceType === 'pdf' && <FileText className="h-5 w-5 text-blue-500" />}
              {sourceType === 'url' && <LinkIcon className="h-5 w-5 text-green-500" />}
              <span className="text-sm text-foreground capitalize">{sourceType}</span>
            </div>
          </div>
          
          <Button onClick={generateQuiz} disabled={isGenerating} className="w-full" size="lg">
            {isGenerating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating Quiz...
              </>
            ) : (
              <>
                <Brain className="mr-2 h-4 w-4" />
                Generate Quiz
              </>
            )}
          </Button>
        </CardContent>
      </Card>
    </motion.div>
  )
}
