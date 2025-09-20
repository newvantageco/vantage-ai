"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import {
  Plus,
  Minus,
  Trash2,
  Save,
  X,
  ArrowRight,
  Settings,
  AlertCircle,
  CheckCircle,
  TestTube,
  Target,
  Users,
  Clock,
  DollarSign,
  Zap,
  BarChart3
} from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "react-hot-toast";

interface ABTestBuilderProps {
  onSave: (test: any) => void;
  onCancel: () => void;
  initialTest?: any;
}

interface ABTestVariant {
  id: string;
  name: string;
  description: string;
  variant_data: Record<string, any>;
  traffic_percentage: number;
}

const testTypes = [
  { 
    value: "content", 
    label: "Content", 
    description: "Test different content variations",
    icon: Target,
    color: "bg-blue-100 text-blue-800"
  },
  { 
    value: "timing", 
    label: "Timing", 
    description: "Test different posting times",
    icon: Clock,
    color: "bg-green-100 text-green-800"
  },
  { 
    value: "audience", 
    label: "Audience", 
    description: "Test different audience segments",
    icon: Users,
    color: "bg-purple-100 text-purple-800"
  },
  { 
    value: "creative", 
    label: "Creative", 
    description: "Test different creative elements",
    icon: Zap,
    color: "bg-yellow-100 text-yellow-800"
  },
  { 
    value: "landing_page", 
    label: "Landing Page", 
    description: "Test different landing pages",
    icon: BarChart3,
    color: "bg-orange-100 text-orange-800"
  },
  { 
    value: "cta", 
    label: "Call-to-Action", 
    description: "Test different CTA buttons",
    icon: Target,
    color: "bg-pink-100 text-pink-800"
  }
];

export function ABTestBuilder({ onSave, onCancel, initialTest }: ABTestBuilderProps) {
  const [step, setStep] = useState(1);
  const [testName, setTestName] = useState(initialTest?.name || "");
  const [testDescription, setTestDescription] = useState(initialTest?.description || "");
  const [hypothesis, setHypothesis] = useState(initialTest?.hypothesis || "");
  const [testType, setTestType] = useState(initialTest?.test_type || "");
  const [trafficAllocation, setTrafficAllocation] = useState(initialTest?.traffic_allocation || 0.5);
  const [minimumSampleSize, setMinimumSampleSize] = useState(initialTest?.minimum_sample_size || 100);
  const [significanceLevel, setSignificanceLevel] = useState(initialTest?.significance_level || 0.05);
  const [plannedDurationDays, setPlannedDurationDays] = useState(initialTest?.planned_duration_days || 7);
  const [variants, setVariants] = useState<ABTestVariant[]>(initialTest?.variants || []);
  const [enabled, setEnabled] = useState(initialTest?.enabled ?? true);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateStep = (stepNumber: number): boolean => {
    const newErrors: Record<string, string> = {};

    if (stepNumber === 1) {
      if (!testName.trim()) newErrors.name = "Test name is required";
      if (!testDescription.trim()) newErrors.description = "Test description is required";
      if (!hypothesis.trim()) newErrors.hypothesis = "Hypothesis is required";
      if (!testType) newErrors.test_type = "Test type is required";
    } else if (stepNumber === 2) {
      if (variants.length < 2) newErrors.variants = "At least 2 variants are required";
      if (variants.length > 10) newErrors.variants = "Maximum 10 variants allowed";
      
      // Check traffic allocation
      const totalTraffic = variants.reduce((sum, variant) => sum + variant.traffic_percentage, 0);
      if (Math.abs(totalTraffic - 1.0) > 0.01) {
        newErrors.traffic_allocation = "Traffic percentages must sum to 100%";
      }
      
      variants.forEach((variant, index) => {
        if (!variant.name.trim()) newErrors[`variant_${index}_name`] = "Variant name is required";
        if (variant.traffic_percentage <= 0) newErrors[`variant_${index}_traffic`] = "Traffic percentage must be greater than 0";
      });
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(step)) {
      setStep(step + 1);
    }
  };

  const handlePrevious = () => {
    setStep(step - 1);
  };

  const handleSave = () => {
    if (validateStep(1) && validateStep(2)) {
      const test = {
        id: initialTest?.id || `ab_test_${Date.now()}`,
        name: testName,
        description: testDescription,
        hypothesis,
        test_type: testType,
        traffic_allocation: trafficAllocation,
        minimum_sample_size: minimumSampleSize,
        significance_level: significanceLevel,
        planned_duration_days: plannedDurationDays,
        status: "draft",
        enabled,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        variants: variants.map((variant, index) => ({
          ...variant,
          id: variant.id || `variant_${index}`,
          ab_test_id: initialTest?.id || `ab_test_${Date.now()}`,
          status: "active",
          impressions: 0,
          clicks: 0,
          conversions: 0,
          engagement_rate: 0,
          conversion_rate: 0,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }))
      };
      onSave(test);
    }
  };

  const addVariant = () => {
    const newVariant: ABTestVariant = {
      id: `variant_${Date.now()}`,
      name: "",
      description: "",
      variant_data: {},
      traffic_percentage: 0.5
    };
    setVariants([...variants, newVariant]);
  };

  const updateVariant = (id: string, field: string, value: any) => {
    setVariants(variants.map(variant => 
      variant.id === id ? { ...variant, [field]: value } : variant
    ));
  };

  const removeVariant = (id: string) => {
    setVariants(variants.filter(variant => variant.id !== id));
  };

  const distributeTrafficEvenly = () => {
    const evenPercentage = 1.0 / variants.length;
    setVariants(variants.map(variant => ({
      ...variant,
      traffic_percentage: evenPercentage
    })));
  };

  const renderVariantConfiguration = (variant: ABTestVariant, index: number) => {
    switch (testType) {
      case "content":
        return (
          <div className="space-y-4">
            <div>
              <Label>Headline</Label>
              <Input
                value={variant.variant_data.headline || ""}
                onChange={(e) => updateVariant(variant.id, "variant_data", { 
                  ...variant.variant_data, 
                  headline: e.target.value 
                })}
                placeholder="Enter headline"
              />
            </div>
            <div>
              <Label>Description</Label>
              <Textarea
                value={variant.variant_data.description || ""}
                onChange={(e) => updateVariant(variant.id, "variant_data", { 
                  ...variant.variant_data, 
                  description: e.target.value 
                })}
                placeholder="Enter description"
              />
            </div>
            <div>
              <Label>Hashtags</Label>
              <Input
                value={variant.variant_data.hashtags || ""}
                onChange={(e) => updateVariant(variant.id, "variant_data", { 
                  ...variant.variant_data, 
                  hashtags: e.target.value 
                })}
                placeholder="Enter hashtags (comma-separated)"
              />
            </div>
          </div>
        );
      
      case "timing":
        return (
          <div className="space-y-4">
            <div>
              <Label>Posting Time</Label>
              <Input
                type="time"
                value={variant.variant_data.posting_time || ""}
                onChange={(e) => updateVariant(variant.id, "variant_data", { 
                  ...variant.variant_data, 
                  posting_time: e.target.value 
                })}
              />
            </div>
            <div>
              <Label>Day of Week</Label>
              <Select
                value={variant.variant_data.day_of_week || ""}
                onValueChange={(value) => updateVariant(variant.id, "variant_data", { 
                  ...variant.variant_data, 
                  day_of_week: value 
                })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select day" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="monday">Monday</SelectItem>
                  <SelectItem value="tuesday">Tuesday</SelectItem>
                  <SelectItem value="wednesday">Wednesday</SelectItem>
                  <SelectItem value="thursday">Thursday</SelectItem>
                  <SelectItem value="friday">Friday</SelectItem>
                  <SelectItem value="saturday">Saturday</SelectItem>
                  <SelectItem value="sunday">Sunday</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        );
      
      case "audience":
        return (
          <div className="space-y-4">
            <div>
              <Label>Age Range</Label>
              <div className="flex space-x-2">
                <Input
                  type="number"
                  placeholder="Min age"
                  value={variant.variant_data.min_age || ""}
                  onChange={(e) => updateVariant(variant.id, "variant_data", { 
                    ...variant.variant_data, 
                    min_age: parseInt(e.target.value) || 0 
                  })}
                />
                <Input
                  type="number"
                  placeholder="Max age"
                  value={variant.variant_data.max_age || ""}
                  onChange={(e) => updateVariant(variant.id, "variant_data", { 
                    ...variant.variant_data, 
                    max_age: parseInt(e.target.value) || 0 
                  })}
                />
              </div>
            </div>
            <div>
              <Label>Interests</Label>
              <Input
                value={variant.variant_data.interests || ""}
                onChange={(e) => updateVariant(variant.id, "variant_data", { 
                  ...variant.variant_data, 
                  interests: e.target.value 
                })}
                placeholder="Enter interests (comma-separated)"
              />
            </div>
            <div>
              <Label>Location</Label>
              <Input
                value={variant.variant_data.location || ""}
                onChange={(e) => updateVariant(variant.id, "variant_data", { 
                  ...variant.variant_data, 
                  location: e.target.value 
                })}
                placeholder="Enter location"
              />
            </div>
          </div>
        );
      
      case "creative":
        return (
          <div className="space-y-4">
            <div>
              <Label>Image Style</Label>
              <Select
                value={variant.variant_data.image_style || ""}
                onValueChange={(value) => updateVariant(variant.id, "variant_data", { 
                  ...variant.variant_data, 
                  image_style: value 
                })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select image style" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="minimal">Minimal</SelectItem>
                  <SelectItem value="bold">Bold</SelectItem>
                  <SelectItem value="vintage">Vintage</SelectItem>
                  <SelectItem value="modern">Modern</SelectItem>
                  <SelectItem value="colorful">Colorful</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Color Scheme</Label>
              <Input
                value={variant.variant_data.color_scheme || ""}
                onChange={(e) => updateVariant(variant.id, "variant_data", { 
                  ...variant.variant_data, 
                  color_scheme: e.target.value 
                })}
                placeholder="Enter color scheme"
              />
            </div>
            <div>
              <Label>Font Style</Label>
              <Select
                value={variant.variant_data.font_style || ""}
                onValueChange={(value) => updateVariant(variant.id, "variant_data", { 
                  ...variant.variant_data, 
                  font_style: value 
                })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select font style" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="serif">Serif</SelectItem>
                  <SelectItem value="sans-serif">Sans-serif</SelectItem>
                  <SelectItem value="script">Script</SelectItem>
                  <SelectItem value="display">Display</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        );
      
      case "cta":
        return (
          <div className="space-y-4">
            <div>
              <Label>Button Text</Label>
              <Input
                value={variant.variant_data.button_text || ""}
                onChange={(e) => updateVariant(variant.id, "variant_data", { 
                  ...variant.variant_data, 
                  button_text: e.target.value 
                })}
                placeholder="Enter button text"
              />
            </div>
            <div>
              <Label>Button Color</Label>
              <Input
                type="color"
                value={variant.variant_data.button_color || "#3B82F6"}
                onChange={(e) => updateVariant(variant.id, "variant_data", { 
                  ...variant.variant_data, 
                  button_color: e.target.value 
                })}
              />
            </div>
            <div>
              <Label>Button Size</Label>
              <Select
                value={variant.variant_data.button_size || ""}
                onValueChange={(value) => updateVariant(variant.id, "variant_data", { 
                  ...variant.variant_data, 
                  button_size: value 
                })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select button size" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="small">Small</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="large">Large</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        );
      
      default:
        return (
          <div className="space-y-4">
            <div>
              <Label>Custom Configuration</Label>
              <Textarea
                value={JSON.stringify(variant.variant_data, null, 2)}
                onChange={(e) => {
                  try {
                    const data = JSON.parse(e.target.value);
                    updateVariant(variant.id, "variant_data", data);
                  } catch (error) {
                    // Invalid JSON, keep the text for editing
                  }
                }}
                placeholder="Enter custom configuration as JSON"
                className="font-mono text-sm"
              />
            </div>
          </div>
        );
    }
  };

  const getTestTypeIcon = (type: string) => {
    const typeConfig = testTypes.find(t => t.value === type);
    const Icon = typeConfig?.icon || TestTube;
    return <Icon className="h-5 w-5" />;
  };

  const getTestTypeColor = (type: string) => {
    const typeConfig = testTypes.find(t => t.value === type);
    return typeConfig?.color || "bg-gray-100 text-gray-800";
  };

  return (
    <div className="space-y-6">
      {/* Progress Indicator */}
      <div className="flex items-center space-x-4">
        {[1, 2].map((stepNumber) => (
          <div key={stepNumber} className="flex items-center">
            <div className={cn(
              "flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium",
              step >= stepNumber 
                ? "bg-primary text-primary-foreground" 
                : "bg-muted text-muted-foreground"
            )}>
              {step > stepNumber ? <CheckCircle className="h-4 w-4" /> : stepNumber}
            </div>
            {stepNumber < 2 && (
              <ArrowRight className="h-4 w-4 mx-2 text-muted-foreground" />
            )}
          </div>
        ))}
      </div>

      {/* Step 1: Basic Information */}
      {step === 1 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Settings className="h-5 w-5 mr-2" />
              Basic Information
            </CardTitle>
            <CardDescription>
              Set up the basic details for your A/B test
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="test-name">Test Name *</Label>
              <Input
                id="test-name"
                value={testName}
                onChange={(e) => setTestName(e.target.value)}
                placeholder="e.g., Headline A/B Test"
                className={errors.name ? "border-red-500" : ""}
              />
              {errors.name && (
                <p className="text-sm text-red-500 flex items-center">
                  <AlertCircle className="h-4 w-4 mr-1" />
                  {errors.name}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="test-description">Description *</Label>
              <Textarea
                id="test-description"
                value={testDescription}
                onChange={(e) => setTestDescription(e.target.value)}
                placeholder="Describe what you're testing..."
                className={errors.description ? "border-red-500" : ""}
              />
              {errors.description && (
                <p className="text-sm text-red-500 flex items-center">
                  <AlertCircle className="h-4 w-4 mr-1" />
                  {errors.description}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="hypothesis">Hypothesis *</Label>
              <Textarea
                id="hypothesis"
                value={hypothesis}
                onChange={(e) => setHypothesis(e.target.value)}
                placeholder="e.g., Shorter headlines will increase click-through rates by 15%"
                className={errors.hypothesis ? "border-red-500" : ""}
              />
              {errors.hypothesis && (
                <p className="text-sm text-red-500 flex items-center">
                  <AlertCircle className="h-4 w-4 mr-1" />
                  {errors.hypothesis}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="test-type">Test Type *</Label>
              <Select value={testType} onValueChange={setTestType}>
                <SelectTrigger className={errors.test_type ? "border-red-500" : ""}>
                  <SelectValue placeholder="Select test type" />
                </SelectTrigger>
                <SelectContent>
                  {testTypes.map((type) => (
                    <SelectItem key={type.value} value={type.value}>
                      <div className="flex items-center space-x-2">
                        <type.icon className="h-4 w-4" />
                        <div>
                          <div className="font-medium">{type.label}</div>
                          <div className="text-sm text-muted-foreground">{type.description}</div>
                        </div>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.test_type && (
                <p className="text-sm text-red-500 flex items-center">
                  <AlertCircle className="h-4 w-4 mr-1" />
                  {errors.test_type}
                </p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="traffic-allocation">Traffic Allocation</Label>
                <div className="flex items-center space-x-2">
                  <Input
                    id="traffic-allocation"
                    type="number"
                    min="0"
                    max="1"
                    step="0.1"
                    value={trafficAllocation}
                    onChange={(e) => setTrafficAllocation(parseFloat(e.target.value) || 0)}
                    className="w-20"
                  />
                  <span className="text-sm text-muted-foreground">
                    ({Math.round(trafficAllocation * 100)}%)
                  </span>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="sample-size">Minimum Sample Size</Label>
                <Input
                  id="sample-size"
                  type="number"
                  min="10"
                  value={minimumSampleSize}
                  onChange={(e) => setMinimumSampleSize(parseInt(e.target.value) || 100)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="significance">Significance Level</Label>
                <div className="flex items-center space-x-2">
                  <Input
                    id="significance"
                    type="number"
                    min="0.01"
                    max="0.5"
                    step="0.01"
                    value={significanceLevel}
                    onChange={(e) => setSignificanceLevel(parseFloat(e.target.value) || 0.05)}
                    className="w-20"
                  />
                  <span className="text-sm text-muted-foreground">
                    ({Math.round(significanceLevel * 100)}%)
                  </span>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="duration">Planned Duration (Days)</Label>
              <Input
                id="duration"
                type="number"
                min="1"
                max="365"
                value={plannedDurationDays}
                onChange={(e) => setPlannedDurationDays(parseInt(e.target.value) || 7)}
              />
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="enabled"
                checked={enabled}
                onChange={(e) => setEnabled(e.target.checked)}
                className="rounded"
              />
              <Label htmlFor="enabled">Enable this test</Label>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 2: Test Variants */}
      {step === 2 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TestTube className="h-5 w-5 mr-2" />
              Test Variants
            </CardTitle>
            <CardDescription>
              Define the different variations you want to test
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {variants.map((variant, index) => (
              <div key={variant.id} className="p-4 border rounded-lg space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={cn("p-2 rounded-lg", getTestTypeColor(testType))}>
                      {getTestTypeIcon(testType)}
                    </div>
                    <div>
                      <h4 className="font-medium">Variant {index + 1}</h4>
                      <p className="text-sm text-muted-foreground">
                        {testTypes.find(t => t.value === testType)?.label || "Test Variant"}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="flex items-center space-x-2">
                      <Label className="text-sm">Traffic:</Label>
                      <Input
                        type="number"
                        min="0"
                        max="1"
                        step="0.1"
                        value={variant.traffic_percentage}
                        onChange={(e) => updateVariant(variant.id, "traffic_percentage", parseFloat(e.target.value) || 0)}
                        className="w-20"
                      />
                      <span className="text-sm text-muted-foreground">
                        ({Math.round(variant.traffic_percentage * 100)}%)
                      </span>
                    </div>
                    {variants.length > 2 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeVariant(variant.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Variant Name</Label>
                    <Input
                      value={variant.name}
                      onChange={(e) => updateVariant(variant.id, "name", e.target.value)}
                      placeholder="e.g., Control - Original"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Description</Label>
                    <Input
                      value={variant.description}
                      onChange={(e) => updateVariant(variant.id, "description", e.target.value)}
                      placeholder="Brief description of this variant"
                    />
                  </div>
                </div>

                {renderVariantConfiguration(variant, index)}
              </div>
            ))}

            <div className="flex items-center justify-between">
              <Button variant="outline" onClick={addVariant} disabled={variants.length >= 10}>
                <Plus className="h-4 w-4 mr-2" />
                Add Variant
              </Button>
              {variants.length > 1 && (
                <Button variant="outline" onClick={distributeTrafficEvenly}>
                  Distribute Traffic Evenly
                </Button>
              )}
            </div>

            {errors.variants && (
              <p className="text-sm text-red-500 flex items-center">
                <AlertCircle className="h-4 w-4 mr-1" />
                {errors.variants}
              </p>
            )}

            {errors.traffic_allocation && (
              <p className="text-sm text-red-500 flex items-center">
                <AlertCircle className="h-4 w-4 mr-1" />
                {errors.traffic_allocation}
              </p>
            )}

            {/* Traffic Allocation Summary */}
            {variants.length > 0 && (
              <div className="p-4 bg-muted rounded-lg">
                <h4 className="font-medium mb-2">Traffic Allocation Summary</h4>
                <div className="space-y-2">
                  {variants.map((variant, index) => (
                    <div key={variant.id} className="flex items-center justify-between">
                      <span className="text-sm">Variant {index + 1}: {variant.name || `Variant ${index + 1}`}</span>
                      <span className="text-sm font-medium">
                        {Math.round(variant.traffic_percentage * 100)}%
                      </span>
                    </div>
                  ))}
                  <div className="flex items-center justify-between font-medium pt-2 border-t">
                    <span>Total</span>
                    <span className={Math.abs(variants.reduce((sum, v) => sum + v.traffic_percentage, 0) - 1.0) > 0.01 ? "text-red-600" : "text-green-600"}>
                      {Math.round(variants.reduce((sum, v) => sum + v.traffic_percentage, 0) * 100)}%
                    </span>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {step > 1 && (
            <Button variant="outline" onClick={handlePrevious}>
              Previous
            </Button>
          )}
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={onCancel}>
            <X className="h-4 w-4 mr-2" />
            Cancel
          </Button>
          {step < 2 ? (
            <Button onClick={handleNext}>
              Next
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          ) : (
            <Button onClick={handleSave}>
              <Save className="h-4 w-4 mr-2" />
              Save A/B Test
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
