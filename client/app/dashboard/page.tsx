'use client'

import { useState, useRef } from 'react'
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { toast } from 'sonner'
import { UserDropdown } from '@/components/user-dropdown'
import type { Material } from '@/lib/api'

// Mock data for demo
const mockMaterials: Material[] = [
  {
    id: '1',
    title: 'Introduction to Machine Learning',
    source_type: 'pdf',
    status: 'ready',
    created_at: '2024-01-15T10:30:00Z',
    updated_at: '2024-01-15T10:35:00Z',
  },
  {
    id: '3',
    title: 'React Best Practices 2024',
    source_type: 'url',
    status: 'processing',
    created_at: '2024-01-13T09:15:00Z',
    updated_at: '2024-01-13T09:15:00Z',
  },
]

const sourceTypeConfig = {
  pdf: { icon: FileText, label: 'PDF', color: 'bg-blue-500/10 text-blue-600' },
  url: { icon: LinkIcon, label: 'Article', color: 'bg-green-500/10 text-green-600' },
}

const statusConfig = {
  processing: { icon: Loader2, label: 'Processing', color: 'bg-yellow-500/10 text-yellow-600', animate: true },
  ready: { icon: CheckCircle2, label: 'Ready', color: 'bg-green-500/10 text-green-600', animate: false },
  error: { icon: AlertCircle, label: 'Error', color: 'bg-red-500/10 text-red-600', animate: false },
}

export default function DashboardPage() {
  const router = useRouter()
  const [materials, setMaterials] = useState<Material[]>(mockMaterials)
  const [isUploadOpen, setIsUploadOpen] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [urlInput, setUrlInput] = useState('')

  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileUpload = async (file: File) => {
    if (!file.type.includes('pdf')) {
      toast.error('Please upload a PDF file')
      return
    }

    setIsUploading(true)
    try {
      // Simulate upload
      await new Promise((resolve) => setTimeout(resolve, 2000))
      
      const newMaterial: Material = {
        id: Date.now().toString(),
        title: file.name.replace('.pdf', ''),
        source_type: 'pdf',
        status: 'processing',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }
      
      setMaterials((prev) => [newMaterial, ...prev])
      toast.success('PDF uploaded successfully!')
      setIsUploadOpen(false)
      
      // Simulate processing completion
      setTimeout(() => {
        setMaterials((prev) =>
          prev.map((m) => (m.id === newMaterial.id ? { ...m, status: 'ready' } : m))
        )
      }, 3000)
    } catch {
      toast.error('Failed to upload PDF')
    } finally {
      setIsUploading(false)
    }
  }

  const handleURLSubmit = async () => {
    if (!urlInput.trim()) {
      toast.error('Please enter a URL')
      return
    }

    setIsUploading(true)
    try {
      await new Promise((resolve) => setTimeout(resolve, 1500))
      
      const newMaterial: Material = {
        id: Date.now().toString(),
        title: 'Article from ' + new URL(urlInput).hostname,
        source_type: 'url',
        status: 'processing',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }
      
      setMaterials((prev) => [newMaterial, ...prev])
      toast.success('URL added successfully!')
      setUrlInput('')
      setIsUploadOpen(false)
      
      setTimeout(() => {
        setMaterials((prev) =>
          prev.map((m) => (m.id === newMaterial.id ? { ...m, status: 'ready' } : m))
        )
      }, 3000)
    } catch {
      toast.error('Invalid URL')
    } finally {
      setIsUploading(false)
    }
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
      {/* Navigation */}
      <nav className="border-b border-border/50 bg-card/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/dashboard" className="flex items-center gap-2">
              <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center">
                <GraduationCap className="w-5 h-5 text-primary" />
              </div>
              <span className="text-xl font-bold text-foreground">Study Mate</span>
            </Link>
            <UserDropdown />
          </div>
        </div>
      </nav>

      {/* Main Content */}
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
                  Upload a PDF or add an article URL
                </DialogDescription>
              </DialogHeader>
              
              <Tabs defaultValue="pdf" className="mt-4">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="pdf" className="gap-2">
                    <FileText className="h-4 w-4" />
                    <span className="hidden sm:inline">PDF</span>
                  </TabsTrigger>
                  <TabsTrigger value="url" className="gap-2">
                    <LinkIcon className="h-4 w-4" />
                    <span className="hidden sm:inline">URL</span>
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
                    onClick={() => fileInputRef.current?.click()}
                    className="border-2 border-dashed border-border rounded-xl p-8 text-center cursor-pointer hover:border-primary/50 hover:bg-muted/30 transition-colors"
                  >
                    <Upload className="h-10 w-10 mx-auto text-muted-foreground mb-4" />
                    <p className="text-foreground font-medium">
                      Click to upload or drag and drop
                    </p>
                    <p className="text-sm text-muted-foreground mt-1">
                      PDF files up to 10MB
                    </p>
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
                        Adding...
                      </>
                    ) : (
                      <>
                        <LinkIcon className="mr-2 h-4 w-4" />
                        Add Article
                      </>
                    )}
                  </Button>
                </TabsContent>
                
              </Tabs>
            </DialogContent>
          </Dialog>
        </div>

        {/* Materials Grid */}
        <AnimatePresence mode="popLayout">
          {materials.length === 0 ? (
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
                const sourceType = sourceTypeConfig[material.source_type]
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
                          <Badge variant="secondary" className={status.color}>
                            <StatusIcon
                              className={`w-3 h-3 mr-1 ${status.animate ? 'animate-spin' : ''}`}
                            />
                            {status.label}
                          </Badge>
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
    </div>
  )
}
