"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import {
  ResponsiveContainer,
  LineChart as RechartsLineChart,
  Line,
  AreaChart as RechartsAreaChart,
  Area,
  BarChart as RechartsBarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
  ComposedChart,
  Scatter,
  ScatterChart
} from "recharts";
import { 
  BarChart2, 
  TrendingUp, 
  Download, 
  RefreshCw, 
  MoreHorizontal,
  Calendar,
  Filter,
  Maximize2
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

// Chart data types
export interface ChartDataPoint {
  name: string;
  [key: string]: string | number;
}

export interface ChartConfig {
  dataKey: string;
  color: string;
  name: string;
  strokeWidth?: number;
  fill?: string;
  type?: 'line' | 'area' | 'bar' | 'scatter';
}

export interface ChartProps {
  data: ChartDataPoint[];
  config: ChartConfig[];
  title: string;
  description?: string;
  loading?: boolean;
  error?: boolean;
  onRetry?: () => void;
  onExport?: () => void;
  onRefresh?: () => void;
  className?: string;
  height?: number;
  showLegend?: boolean;
  showGrid?: boolean;
  showTooltip?: boolean;
  showReferenceLine?: boolean;
  referenceValue?: number;
  referenceLabel?: string;
  xAxisKey?: string;
  yAxisDomain?: [number, number] | 'auto';
  aspect?: number;
}

// Base chart wrapper component
function ChartWrapper({ 
  children, 
  title, 
  description, 
  loading, 
  error, 
  onRetry, 
  onExport, 
  onRefresh,
  className,
  height = 300,
  showActions = true
}: {
  children: React.ReactNode;
  title: string;
  description?: string;
  loading?: boolean;
  error?: boolean;
  onRetry?: () => void;
  onExport?: () => void;
  onRefresh?: () => void;
  className?: string;
  height?: number;
  showActions?: boolean;
}) {
  if (loading) {
    return (
      <Card className={cn("card-premium", className)} data-testid="chart-loading">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <div className="space-y-1">
            <Skeleton className="h-6 w-48" />
            {description && <Skeleton className="h-4 w-64" />}
          </div>
          {showActions && <Skeleton className="h-8 w-8" />}
        </CardHeader>
        <CardContent>
          <Skeleton className="w-full" style={{ height: `${height}px` }} />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={cn("card-premium", className)} data-testid="chart-error">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <div>
            <CardTitle className="text-lg font-semibold">{title}</CardTitle>
            {description && <p className="text-sm text-muted-foreground">{description}</p>}
          </div>
          {onRetry && (
            <Button variant="outline" size="sm" onClick={onRetry} data-testid="chart-retry-button">
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          )}
        </CardHeader>
        <CardContent className="flex items-center justify-center" style={{ height: `${height}px` }}>
          <div className="text-center text-error-600">
            <BarChart2 className="h-12 w-12 mx-auto mb-2" />
            <p className="text-sm">Failed to load chart data</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn("card-premium", className)} data-testid="chart-card">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div>
          <CardTitle className="text-lg font-semibold">{title}</CardTitle>
          {description && <p className="text-sm text-muted-foreground">{description}</p>}
        </div>
        {showActions && (
          <div className="flex items-center gap-2">
            {onRefresh && (
              <Button variant="ghost" size="sm" onClick={onRefresh} data-testid="chart-refresh-button">
                <RefreshCw className="h-4 w-4" />
              </Button>
            )}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" data-testid="chart-menu-button">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {onExport && (
                  <DropdownMenuItem onClick={onExport} data-testid="chart-export-button">
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </DropdownMenuItem>
                )}
                <DropdownMenuItem data-testid="chart-fullscreen-button">
                  <Maximize2 className="h-4 w-4 mr-2" />
                  Fullscreen
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div style={{ height: `${height}px` }}>
          {children}
        </div>
      </CardContent>
    </Card>
  );
}

// Line Chart Component
export function LineChart({
  data,
  config,
  title,
  description,
  loading,
  error,
  onRetry,
  onExport,
  onRefresh,
  className,
  height = 300,
  showLegend = true,
  showGrid = true,
  showTooltip = true,
  showReferenceLine = false,
  referenceValue,
  referenceLabel,
  xAxisKey = "name",
  yAxisDomain = 'auto',
  aspect
}: ChartProps) {
  return (
    <ChartWrapper
      title={title}
      description={description}
      loading={loading}
      error={error}
      onRetry={onRetry}
      onExport={onExport}
      onRefresh={onRefresh}
      className={className}
      height={height}
    >
      <ResponsiveContainer width="100%" height="100%">
        <RechartsLineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--neutral-200))" />}
          <XAxis 
            dataKey={xAxisKey} 
            stroke="hsl(var(--neutral-400))" 
            fontSize={12} 
            tickLine={false} 
            axisLine={false}
          />
          <YAxis 
            stroke="hsl(var(--neutral-400))" 
            fontSize={12} 
            tickLine={false} 
            axisLine={false}
            domain={yAxisDomain}
          />
          {showTooltip && (
            <Tooltip
              contentStyle={{ 
                borderRadius: '0.75rem', 
                border: '1px solid hsl(var(--neutral-200))', 
                background: 'white',
                fontSize: '0.875rem',
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
              }}
              labelStyle={{ fontWeight: 'bold', marginBottom: '0.5rem' }}
              itemStyle={{ padding: '0.25rem 0' }}
            />
          )}
          {showLegend && <Legend />}
          {showReferenceLine && referenceValue && (
            <ReferenceLine 
              y={referenceValue} 
              stroke="hsl(var(--neutral-400))" 
              strokeDasharray="5 5"
              label={referenceLabel}
            />
          )}
          {config.map((item, index) => (
            <Line
              key={index}
              type="monotone"
              dataKey={item.dataKey}
              stroke={item.color}
              strokeWidth={item.strokeWidth || 2}
              dot={{ fill: item.color, strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: item.color, strokeWidth: 2 }}
              name={item.name}
            />
          ))}
        </RechartsLineChart>
      </ResponsiveContainer>
    </ChartWrapper>
  );
}

// Area Chart Component
export function AreaChart({
  data,
  config,
  title,
  description,
  loading,
  error,
  onRetry,
  onExport,
  onRefresh,
  className,
  height = 300,
  showLegend = true,
  showGrid = true,
  showTooltip = true,
  showReferenceLine = false,
  referenceValue,
  referenceLabel,
  xAxisKey = "name",
  yAxisDomain = 'auto'
}: ChartProps) {
  return (
    <ChartWrapper
      title={title}
      description={description}
      loading={loading}
      error={error}
      onRetry={onRetry}
      onExport={onExport}
      onRefresh={onRefresh}
      className={className}
      height={height}
    >
      <ResponsiveContainer width="100%" height="100%">
        <RechartsAreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <defs>
            {config.map((item, index) => (
              <linearGradient key={index} id={`color${index}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={item.color} stopOpacity={0.8}/>
                <stop offset="95%" stopColor={item.color} stopOpacity={0}/>
              </linearGradient>
            ))}
          </defs>
          {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--neutral-200))" />}
          <XAxis 
            dataKey={xAxisKey} 
            stroke="hsl(var(--neutral-400))" 
            fontSize={12} 
            tickLine={false} 
            axisLine={false}
          />
          <YAxis 
            stroke="hsl(var(--neutral-400))" 
            fontSize={12} 
            tickLine={false} 
            axisLine={false}
            domain={yAxisDomain}
          />
          {showTooltip && (
            <Tooltip
              contentStyle={{ 
                borderRadius: '0.75rem', 
                border: '1px solid hsl(var(--neutral-200))', 
                background: 'white',
                fontSize: '0.875rem',
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
              }}
              labelStyle={{ fontWeight: 'bold', marginBottom: '0.5rem' }}
              itemStyle={{ padding: '0.25rem 0' }}
            />
          )}
          {showLegend && <Legend />}
          {showReferenceLine && referenceValue && (
            <ReferenceLine 
              y={referenceValue} 
              stroke="hsl(var(--neutral-400))" 
              strokeDasharray="5 5"
              label={referenceLabel}
            />
          )}
          {config.map((item, index) => (
            <Area
              key={index}
              type="monotone"
              dataKey={item.dataKey}
              stroke={item.color}
              fill={`url(#color${index})`}
              strokeWidth={item.strokeWidth || 2}
              name={item.name}
            />
          ))}
        </RechartsAreaChart>
      </ResponsiveContainer>
    </ChartWrapper>
  );
}

// Bar Chart Component
export function BarChart({
  data,
  config,
  title,
  description,
  loading,
  error,
  onRetry,
  onExport,
  onRefresh,
  className,
  height = 300,
  showLegend = true,
  showGrid = true,
  showTooltip = true,
  showReferenceLine = false,
  referenceValue,
  referenceLabel,
  xAxisKey = "name",
  yAxisDomain = 'auto'
}: ChartProps) {
  return (
    <ChartWrapper
      title={title}
      description={description}
      loading={loading}
      error={error}
      onRetry={onRetry}
      onExport={onExport}
      onRefresh={onRefresh}
      className={className}
      height={height}
    >
      <ResponsiveContainer width="100%" height="100%">
        <RechartsBarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--neutral-200))" />}
          <XAxis 
            dataKey={xAxisKey} 
            stroke="hsl(var(--neutral-400))" 
            fontSize={12} 
            tickLine={false} 
            axisLine={false}
          />
          <YAxis 
            stroke="hsl(var(--neutral-400))" 
            fontSize={12} 
            tickLine={false} 
            axisLine={false}
            domain={yAxisDomain}
          />
          {showTooltip && (
            <Tooltip
              contentStyle={{ 
                borderRadius: '0.75rem', 
                border: '1px solid hsl(var(--neutral-200))', 
                background: 'white',
                fontSize: '0.875rem',
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
              }}
              labelStyle={{ fontWeight: 'bold', marginBottom: '0.5rem' }}
              itemStyle={{ padding: '0.25rem 0' }}
            />
          )}
          {showLegend && <Legend />}
          {showReferenceLine && referenceValue && (
            <ReferenceLine 
              y={referenceValue} 
              stroke="hsl(var(--neutral-400))" 
              strokeDasharray="5 5"
              label={referenceLabel}
            />
          )}
          {config.map((item, index) => (
            <Bar
              key={index}
              dataKey={item.dataKey}
              fill={item.color}
              radius={[4, 4, 0, 0]}
              name={item.name}
            />
          ))}
        </RechartsBarChart>
      </ResponsiveContainer>
    </ChartWrapper>
  );
}

// Pie Chart Component
export function PieChart({
  data,
  config,
  title,
  description,
  loading,
  error,
  onRetry,
  onExport,
  onRefresh,
  className,
  height = 300,
  showLegend = true,
  showTooltip = true
}: ChartProps) {
  const COLORS = ['hsl(var(--brand-500))', 'hsl(var(--success-500))', 'hsl(var(--warning-500))', 'hsl(var(--error-500))', 'hsl(var(--neutral-500))'];

  return (
    <ChartWrapper
      title={title}
      description={description}
      loading={loading}
      error={error}
      onRetry={onRetry}
      onExport={onExport}
      onRefresh={onRefresh}
      className={className}
      height={height}
    >
      <ResponsiveContainer width="100%" height="100%">
        <RechartsPieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey={config[0]?.dataKey || 'value'}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          {showTooltip && (
            <Tooltip
              contentStyle={{ 
                borderRadius: '0.75rem', 
                border: '1px solid hsl(var(--neutral-200))', 
                background: 'white',
                fontSize: '0.875rem',
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
              }}
            />
          )}
          {showLegend && <Legend />}
        </RechartsPieChart>
      </ResponsiveContainer>
    </ChartWrapper>
  );
}

// Composed Chart Component (Line + Bar)
export function ComposedChart({
  data,
  config,
  title,
  description,
  loading,
  error,
  onRetry,
  onExport,
  onRefresh,
  className,
  height = 300,
  showLegend = true,
  showGrid = true,
  showTooltip = true,
  xAxisKey = "name",
  yAxisDomain = 'auto'
}: ChartProps) {
  return (
    <ChartWrapper
      title={title}
      description={description}
      loading={loading}
      error={error}
      onRetry={onRetry}
      onExport={onExport}
      onRefresh={onRefresh}
      className={className}
      height={height}
    >
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--neutral-200))" />}
          <XAxis 
            dataKey={xAxisKey} 
            stroke="hsl(var(--neutral-400))" 
            fontSize={12} 
            tickLine={false} 
            axisLine={false}
          />
          <YAxis 
            stroke="hsl(var(--neutral-400))" 
            fontSize={12} 
            tickLine={false} 
            axisLine={false}
            domain={yAxisDomain}
          />
          {showTooltip && (
            <Tooltip
              contentStyle={{ 
                borderRadius: '0.75rem', 
                border: '1px solid hsl(var(--neutral-200))', 
                background: 'white',
                fontSize: '0.875rem',
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
              }}
              labelStyle={{ fontWeight: 'bold', marginBottom: '0.5rem' }}
              itemStyle={{ padding: '0.25rem 0' }}
            />
          )}
          {showLegend && <Legend />}
          {config.map((item, index) => {
            if (item.type === 'bar') {
              return (
                <Bar
                  key={index}
                  dataKey={item.dataKey}
                  fill={item.color}
                  radius={[4, 4, 0, 0]}
                  name={item.name}
                />
              );
            } else if (item.type === 'area') {
              return (
                <Area
                  key={index}
                  type="monotone"
                  dataKey={item.dataKey}
                  stroke={item.color}
                  fill={item.color}
                  fillOpacity={0.3}
                  name={item.name}
                />
              );
            } else {
              return (
                <Line
                  key={index}
                  type="monotone"
                  dataKey={item.dataKey}
                  stroke={item.color}
                  strokeWidth={item.strokeWidth || 2}
                  name={item.name}
                />
              );
            }
          })}
        </ComposedChart>
      </ResponsiveContainer>
    </ChartWrapper>
  );
}

// Chart configuration helpers
export const CHART_COLORS = {
  primary: 'hsl(var(--brand-500))',
  success: 'hsl(var(--success-500))',
  warning: 'hsl(var(--warning-500))',
  error: 'hsl(var(--error-500))',
  neutral: 'hsl(var(--neutral-500))',
  brand: {
    50: 'hsl(var(--brand-50))',
    100: 'hsl(var(--brand-100))',
    200: 'hsl(var(--brand-200))',
    300: 'hsl(var(--brand-300))',
    400: 'hsl(var(--brand-400))',
    500: 'hsl(var(--brand-500))',
    600: 'hsl(var(--brand-600))',
    700: 'hsl(var(--brand-700))',
    800: 'hsl(var(--brand-800))',
    900: 'hsl(var(--brand-900))',
  }
} as const;
