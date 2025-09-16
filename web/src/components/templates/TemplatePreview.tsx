"use client";

import { useState } from "react";
import Image from 'next/image';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Loader2 } from "lucide-react";

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

interface TemplatePreviewProps {
  template: Template;
  inputs: TemplateInputs;
  onInputChange: (inputs: TemplateInputs) => void;
  onGenerate: () => void;
  generatedAsset: any;
  generating: boolean;
}

function extractInputFields(spec: any): Array<{name: string, label: string, placeholder: string}> {
  const fields: Array<{name: string, label: string, placeholder: string}> = [];
  
  if (!spec || !spec.elements) return fields;
  
  spec.elements.forEach((element: any) => {
    if (element.type === "text" && element.editable) {
      fields.push({
        name: element.id || element.name,
        label: element.label || element.name || "Text Input",
        placeholder: element.placeholder || `Enter ${element.label || "text"}`,
      });
    }
  });
  
  return fields;
}

export default function TemplatePreview({ 
  template, 
  inputs, 
  onInputChange, 
  onGenerate, 
  generatedAsset,
  generating 
}: TemplatePreviewProps) {
  const inputFields = extractInputFields(template.spec);

  const handleInputChange = (field: string, value: string) => {
    const updatedInputs = { ...inputs, [field]: value };
    onInputChange(updatedInputs);
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Input Fields */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Template Inputs</h3>
        {inputFields.length > 0 ? (
          <div className="space-y-3">
            {inputFields.map((field) => (
              <div key={field.name}>
                <Label htmlFor={field.name}>{field.label}</Label>
                {field.name.includes('description') || field.name.includes('content') ? (
                  <Textarea
                    id={field.name}
                    value={inputs[field.name] || ""}
                    onChange={(e) => handleInputChange(field.name, e.target.value)}
                    placeholder={field.placeholder}
                    rows={3}
                  />
                ) : (
                  <Input
                    id={field.name}
                    value={inputs[field.name] || ""}
                    onChange={(e) => handleInputChange(field.name, e.target.value)}
                    placeholder={field.placeholder}
                  />
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground">This template doesn't have any customisable fields.</p>
        )}
        
        <Button 
          onClick={onGenerate}
          disabled={generating}
          className="w-full"
        >
          {generating ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Generating...
            </>
          ) : (
            "Generate Preview"
          )}
        </Button>
      </div>

      {/* Preview */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Preview</h3>
        {generatedAsset ? (
          <div className="border rounded-lg p-4">
            {template.type === "image" ? (
              <Image 
                src={generatedAsset.url} 
                alt="Generated template preview"
                width={600}
                height={400}
                className="rounded object-contain"
                style={{ maxWidth: '100%', height: 'auto' }}
              />
            ) : (
              <video 
                src={generatedAsset.url} 
                controls
                className="max-w-full h-auto rounded"
              />
            )}
            <div className="mt-2 text-sm text-muted-foreground">
              Generated: {new Date(generatedAsset.created_at).toLocaleString()}
            </div>
          </div>
        ) : (
          <div className="border-2 border-dashed border-muted rounded-lg p-8 text-center text-muted-foreground">
            <div className="text-4xl mb-2">🎨</div>
            <p>Click "Generate Preview" to see your customised template</p>
          </div>
        )}
      </div>
    </div>
  );
}
