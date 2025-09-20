"use client";

import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  CheckCircle,
  XCircle,
  AlertCircle,
  Info,
  X,
  RefreshCw,
  ExternalLink,
  Copy,
  Download,
  Upload,
  Save,
  Trash2,
  Edit,
  Eye,
  EyeOff,
  Lock,
  Unlock,
  Shield,
  AlertTriangle,
  Bell,
  MessageSquare,
  Mail,
  Phone,
  Calendar,
  Clock,
  User,
  Users,
  Settings,
  Home,
  Search,
  Filter,
  Plus,
  Minus,
  ArrowRight,
  ArrowLeft,
  ChevronUp,
  ChevronDown,
  ChevronRight,
  ChevronLeft,
  Check,
  X as XIcon,
  MoreHorizontal,
  MoreVertical,
  Menu,
  Grid3X3,
  List,
  Maximize2,
  Minimize2,
  RotateCcw,
  RotateCw,
  ZoomIn,
  ZoomOut,
  Move,
  Copy as CopyIcon,
  Scissors,
  Clipboard,
  Bookmark,
  Flag,
  Tag,
  Hash,
  AtSign,
  DollarSign,
  Percent,
  TrendingUp,
  TrendingDown,
  Activity,
  Target,
  Award,
  Gift,
  Package,
  Truck,
  Building,
  MapPin,
  Send,
  Loader2,
  HelpCircle,
  QuestionMarkCircle,
  Lightbulb,
  Rocket,
  Sparkles,
  Wand2,
  Crown,
  Key,
  Eye as EyeIcon,
  Volume2,
  VolumeX,
  Play,
  Pause,
  Stop,
  SkipBack,
  SkipForward,
  Repeat,
  Shuffle,
  Volume1,
  Mic,
  MicOff,
  Camera,
  CameraOff,
  Video,
  VideoOff,
  Headphones,
  Speaker,
  Monitor,
  Smartphone,
  Tablet,
  Laptop,
  Desktop,
  Server,
  HardDrive,
  Cpu,
  MemoryStick,
  Wifi,
  WifiOff,
  Bluetooth,
  BluetoothOff,
  Battery,
  BatteryLow,
  Plug,
  Power,
  PowerOff,
  Sun,
  Moon,
  Cloud,
  CloudOff,
  CloudRain,
  CloudSnow,
  CloudLightning,
  Wind,
  Droplets,
  Thermometer,
  Gauge,
  Timer,
  Stopwatch,
  Clock3,
  Clock4,
  Clock5,
  Clock6,
  Clock7,
  Clock8,
  Clock9,
  Clock10,
  Clock11,
  Clock12,
  Calendar as CalendarIcon,
  CalendarDays,
  CalendarCheck,
  CalendarX,
  CalendarPlus,
  CalendarMinus,
  CalendarRange,
  CalendarSearch,
  CalendarClock,
  CalendarHeart,
  CalendarStar,
  CalendarUser,
  CalendarEdit,
  CalendarTrash2,
  CalendarSettings,
  CalendarDownload,
  CalendarUpload,
  CalendarShare,
  CalendarCopy,
  CalendarMove,
  CalendarRotateCcw,
  CalendarRotateCw,
  CalendarZoomIn,
  CalendarZoomOut,
  CalendarMaximize2,
  CalendarMinimize2,
  CalendarGrid3X3,
  CalendarList,
  CalendarMoreHorizontal,
  CalendarMoreVertical,
  CalendarMenu,
  CalendarXCircle,
  CalendarCheckCircle,
  CalendarAlertCircle,
  CalendarInfo,
  CalendarHelpCircle,
  CalendarQuestionMarkCircle,
  CalendarLightbulb,
  CalendarRocket,
  CalendarSparkles,
  CalendarWand2,
  CalendarMagic,
  CalendarCrown,
  CalendarKey,
  CalendarLock,
  CalendarUnlock,
  CalendarEye,
  CalendarEyeOff,
  CalendarVolume2,
  CalendarVolumeX,
  CalendarPlay,
  CalendarPause,
  CalendarStop,
  CalendarSkipBack,
  CalendarSkipForward,
  CalendarRepeat,
  CalendarShuffle,
  CalendarVolume1,
  CalendarMic,
  CalendarMicOff,
  CalendarCamera,
  CalendarCameraOff,
  CalendarVideo,
  CalendarVideoOff,
  CalendarHeadphones,
  CalendarSpeaker,
  CalendarMonitor,
  CalendarSmartphone,
  CalendarTablet,
  CalendarLaptop,
  CalendarDesktop,
  CalendarServer,
  CalendarHardDrive,
  CalendarCpu,
  CalendarMemoryStick,
  CalendarWifi,
  CalendarWifiOff,
  CalendarBluetooth,
  CalendarBluetoothOff,
  CalendarBattery,
  CalendarBatteryLow,
  CalendarPlug,
  CalendarPower,
  CalendarPowerOff,
  CalendarSun,
  CalendarMoon,
  CalendarCloud,
  CalendarCloudOff,
  CalendarCloudRain,
  CalendarCloudSnow,
  CalendarCloudLightning,
  CalendarWind,
  CalendarDroplets,
  CalendarThermometer,
  CalendarGauge,
  CalendarTimer,
  CalendarStopwatch
} from "lucide-react";

export interface ToastProps {
  id: string;
  title?: string;
  description?: string;
  type?: "success" | "error" | "warning" | "info" | "loading";
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
    variant?: "default" | "outline" | "secondary" | "ghost" | "link" | "destructive";
  };
  onClose?: () => void;
  className?: string;
  icon?: React.ComponentType<{ className?: string }>;
  persistent?: boolean;
  position?: "top-left" | "top-center" | "top-right" | "bottom-left" | "bottom-center" | "bottom-right";
}

const TOAST_ICONS = {
  success: CheckCircle,
  error: XCircle,
  warning: AlertTriangle,
  info: Info,
  loading: Loader2
} as const;

const TOAST_COLORS = {
  success: "text-success-600 bg-success-50 border-success-200",
  error: "text-error-600 bg-error-50 border-error-200",
  warning: "text-warning-600 bg-warning-50 border-warning-200",
  info: "text-brand-600 bg-brand-50 border-brand-200",
  loading: "text-brand-600 bg-brand-50 border-brand-200"
} as const;

const TOAST_ICON_COLORS = {
  success: "text-success-600",
  error: "text-error-600",
  warning: "text-warning-600",
  info: "text-brand-600",
  loading: "text-brand-600"
} as const;

export function Toast({
  id,
  title,
  description,
  type = "info",
  duration = 5000,
  action,
  onClose,
  className,
  icon,
  persistent = false,
  position = "top-right"
}: ToastProps) {
  const [isVisible, setIsVisible] = useState(true);
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    if (persistent || type === "loading") return;

    const timer = setTimeout(() => {
      handleClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, persistent, type]);

  const handleClose = () => {
    setIsExiting(true);
    setTimeout(() => {
      setIsVisible(false);
      onClose?.();
    }, 300);
  };

  const handleAction = () => {
    action?.onClick();
    if (type !== "loading") {
      handleClose();
    }
  };

  if (!isVisible) return null;

  const Icon = icon || TOAST_ICONS[type];
  const isAnimated = type === "loading";

  return (
    <div
      className={cn(
        "fixed z-50 max-w-sm w-full",
        position === "top-left" && "top-4 left-4",
        position === "top-center" && "top-4 left-1/2 transform -translate-x-1/2",
        position === "top-right" && "top-4 right-4",
        position === "bottom-left" && "bottom-4 left-4",
        position === "bottom-center" && "bottom-4 left-1/2 transform -translate-x-1/2",
        position === "bottom-right" && "bottom-4 right-4"
      )}
      data-testid={`toast-${id}`}
    >
      <div
        className={cn(
          "flex items-start gap-3 p-4 rounded-xl border shadow-lg transition-all duration-300",
          TOAST_COLORS[type],
          isExiting ? "opacity-0 translate-x-full" : "opacity-100 translate-x-0",
          className
        )}
      >
        {/* Icon */}
        <div className="flex-shrink-0">
          <Icon
            className={cn(
              "h-5 w-5",
              TOAST_ICON_COLORS[type],
              isAnimated && "animate-spin"
            )}
          />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {title && (
            <div className="font-semibold text-sm mb-1" data-testid="toast-title">
              {title}
            </div>
          )}
          {description && (
            <div className="text-sm opacity-90" data-testid="toast-description">
              {description}
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          {action && (
            <Button
              variant={action.variant || "ghost"}
              size="sm"
              onClick={handleAction}
              className="h-8 px-3 text-xs"
              data-testid="toast-action-button"
            >
              {action.label}
            </Button>
          )}
          
          {!persistent && type !== "loading" && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClose}
              className="h-8 w-8 p-0 hover:bg-black/10"
              data-testid="toast-close-button"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

// Toast Container Component
export function ToastContainer({
  toasts,
  onRemove,
  position = "top-right",
  className
}: {
  toasts: ToastProps[];
  onRemove: (id: string) => void;
  position?: ToastProps['position'];
  className?: string;
}) {
  return (
    <div
      className={cn(
        "fixed z-50 pointer-events-none",
        position === "top-left" && "top-4 left-4",
        position === "top-center" && "top-4 left-1/2 transform -translate-x-1/2",
        position === "top-right" && "top-4 right-4",
        position === "bottom-left" && "bottom-4 left-4",
        position === "bottom-center" && "bottom-4 left-1/2 transform -translate-x-1/2",
        position === "bottom-right" && "bottom-4 right-4",
        className
      )}
      data-testid="toast-container"
    >
      <div className="space-y-2 pointer-events-auto">
        {toasts.map((toast) => (
          <Toast
            key={toast.id}
            {...toast}
            onClose={() => onRemove(toast.id)}
            position={position}
          />
        ))}
      </div>
    </div>
  );
}

// Toast Hook
export function useToast() {
  const [toasts, setToasts] = useState<ToastProps[]>([]);

  const addToast = (toast: Omit<ToastProps, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newToast = { ...toast, id };
    setToasts(prev => [...prev, newToast]);
    return id;
  };

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  const updateToast = (id: string, updates: Partial<ToastProps>) => {
    setToasts(prev =>
      prev.map(toast =>
        toast.id === id ? { ...toast, ...updates } : toast
      )
    );
  };

  const clearToasts = () => {
    setToasts([]);
  };

  // Convenience methods
  const success = (title: string, description?: string, options?: Partial<ToastProps>) => {
    return addToast({
      type: "success",
      title,
      description,
      ...options
    });
  };

  const error = (title: string, description?: string, options?: Partial<ToastProps>) => {
    return addToast({
      type: "error",
      title,
      description,
      ...options
    });
  };

  const warning = (title: string, description?: string, options?: Partial<ToastProps>) => {
    return addToast({
      type: "warning",
      title,
      description,
      ...options
    });
  };

  const info = (title: string, description?: string, options?: Partial<ToastProps>) => {
    return addToast({
      type: "info",
      title,
      description,
      ...options
    });
  };

  const loading = (title: string, description?: string, options?: Partial<ToastProps>) => {
    return addToast({
      type: "loading",
      title,
      description,
      persistent: true,
      ...options
    });
  };

  return {
    toasts,
    addToast,
    removeToast,
    updateToast,
    clearToasts,
    success,
    error,
    warning,
    info,
    loading
  };
}

// Predefined toast configurations
export const TOAST_PRESETS = {
  // Success messages
  saved: {
    type: "success" as const,
    title: "Saved successfully",
    description: "Your changes have been saved.",
    icon: Save
  },
  published: {
    type: "success" as const,
    title: "Published successfully",
    description: "Your content has been published.",
    icon: Send
  },
  connected: {
    type: "success" as const,
    title: "Connected successfully",
    description: "Integration has been connected.",
    icon: CheckCircle
  },
  uploaded: {
    type: "success" as const,
    title: "Uploaded successfully",
    description: "Your file has been uploaded.",
    icon: Upload
  },
  downloaded: {
    type: "success" as const,
    title: "Downloaded successfully",
    description: "Your file has been downloaded.",
    icon: Download
  },
  copied: {
    type: "success" as const,
    title: "Copied to clipboard",
    description: "Content has been copied.",
    icon: Copy
  },

  // Error messages
  saveError: {
    type: "error" as const,
    title: "Save failed",
    description: "There was an error saving your changes.",
    icon: XCircle
  },
  publishError: {
    type: "error" as const,
    title: "Publish failed",
    description: "There was an error publishing your content.",
    icon: XCircle
  },
  connectionError: {
    type: "error" as const,
    title: "Connection failed",
    description: "There was an error connecting to the service.",
    icon: XCircle
  },
  uploadError: {
    type: "error" as const,
    title: "Upload failed",
    description: "There was an error uploading your file.",
    icon: XCircle
  },
  networkError: {
    type: "error" as const,
    title: "Network error",
    description: "Please check your internet connection.",
    icon: WifiOff
  },

  // Warning messages
  unsavedChanges: {
    type: "warning" as const,
    title: "Unsaved changes",
    description: "You have unsaved changes that will be lost.",
    icon: AlertTriangle
  },
  connectionExpired: {
    type: "warning" as const,
    title: "Connection expired",
    description: "Please reconnect to continue using this feature.",
    icon: AlertTriangle
  },
  quotaExceeded: {
    type: "warning" as const,
    title: "Quota exceeded",
    description: "You have reached your usage limit for this month.",
    icon: AlertTriangle
  },

  // Info messages
  newFeature: {
    type: "info" as const,
    title: "New feature available",
    description: "Check out the latest updates to the platform.",
    icon: Sparkles
  },
  maintenance: {
    type: "info" as const,
    title: "Scheduled maintenance",
    description: "The system will be under maintenance from 2-4 AM.",
    icon: Settings
  },
  updateAvailable: {
    type: "info" as const,
    title: "Update available",
    description: "A new version of the app is available.",
    icon: RefreshCw
  },

  // Loading messages
  saving: {
    type: "loading" as const,
    title: "Saving...",
    description: "Please wait while we save your changes.",
    icon: Loader2
  },
  publishing: {
    type: "loading" as const,
    title: "Publishing...",
    description: "Please wait while we publish your content.",
    icon: Loader2
  },
  connecting: {
    type: "loading" as const,
    title: "Connecting...",
    description: "Please wait while we connect to the service.",
    icon: Loader2
  },
  uploading: {
    type: "loading" as const,
    title: "Uploading...",
    description: "Please wait while we upload your file.",
    icon: Loader2
  }
} as const;

// Helper function to create toast with preset
export function createToastWithPreset(
  preset: keyof typeof TOAST_PRESETS,
  customTitle?: string,
  customDescription?: string,
  options?: Partial<ToastProps>
): ToastProps {
  const presetConfig = TOAST_PRESETS[preset];
  return {
    ...presetConfig,
    title: customTitle || presetConfig.title,
    description: customDescription || presetConfig.description,
    ...options
  };
}
