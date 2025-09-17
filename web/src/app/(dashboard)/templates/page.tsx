"use client";

import { useState, useEffect } from "react";
import Image from 'next/image';
import dynamic from 'next/dynamic';
import toast from 'react-hot-toast';
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Plus, Search, Filter, Eye, Copy, Edit, Trash2, Image as ImageIcon, Video, Palette } from "lucide-react";

// Dynamic imports for code splitting
const CreateTemplateForm = dynamic(
  () => import('@/components/templates/CreateTemplateForm'),
  { 
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
      </div>
    )
  }
);

const TemplatePreview = dynamic(
  () => import('@/components/templates/TemplatePreview'),
  { 
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
      </div>
    )
  }
);

interface Template {
  id?: string;
  name: string;
  description?: string;
  type: "image" | "video";
  spec: any;
  is_public: boolean;
  created_at?: string;
  created_by?: string;
}

interface TemplateInputs {
  [key: string]: any;
}

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [filteredTemplates, setFilteredTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showPreviewDialog, setShowPreviewDialog] = useState(false);
  const [previewInputs, setPreviewInputs] = useState<TemplateInputs>({});
  const [generatedAsset, setGeneratedAsset] = useState<any>(null);
  const [generating, setGenerating] = useState(false);

  // Skeleton loader component
  const TemplateCardSkeleton = () => (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Skeleton className="h-5 w-5 rounded" />
            <Skeleton className="h-6 w-32" />
          </div>
          <Skeleton className="h-5 w-16 rounded-full" />
        </div>
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
      </CardHeader>
      <CardContent className="pt-0">
        <div className="flex items-center justify-between">
          <Skeleton className="h-4 w-24" />
          <div className="space-x-2">
            <Skeleton className="inline-block h-8 w-16" />
            <Skeleton className="inline-block h-8 w-16" />
            <Skeleton className="inline-block h-8 w-8" />
          </div>
        </div>
      </CardContent>
    </Card>
  );

  // Load templates
  useEffect(() => {
    loadTemplates();
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Cmd/Ctrl + N to create new template  
      if ((event.metaKey || event.ctrlKey) && event.key === 'n') {
        event.preventDefault();
        setShowCreateDialog(true);
      }

      // Escape to close modals
      if (event.key === 'Escape') {
        setShowCreateDialog(false);
        setShowPreviewDialog(false);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Filter templates
  useEffect(() => {
    let filtered = templates;
    
    if (searchTerm) {
      filtered = filtered.filter(t => 
        t.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        t.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    if (typeFilter !== "all") {
      filtered = filtered.filter(t => t.type === typeFilter);
    }
    
    setFilteredTemplates(filtered);
  }, [templates, searchTerm, typeFilter]);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/v1/templates/my");
      const data = await response.json();
      setTemplates(data.templates || []);
    } catch (error) {
      // Error handled by UI state
      toast.error("Failed to load templates");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTemplate = async (templateData: Partial<Template>) => {
    try {
      toast.loading("Creating template...", { id: "create-template" });
      const response = await fetch("/api/v1/templates", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(templateData)
      });
      
      if (response.ok) {
        toast.success("Template created successfully!", { id: "create-template" });
        await loadTemplates();
        setShowCreateDialog(false);
      } else {
        toast.error("Failed to create template", { id: "create-template" });
      }
    } catch (error) {
      // Error handled by UI state
      toast.error("Failed to create template", { id: "create-template" });
    }
  };

  const handleGeneratePreview = async () => {
    if (!selectedTemplate) return;
    
    try {
      setGenerating(true);
      toast.loading("Generating preview...", { id: "generate-preview" });
      const response = await fetch(`/api/v1/templates/${selectedTemplate.id}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ inputs: previewInputs })
      });
      
      if (response.ok) {
        const result = await response.json();
        setGeneratedAsset(result);
        toast.success("Preview generated!", { id: "generate-preview" });
      } else {
        toast.error("Failed to generate preview", { id: "generate-preview" });
      }
    } catch (error) {
      // Error handled by UI state
      toast.error("Failed to generate preview", { id: "generate-preview" });
    } finally {
      setGenerating(false);
    }
  };

  const handleDuplicateTemplate = async (template: Template) => {
    const duplicatedTemplate = {
      ...template,
      name: `${template.name} (Copy)`,
      is_public: false
    };
    delete duplicatedTemplate.id;
    delete duplicatedTemplate.created_at;
    delete duplicatedTemplate.created_by;
    
    await handleCreateTemplate(duplicatedTemplate);
  };

  const getTemplateIcon = (type: string) => {
    return type === "image" ? <ImageIcon className="h-4 w-4" /> : <Video className="h-4 w-4" />;
  };

  const getTemplateColor = (type: string) => {
    return type === "image" ? "bg-blue-100 text-blue-800" : "bg-purple-100 text-purple-800";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Templates</h1>
          <p className="text-muted-foreground">
            Create and manage reusable templates for images and videos
          </p>
        </div>
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Template
              <kbd className="hidden sm:inline-flex ml-2 px-1.5 py-0.5 text-xs font-semibold text-muted-foreground bg-muted/50 rounded">⌘N</kbd>
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create New Template</DialogTitle>
              <DialogDescription>
                Create a reusable template for generating branded content across your campaigns
              </DialogDescription>
            </DialogHeader>
            <CreateTemplateForm onSubmit={handleCreateTemplate} />
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder="Search templates..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-32">
            <SelectValue placeholder="Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="image">Images</SelectItem>
            <SelectItem value="video">Videos</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Templates Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <TemplateCardSkeleton key={i} />
          ))}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTemplates.map((template) => (
              <Card key={template.id} className="hover:shadow-lg transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {getTemplateIcon(template.type)}
                      <CardTitle className="text-lg">{template.name}</CardTitle>
                    </div>
                    <Badge className={getTemplateColor(template.type)}>
                      {template.type}
                    </Badge>
                  </div>
                  {template.description && (
                    <CardDescription>{template.description}</CardDescription>
                  )}
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-muted-foreground">
                      {template.is_public ? "Public" : "Private"}
                    </div>
                    <div className="flex space-x-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setSelectedTemplate(template);
                          setShowPreviewDialog(true);
                        }}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDuplicateTemplate(template)}
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredTemplates.length === 0 && (
        <div className="text-center py-16 px-4">
          <div className="max-w-sm mx-auto">
            <div className="rounded-full bg-muted/20 w-20 h-20 flex items-center justify-center mx-auto mb-6">
              <Palette className="h-10 w-10 text-muted-foreground/60" />
            </div>
            <h3 className="text-xl font-semibold mb-3 text-foreground">
              {searchTerm || typeFilter !== "all" ? "No templates match your search" : "No templates yet"}
            </h3>
            <p className="text-muted-foreground mb-6 leading-relaxed">
              {searchTerm || typeFilter !== "all" 
                ? "Try adjusting your search or filters to find what you're looking for." 
                : "Get started by creating your first reusable template for generating branded content across your campaigns."
              }
            </p>
            {(!searchTerm && typeFilter === "all") && (
              <Button onClick={() => setShowCreateDialog(true)} size="lg">
                <Plus className="h-4 w-4 mr-2" />
                Create Your First Template
              </Button>
            )}
            {(searchTerm || typeFilter !== "all") && (
              <Button 
                variant="outline" 
                onClick={() => {
                  setSearchTerm("");
                  setTypeFilter("all");
                }}
              >
                Clear Filters
              </Button>
            )}
          </div>
        </div>
          )}
        </>
      )}

      {/* Preview Dialog */}
      <Dialog open={showPreviewDialog} onOpenChange={setShowPreviewDialog}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>Preview Template: {selectedTemplate?.name}</DialogTitle>
            <DialogDescription>
              Generate a preview of this template with custom inputs
            </DialogDescription>
          </DialogHeader>
          {selectedTemplate && (
            <TemplatePreview
              template={selectedTemplate}
              inputs={previewInputs}
              onInputChange={setPreviewInputs}
              onGenerate={handleGeneratePreview}
              generatedAsset={generatedAsset}
              generating={generating}
            />
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
