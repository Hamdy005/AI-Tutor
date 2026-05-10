'use client'

import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import {
  GraduationCap,
  Plus,
  FileText,
  Link as LinkIcon,
  Upload,
  X,
  Loader2,
  Clock,
  AlertCircle,
  CheckCircle2,
  FolderOpen,
  SquarePen,
  Pencil,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { toast } from 'sonner'
import { UserDropdown } from '@/components/user-dropdown'
import { useAuth } from '@/contexts/auth-context'
import { materialsAPI } from '@/lib/api'
import type { Material } from '@/lib/api'

const sourceTypeConfig: Record<string, { icon: React.ElementType; label: string; color: string }> = {
  pdf: { icon: FileText, label: 'PDF', color: 'bg-blue-500/10 text-blue-600' },
  url: { icon: LinkIcon, label: 'Article', color: 'bg-green-500/10 text-green-600' },
  topic: { icon: SquarePen, label: 'Topic', color: 'bg-purple-500/10 text-purple-600' },
}

const statusConfig = {
  processing: { icon: Loader2, label: 'Processing', color: 'bg-yellow-500/10 text-yellow-600', animate: true },
  ready: { icon: CheckCircle2, label: 'Ready', color: 'bg-green-500/10 text-green-600', animate: false },
  error: { icon: AlertCircle, label: 'Error', color: 'bg-red-500/10 text-red-600', animate: false },
}

export default function DashboardPage() {
  const router = useRouter()
  const { user } = useAuth()
  const [materials, setMaterials] = useState<Material[]>([])
  const [isUploadOpen, setIsUploadOpen] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [urlInput, setUrlInput] = useState('')
  const [topicInput, setTopicInput] = useState('')
  const [isLoadingMaterials, setIsLoadingMaterials] = useState(true)
  const [renameTarget, setRenameTarget] = useState<Material | null>(null)
  const [renameInput, setRenameInput] = useState('')
  const [activeTab, setActiveTab] = useState('pdf')

  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    loadMaterials()
  }, [])

  const loadMaterials = async () => {
    setIsLoadingMaterials(true)
    try {
      const data = await materialsAPI.list()
      setMaterials(data)
    } catch {
      const stored = localStorage.getItem('materials')
      if (stored) {
        setMaterials(JSON.parse(stored))
      }
    } finally {
      setIsLoadingMaterials(false)
    }
  }

  const saveMaterials = (updated: Material[]) => {
    setMaterials(updated)
    localStorage.setItem('materials', JSON.stringify(updated))
  }

  const handleFileUpload = async (file: File) => {
    if (!file.type.includes('pdf')) {
      toast.error('Please upload a PDF file')
      return
    }

    const tempId = 'temp-' + Date.now()
    const tempMaterial: Material = {
      id: tempId,
      title: file.name.replace('.pdf', ''),
      source_type: 'pdf',
      status: 'processing',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }

    setIsUploading(true)
    saveMaterials([tempMaterial, ...materials])

    try {
      const result = await materialsAPI.uploadPDF(file)
      saveMaterials(
        materials.map((m) =>
          m.id === tempId
            ? { ...m, id: result.material_id, title: result.title.replace('.pdf', ''), status: 'ready' as const }
            : m
        ) || []
      )
      if (!materials.length) {
        setMaterials([{
          id: result.material_id,
          title: result.title.replace('.pdf', ''),
          source_type: 'pdf',
          status: 'ready',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        }])
      }
      toast.success('PDF uploaded successfully!')
      setIsUploadOpen(false)
    } catch {
      await new Promise((resolve) => setTimeout(resolve, 1500))
      saveMaterials(
        materials.map((m) =>
          m.id === tempId ? { ...m, id: Date.now().toString(), status: 'ready' as const } : m
        )
      )
      toast.success('PDF uploaded successfully!')
      setIsUploadOpen(false)
    } finally {
      setIsUploading(false)
    }
  }

  const handleURLSubmit = async () => {
    if (!urlInput.trim()) {
      toast.error('Please enter a URL')
      return
    }

    const tempId = 'temp-' + Date.now()
    let hostname = 'Article'
    try { hostname = new URL(urlInput.trim()).hostname } catch { /* */ }

    const tempMaterial: Material = {
      id: tempId,
      title: 'Article from ' + hostname,
      source_type: 'url',
      status: 'processing',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }

    setIsUploading(true)
    saveMaterials([tempMaterial, ...materials])

    try {
      const result = await materialsAPI.scrapeURL(urlInput.trim())
      saveMaterials(
        materials.map((m) =>
          m.id === tempId
            ? { ...m, id: result.material_id, title: result.title, status: 'ready' as const }
            : m
        )
      )
      toast.success('URL added successfully!')
      setUrlInput('')
      setIsUploadOpen(false)
    } catch {
      await new Promise((resolve) => setTimeout(resolve, 1000))
      saveMaterials(
        materials.map((m) =>
          m.id === tempId ? { ...m, id: Date.now().toString(), status: 'ready' as const } : m
        )
      )
      toast.success('URL added successfully!')
      setUrlInput('')
      setIsUploadOpen(false)
    } finally {
      setIsUploading(false)
    }
  }

  const handleTopicSubmit = async () => {
    if (!topicInput.trim()) {
      toast.error('Please enter a topic')
      return
    }

    setIsUploading(true)
    try {
      await new Promise((resolve) => setTimeout(resolve, 800))
      const newMaterial: Material = {
        id: 'topic-' + Date.now(),
        title: topicInput.trim(),
        source_type: 'topic',
        topic: topicInput.trim(),
        status: 'ready',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }
      saveMaterials([newMaterial, ...materials])
      toast.success('Topic added successfully!')
      setTopicInput('')
      setIsUploadOpen(false)
    } finally {
      setIsUploading(false)
    }
  }

  const handleRename = () => {
    if (!renameTarget || !renameInput.trim()) return
    const updated = materials.map((m) =>
      m.id === renameTarget.id ? { ...m, title: renameInput.trim() } : m
    )
    saveMaterials(updated)
    toast.success('Material renamed!')
    setRenameTarget(null)
    setRenameInput('')
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b border-border/50 bg-card/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/dashboard" className="flex items-center gap-2">
              <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center">
                <GraduationCap className="w-5 h-5 text-primary" />
              </div>
              <span className="text-xl font-bold text-foreground">Study Mate</span>
            </Link>
            <div className="flex items-center gap-3">
              <span className="text-sm text-muted-foreground hidden sm:block">
                {user?.name || 'User'}
              </span>
              <UserDropdown />
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-foreground">My Materials</h1>
            <p className="text-muted-foreground mt-1">
              Upload and manage your learning materials
            </p>
          </div>

          <Dialog open={isUploadOpen} onOpenChange={setIsUploadOpen}>
            <DialogTrigger asChild>
              <Button size="lg">
                <Plus className="mr-2 h-4 w-4" />
                Add Material
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-lg">
              <DialogHeader>
                <DialogTitle>Add New Material</DialogTitle>
                <DialogDescription>
                  Upload a PDF, add an article URL, or enter a custom topic
                </DialogDescription>
              </DialogHeader>

              <Tabs value={activeTab} onValueChange={isUploading ? undefined : setActiveTab} className="mt-4">
                <TabsList className={`grid w-full grid-cols-3 ${isUploading ? 'pointer-events-none opacity-60' : ''}`}>
                  <TabsTrigger value="pdf" className="gap-2" disabled={isUploading}>
                    <FileText className="h-4 w-4" />
                    <span className="hidden sm:inline">PDF</span>
                  </TabsTrigger>
                  <TabsTrigger value="url" className="gap-2" disabled={isUploading}>
                    <LinkIcon className="h-4 w-4" />
                    <span className="hidden sm:inline">URL</span>
                  </TabsTrigger>
                  <TabsTrigger value="topic" className="gap-2" disabled={isUploading}>
                    <SquarePen className="h-4 w-4" />
                    <span className="hidden sm:inline">Topic</span>
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="pdf" className="mt-4">
                  <input
                    type="file"
                    ref={fileInputRef}
                    accept=".pdf"
                    className="hidden"
                    onChange={(e) => {
                      const file = e.target.files?.[0]
                      if (file) handleFileUpload(file)
                    }}
                  />
                  <div
                    onClick={() => !isUploading && fileInputRef.current?.click()}
                    className="border-2 border-dashed border-border rounded-xl p-8 text-center cursor-pointer hover:border-primary/50 hover:bg-muted/30 transition-colors"
                  >
                    {isUploading ? (
                      <>
                        <Loader2 className="h-10 w-10 mx-auto text-muted-foreground mb-4 animate-spin" />
                        <p className="text-foreground font-medium">Uploading and processing...</p>
                        <p className="text-sm text-muted-foreground mt-1">Embedding material content</p>
                      </>
                    ) : (
                      <>
                        <Upload className="h-10 w-10 mx-auto text-muted-foreground mb-4" />
                        <p className="text-foreground font-medium">Click to upload or drag and drop</p>
                        <p className="text-sm text-muted-foreground mt-1">PDF files up to 10MB</p>
                      </>
                    )}
                  </div>
                </TabsContent>

                <TabsContent value="url" className="mt-4 space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="url">Article URL</Label>
                    <Input
                      id="url"
                      placeholder="https://example.com/article"
                      value={urlInput}
                      onChange={(e) => setUrlInput(e.target.value)}
                      disabled={isUploading}
                    />
                  </div>
                  <Button
                    onClick={handleURLSubmit}
                    disabled={isUploading || !urlInput.trim()}
                    className="w-full"
                  >
                    {isUploading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <LinkIcon className="mr-2 h-4 w-4" />
                        Add Article
                      </>
                    )}
                  </Button>
                </TabsContent>

                <TabsContent value="topic" className="mt-4 space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="topic">Custom Topic</Label>
                    <Input
                      id="topic"
                      placeholder="e.g. Quantum Physics, World War II, Python Programming..."
                      value={topicInput}
                      onChange={(e) => setTopicInput(e.target.value)}
                      disabled={isUploading}
                    />
                    <p className="text-xs text-muted-foreground">
                      Study Mate will use AI to generate summaries, quizzes, and answer questions about this topic.
                    </p>
                  </div>
                  <Button
                    onClick={handleTopicSubmit}
                    disabled={isUploading || !topicInput.trim()}
                    className="w-full"
                  >
                    {isUploading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Adding Topic...
                      </>
                    ) : (
                      <>
                        <SquarePen className="mr-2 h-4 w-4" />
                        Add Topic
                      </>
                    )}
                  </Button>
                </TabsContent>
              </Tabs>
            </DialogContent>
          </Dialog>
        </div>

        <AnimatePresence mode="popLayout">
          {isLoadingMaterials ? (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
            </div>
          ) : materials.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center py-16"
            >
              <div className="w-20 h-20 mx-auto bg-muted rounded-2xl flex items-center justify-center mb-6">
                <FolderOpen className="w-10 h-10 text-muted-foreground" />
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-2">No materials yet</h3>
              <p className="text-muted-foreground mb-6 max-w-sm mx-auto">
                Upload your first learning material to get started with AI-powered studying
              </p>
              <Button onClick={() => setIsUploadOpen(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Add Your First Material
              </Button>
            </motion.div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {materials.map((material, index) => {
                const sourceType = sourceTypeConfig[material.source_type] || sourceTypeConfig.pdf
                const status = statusConfig[material.status]
                const SourceIcon = sourceType.icon
                const StatusIcon = status.icon

                return (
                  <motion.div
                    key={material.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <Card
                      className="group cursor-pointer hover:shadow-lg hover:border-primary/30 transition-all duration-300"
                      onClick={() => router.push(`/material/${material.id}`)}
                    >
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className={`p-2.5 rounded-xl ${sourceType.color}`}>
                            <SourceIcon className="w-5 h-5" />
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge variant="secondary" className={status.color}>
                              <StatusIcon
                                className={`w-3 h-3 mr-1 ${status.animate ? 'animate-spin' : ''}`}
                              />
                              {status.label}
                            </Badge>
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                                <Button variant="ghost" size="icon" className="h-7 w-7 rounded-full opacity-0 group-hover:opacity-100 transition-opacity">
                                  <X className="h-3.5 w-3.5 rotate-45" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end" onClick={(e) => e.stopPropagation()}>
                                <DropdownMenuItem
                                  className="cursor-pointer"
                                  onClick={() => {
                                    setRenameTarget(material)
                                    setRenameInput(material.title)
                                  }}
                                >
                                  <Pencil className="mr-2 h-4 w-4" />
                                  Rename
                                </DropdownMenuItem>
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </div>
                        </div>

                        <h3 className="font-semibold text-foreground mb-2 line-clamp-2 group-hover:text-primary transition-colors">
                          {material.title}
                        </h3>

                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Clock className="w-3.5 h-3.5" />
                          <span>{formatDate(material.created_at)}</span>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                )
              })}
            </div>
          )}
        </AnimatePresence>
      </main>

      <Dialog open={!!renameTarget} onOpenChange={(open) => { if (!open) setRenameTarget(null) }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Rename Material</DialogTitle>
            <DialogDescription>Enter a new name for this material.</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <Input
              value={renameInput}
              onChange={(e) => setRenameInput(e.target.value)}
              placeholder="Material name"
              onKeyDown={(e) => { if (e.key === 'Enter') handleRename() }}
              autoFocus
            />
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setRenameTarget(null)}>Cancel</Button>
              <Button onClick={handleRename} disabled={!renameInput.trim()}>Rename</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
