"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

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

interface CreateTemplateFormProps {
  onSubmit: (data: Partial<Template>) => void;
}

export default function CreateTemplateForm({ onSubmit }: CreateTemplateFormProps) {
  const [formData, setFormData] = useState<{
    name: string;
    description: string;
    type: "image" | "video";
    is_public: boolean;
  }>({
    name: "",
    description: "",
    type: "image",
    is_public: false,
  });

  const [templateSpec, setTemplateSpec] = useState({
    width: 1080,
    height: 1080,
    background: "#ffffff",
    elements: [] as any[],
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const templateData = {
      ...formData,
      spec: templateSpec,
    };
    
    onSubmit(templateData);
    
    // Reset form
    setFormData({
      name: "",
      description: "",
      type: "image",
      is_public: false,
    });
    setTemplateSpec({
      width: 1080,
      height: 1080,
      background: "#ffffff",
      elements: [],
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 gap-4">
        <div>
          <Label htmlFor="name">Template Name</Label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="e.g., Instagram Story Template"
            required
          />
        </div>
        
        <div>
          <Label htmlFor="description">Description (Optional)</Label>
          <Textarea
            id="description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="A template for creating engaging Instagram stories with your brand colours and fonts"
            rows={3}
          />
        </div>

        <div>
          <Label htmlFor="type">Content Type</Label>
          <Select
            value={formData.type}
            onValueChange={(value: string) => {
              if (value === "image" || value === "video") {
                setFormData({ ...formData, type: value as "image" | "video" })
              }
            }}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select content type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="image">Image</SelectItem>
              <SelectItem value="video">Video</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="width">Width (px)</Label>
            <Input
              id="width"
              type="number"
              value={templateSpec.width}
              onChange={(e) => setTemplateSpec({ ...templateSpec, width: parseInt(e.target.value) })}
              min="100"
              max="4000"
            />
          </div>
          <div>
            <Label htmlFor="height">Height (px)</Label>
            <Input
              id="height"
              type="number"
              value={templateSpec.height}
              onChange={(e) => setTemplateSpec({ ...templateSpec, height: parseInt(e.target.value) })}
              min="100"
              max="4000"
            />
          </div>
        </div>

        <div>
          <Label htmlFor="background">Background Color</Label>
          <Input
            id="background"
            type="color"
            value={templateSpec.background}
            onChange={(e) => setTemplateSpec({ ...templateSpec, background: e.target.value })}
          />
        </div>
      </div>

      <div className="flex justify-end space-x-2 pt-4">
        <Button type="submit">Create Template</Button>
      </div>
    </form>
  );
}
