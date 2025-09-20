"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  FileText,
  Image,
  Video,
  Calendar,
  BarChart2,
  Users,
  Search,
  Filter,
  Plus,
  RefreshCw,
  AlertCircle,
  Clock,
  Globe,
  Database,
  Zap,
  Shield,
  MessageSquare,
  Bell,
  CreditCard,
  Puzzle,
  Library,
  Eye,
  Archive,
  Heart,
  ExternalLink,
  ArrowRight,
  ArrowLeft,
  ChevronRight,
  ChevronLeft,
  ChevronUp,
  ChevronDown,
  X,
  Check,
  Minus,
  MoreHorizontal,
  Grid3X3,
  List,
  Maximize2,
  Minimize2,
  RotateCcw,
  RotateCw,
  ZoomIn,
  ZoomOut,
  Move,
  Copy,
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
  Home,
  Building,
  MapPin,
  Phone,
  Mail,
  Send,
  Save,
  Loader2,
  AlertTriangle,
  Info,
  HelpCircle,
  Lightbulb,
  Rocket,
  Sparkles,
  Wand2,
  Crown,
  Key,
  Lock,
  Unlock,
  EyeOff,
  Volume2,
  VolumeX,
  Play,
  Pause,
  Square,
  SkipBack,
  SkipForward,
  Repeat,
  Shuffle,
  Volume1,
  Mic,
  MicOff,
  Camera,
  CameraOff,
  VideoOff,
  Headphones,
  Speaker,
  Monitor,
  Smartphone,
  Tablet,
  Laptop,
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
  Star,
  User,
  Edit,
  Trash2,
  Settings,
  Download,
  Upload,
  Share2,
  MoreVertical,
  Menu,
  XCircle,
  CheckCircle,
  HelpCircle,
  Lightbulb,
  Rocket,
  Sparkles,
  Wand2,
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
  CalendarSquare,
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
  CalendarMonitor,
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
  CalendarTimer
} from "lucide-react";

interface EmptyStateProps {
  icon?: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
    variant?: "default" | "outline" | "secondary" | "ghost" | "link" | "destructive";
  };
  secondaryAction?: {
    label: string;
    onClick: () => void;
    variant?: "default" | "outline" | "secondary" | "ghost" | "link" | "destructive";
  };
  image?: string;
  className?: string;
  size?: "sm" | "md" | "lg";
  variant?: "default" | "error" | "success" | "warning" | "info";
}

const ICON_MAP = {
  // Content
  content: FileText,
  post: FileText,
  article: FileText,
  blog: FileText,
  text: FileText,
  document: FileText,
  file: FileText,
  
  // Media
  image: Image,
  photo: Image,
  picture: Image,
  media: Image,
  video: Video,
  clip: Video,
  movie: Video,
  
  // Calendar
  calendar: Calendar,
  schedule: Calendar,
  event: Calendar,
  appointment: Calendar,
  
  // Analytics
  analytics: BarChart2,
  stats: BarChart2,
  metrics: BarChart2,
  performance: BarChart2,
  data: BarChart2,
  
  // Users
  users: Users,
  team: Users,
  members: Users,
  people: Users,
  
  // Settings
  settings: Settings,
  config: Settings,
  preferences: Settings,
  
  // Search
  search: Search,
  find: Search,
  lookup: Search,
  
  // Filter
  filter: Filter,
  filters: Filter,
  
  // Add
  add: Plus,
  create: Plus,
  new: Plus,
  plus: Plus,
  
  // Refresh
  refresh: RefreshCw,
  reload: RefreshCw,
  sync: RefreshCw,
  
  // Error
  error: AlertCircle,
  warning: AlertCircle,
  alert: AlertCircle,
  
  // Success
  success: CheckCircle,
  complete: CheckCircle,
  done: CheckCircle,
  
  // Time
  time: Clock,
  clock: Clock,
  timer: Clock,
  
  // Globe
  globe: Globe,
  world: Globe,
  international: Globe,
  
  // Database
  database: Database,
  storage: Database,
  data: Database,
  
  // Automation
  automation: Zap,
  zap: Zap,
  lightning: Zap,
  
  // Security
  security: Shield,
  shield: Shield,
  protect: Shield,
  
  // Messages
  messages: MessageSquare,
  chat: MessageSquare,
  conversation: MessageSquare,
  
  // Notifications
  notifications: Bell,
  bell: Bell,
  alerts: Bell,
  
  // Billing
  billing: CreditCard,
  payment: CreditCard,
  subscription: CreditCard,
  
  // Integrations
  integrations: Puzzle,
  puzzle: Puzzle,
  connect: Puzzle,
  
  // Library
  library: Library,
  collection: Library,
  archive: Library,
  
  // Edit
  edit: Edit,
  modify: Edit,
  update: Edit,
  
  // View
  view: Eye,
  see: Eye,
  preview: Eye,
  
  // Download
  download: Download,
  export: Download,
  save: Download,
  
  // Upload
  upload: Upload,
  import: Upload,
  add: Upload,
  
  // Delete
  delete: Trash2,
  remove: Trash2,
  trash: Trash2,
  
  // Archive
  archive: Archive,
  store: Archive,
  keep: Archive,
  
  // Star
  star: Star,
  favorite: Star,
  bookmark: Star,
  
  // Heart
  heart: Heart,
  like: Heart,
  love: Heart,
  
  // Share
  share: Share2,
  social: Share2,
  distribute: Share2,
  
  // External
  external: ExternalLink,
  link: ExternalLink,
  open: ExternalLink,
  
  // Arrows
  right: ArrowRight,
  left: ArrowLeft,
  up: ChevronUp,
  down: ChevronDown,
  next: ChevronRight,
  previous: ChevronLeft,
  
  // Actions
  close: X,
  cancel: X,
  clear: X,
  check: Check,
  confirm: Check,
  minus: Minus,
  remove: Minus,
  
  // More
  more: MoreHorizontal,
  menu: Menu,
  options: MoreHorizontal,
  
  // Views
  grid: Grid3X3,
  list: List,
  table: List,
  
  // Display
  maximize: Maximize2,
  minimize: Minimize2,
  fullscreen: Maximize2,
  
  // Rotate
  rotate: RotateCcw,
  turn: RotateCcw,
  flip: RotateCcw,
  
  // Zoom
  zoom: ZoomIn,
  magnify: ZoomIn,
  enlarge: ZoomIn,
  
  // Move
  move: Move,
  drag: Move,
  position: Move,
  
  // Copy
  copy: Copy,
  duplicate: Copy,
  clone: Copy,
  
  // Cut
  cut: Scissors,
  scissors: Scissors,
  trim: Scissors,
  
  // Paste
  paste: Clipboard,
  insert: Clipboard,
  apply: Clipboard,
  
  // Bookmark
  bookmark: Bookmark,
  save: Bookmark,
  mark: Bookmark,
  
  // Flag
  flag: Flag,
  mark: Flag,
  signal: Flag,
  
  // Tag
  tag: Tag,
  label: Tag,
  category: Tag,
  
  // Hash
  hash: Hash,
  number: Hash,
  count: Hash,
  
  // At
  at: AtSign,
  mention: AtSign,
  user: AtSign,
  
  // Money
  money: DollarSign,
  price: DollarSign,
  cost: DollarSign,
  currency: DollarSign,
  
  // Percent
  percent: Percent,
  percentage: Percent,
  rate: Percent,
  
  // Trending
  trending: TrendingUp,
  growth: TrendingUp,
  increase: TrendingUp,
  rise: TrendingUp,
  
  // Activity
  activity: Activity,
  motion: Activity,
  movement: Activity,
  
  // Target
  target: Target,
  goal: Target,
  aim: Target,
  
  // Award
  award: Award,
  prize: Award,
  achievement: Award,
  
  // Gift
  gift: Gift,
  present: Gift,
  surprise: Gift,
  
  // Package
  package: Package,
  box: Package,
  container: Package,
  
  // Truck
  truck: Truck,
  delivery: Truck,
  transport: Truck,
  
  // Home
  home: Home,
  house: Home,
  residence: Home,
  
  // Building
  building: Building,
  office: Building,
  workplace: Building,
  
  // Map
  map: MapPin,
  location: MapPin,
  place: MapPin,
  
  // Phone
  phone: Phone,
  call: Phone,
  telephone: Phone,
  
  // Mail
  mail: Mail,
  email: Mail,
  message: Mail,
  
  // Send
  send: Send,
  submit: Send,
  deliver: Send,
  
  // Save
  save: Save,
  store: Save,
  keep: Save,
  
  // Loader
  loading: Loader2,
  spinner: Loader2,
  wait: Loader2,
  
  // Alert
  alert: AlertTriangle,
  warning: AlertTriangle,
  caution: AlertTriangle,
  
  // Info
  info: Info,
  information: Info,
  details: Info,
  
  // Help
  help: HelpCircle,
  question: HelpCircle,
  support: HelpCircle,
  
  // Lightbulb
  idea: Lightbulb,
  suggestion: Lightbulb,
  tip: Lightbulb,
  
  // Rocket
  rocket: Rocket,
  launch: Rocket,
  blast: Rocket,
  
  // Sparkles
  sparkles: Sparkles,
  magic: Sparkles,
  wonder: Sparkles,
  
  // Wand
  wand: Wand2,
  magic: Wand2,
  spell: Wand2,
  
  // Crown
  crown: Crown,
  king: Crown,
  royalty: Crown,
  
  // Key
  key: Key,
  access: Key,
  unlock: Key,
  
  // Lock
  lock: Lock,
  secure: Lock,
  protect: Lock,
  
  // Unlock
  unlock: Unlock,
  open: Unlock,
  access: Unlock,
  
  // Eye
  eye: Eye,
  see: Eye,
  view: Eye,
  
  // Eye Off
  eyeOff: EyeOff,
  hide: EyeOff,
  blind: EyeOff,
  
  // Volume
  volume: Volume2,
  sound: Volume2,
  audio: Volume2,
  
  // Volume Off
  volumeOff: VolumeX,
  mute: VolumeX,
  silent: VolumeX,
  
  // Play
  play: Play,
  start: Play,
  begin: Play,
  
  // Pause
  pause: Pause,
  stop: Pause,
  halt: Pause,
  
  // Stop
  stop: Square,
  end: Square,
  finish: Square,
  
  // Skip
  skip: SkipForward,
  next: SkipForward,
  forward: SkipForward,
  
  // Skip Back
  skipBack: SkipBack,
  previous: SkipBack,
  back: SkipBack,
  
  // Repeat
  repeat: Repeat,
  loop: Repeat,
  cycle: Repeat,
  
  // Shuffle
  shuffle: Shuffle,
  random: Shuffle,
  mix: Shuffle,
  
  // Volume 1
  volume1: Volume1,
  low: Volume1,
  quiet: Volume1,
  
  // Mic
  mic: Mic,
  microphone: Mic,
  record: Mic,
  
  // Mic Off
  micOff: MicOff,
  mute: MicOff,
  silent: MicOff,
  
  // Camera
  camera: Camera,
  photo: Camera,
  picture: Camera,
  
  // Camera Off
  cameraOff: CameraOff,
  noPhoto: CameraOff,
  disabled: CameraOff,
  
  // Video
  video: Video,
  clip: Video,
  movie: Video,
  
  // Video Off
  videoOff: VideoOff,
  noVideo: VideoOff,
  disabled: VideoOff,
  
  // Headphones
  headphones: Headphones,
  audio: Headphones,
  sound: Headphones,
  
  // Speaker
  speaker: Speaker,
  sound: Speaker,
  audio: Speaker,
  
  // Monitor
  monitor: Monitor,
  screen: Monitor,
  display: Monitor,
  
  // Smartphone
  smartphone: Smartphone,
  phone: Smartphone,
  mobile: Smartphone,
  
  // Tablet
  tablet: Tablet,
  pad: Tablet,
  device: Tablet,
  
  // Laptop
  laptop: Laptop,
  computer: Laptop,
  machine: Laptop,
  
  // Desktop
  desktop: Monitor,
  computer: Monitor,
  machine: Monitor,
  
  // Server
  server: Server,
  host: Server,
  machine: Server,
  
  // Hard Drive
  hardDrive: HardDrive,
  storage: HardDrive,
  disk: HardDrive,
  
  // CPU
  cpu: Cpu,
  processor: Cpu,
  chip: Cpu,
  
  // Memory
  memory: MemoryStick,
  ram: MemoryStick,
  storage: MemoryStick,
  
  // WiFi
  wifi: Wifi,
  wireless: Wifi,
  network: Wifi,
  
  // WiFi Off
  wifiOff: WifiOff,
  noWifi: WifiOff,
  offline: WifiOff,
  
  // Bluetooth
  bluetooth: Bluetooth,
  wireless: Bluetooth,
  connect: Bluetooth,
  
  // Bluetooth Off
  bluetoothOff: BluetoothOff,
  noBluetooth: BluetoothOff,
  disconnect: BluetoothOff,
  
  // Battery
  battery: Battery,
  power: Battery,
  energy: Battery,
  
  // Battery Low
  batteryLow: BatteryLow,
  lowPower: BatteryLow,
  warning: BatteryLow,
  
  // Plug
  plug: Plug,
  power: Plug,
  charge: Plug,
  
  // Power
  power: Power,
  on: Power,
  start: Power,
  
  // Power Off
  powerOff: PowerOff,
  off: PowerOff,
  stop: PowerOff,
  
  // Sun
  sun: Sun,
  day: Sun,
  light: Sun,
  
  // Moon
  moon: Moon,
  night: Moon,
  dark: Moon,
  
  // Cloud
  cloud: Cloud,
  sky: Cloud,
  weather: Cloud,
  
  // Cloud Off
  cloudOff: CloudOff,
  noCloud: CloudOff,
  clear: CloudOff,
  
  // Cloud Rain
  cloudRain: CloudRain,
  rain: CloudRain,
  wet: CloudRain,
  
  // Cloud Snow
  cloudSnow: CloudSnow,
  snow: CloudSnow,
  cold: CloudSnow,
  
  // Cloud Lightning
  cloudLightning: CloudLightning,
  lightning: CloudLightning,
  storm: CloudLightning,
  
  // Wind
  wind: Wind,
  air: Wind,
  breeze: Wind,
  
  // Droplets
  droplets: Droplets,
  water: Droplets,
  liquid: Droplets,
  
  // Thermometer
  thermometer: Thermometer,
  temperature: Thermometer,
  heat: Thermometer,
  
  // Gauge
  gauge: Gauge,
  meter: Gauge,
  measure: Gauge,
  
  // Timer
  timer: Timer,
  clock: Timer,
  time: Timer,
  
  // Stopwatch
  stopwatch: Timer,
  timer: Timer,
  time: Timer,
  
  // Clock 3
  clock3: Clock3,
  time: Clock3,
  hour: Clock3,
  
  // Clock 4
  clock4: Clock4,
  time: Clock4,
  hour: Clock4,
  
  // Clock 5
  clock5: Clock5,
  time: Clock5,
  hour: Clock5,
  
  // Clock 6
  clock6: Clock6,
  time: Clock6,
  hour: Clock6,
  
  // Clock 7
  clock7: Clock7,
  time: Clock7,
  hour: Clock7,
  
  // Clock 8
  clock8: Clock8,
  time: Clock8,
  hour: Clock8,
  
  // Clock 9
  clock9: Clock9,
  time: Clock9,
  hour: Clock9,
  
  // Clock 10
  clock10: Clock10,
  time: Clock10,
  hour: Clock10,
  
  // Clock 11
  clock11: Clock11,
  time: Clock11,
  hour: Clock11,
  
  // Clock 12
  clock12: Clock12,
  time: Clock12,
  hour: Clock12,
  
  // Calendar
  calendar: CalendarIcon,
  date: CalendarIcon,
  schedule: CalendarIcon,
  
  // Calendar Days
  calendarDays: CalendarDays,
  dates: CalendarDays,
  schedule: CalendarDays,
  
  // Calendar Check
  calendarCheck: CalendarCheck,
  confirmed: CalendarCheck,
  approved: CalendarCheck,
  
  // Calendar X
  calendarX: CalendarX,
  cancelled: CalendarX,
  rejected: CalendarX,
  
  // Calendar Plus
  calendarPlus: CalendarPlus,
  add: CalendarPlus,
  create: CalendarPlus,
  
  // Calendar Minus
  calendarMinus: CalendarMinus,
  remove: CalendarMinus,
  delete: CalendarMinus,
  
  // Calendar Range
  calendarRange: CalendarRange,
  period: CalendarRange,
  duration: CalendarRange,
  
  // Calendar Search
  calendarSearch: CalendarSearch,
  find: CalendarSearch,
  lookup: CalendarSearch,
  
  // Calendar Clock
  calendarClock: CalendarClock,
  time: CalendarClock,
  schedule: CalendarClock,
  
  // Calendar Heart
  calendarHeart: CalendarHeart,
  favorite: CalendarHeart,
  love: CalendarHeart,
  
  // Calendar Star
  calendarStar: Star,
  favorite: Star,
  important: Star,
  
  // Calendar User
  calendarUser: User,
  person: User,
  member: User,
  
  // Calendar Edit
  calendarEdit: Edit,
  modify: Edit,
  update: Edit,
  
  // Calendar Trash
  calendarTrash: Trash2,
  delete: Trash2,
  remove: Trash2,
  
  // Calendar Settings
  calendarSettings: Settings,
  config: Settings,
  preferences: Settings,
  
  // Calendar Download
  calendarDownload: Download,
  export: Download,
  save: Download,
  
  // Calendar Upload
  calendarUpload: Upload,
  import: Upload,
  add: Upload,
  
  // Calendar Share
  calendarShare: Share2,
  social: Share2,
  distribute: Share2,
  
  // Calendar Copy
  calendarCopy: CalendarCopy,
  duplicate: CalendarCopy,
  clone: CalendarCopy,
  
  // Calendar Move
  calendarMove: CalendarMove,
  transfer: CalendarMove,
  relocate: CalendarMove,
  
  // Calendar Rotate
  calendarRotate: CalendarRotateCcw,
  turn: CalendarRotateCcw,
  flip: CalendarRotateCcw,
  
  // Calendar Rotate Cw
  calendarRotateCw: CalendarRotateCw,
  turn: CalendarRotateCw,
  flip: CalendarRotateCw,
  
  // Calendar Zoom
  calendarZoom: CalendarZoomIn,
  magnify: CalendarZoomIn,
  enlarge: CalendarZoomIn,
  
  // Calendar Zoom Out
  calendarZoomOut: CalendarZoomOut,
  reduce: CalendarZoomOut,
  shrink: CalendarZoomOut,
  
  // Calendar Maximize
  calendarMaximize: CalendarMaximize2,
  fullscreen: CalendarMaximize2,
  expand: CalendarMaximize2,
  
  // Calendar Minimize
  calendarMinimize: CalendarMinimize2,
  collapse: CalendarMinimize2,
  shrink: CalendarMinimize2,
  
  // Calendar Grid
  calendarGrid: CalendarGrid3X3,
  grid: CalendarGrid3X3,
  layout: CalendarGrid3X3,
  
  // Calendar List
  calendarList: CalendarList,
  list: CalendarList,
  table: CalendarList,
  
  // Calendar More
  calendarMore: CalendarMoreHorizontal,
  menu: CalendarMoreHorizontal,
  options: CalendarMoreHorizontal,
  
  // Calendar More Vertical
  calendarMoreVertical: CalendarMoreVertical,
  menu: CalendarMoreVertical,
  options: CalendarMoreVertical,
  
  // Calendar Menu
  calendarMenu: CalendarMenu,
  menu: CalendarMenu,
  navigation: CalendarMenu,
  
  // Calendar X Circle
  calendarXCircle: CalendarXCircle,
  cancel: CalendarXCircle,
  close: CalendarXCircle,
  
  // Calendar Check Circle
  calendarCheckCircle: CalendarCheckCircle,
  confirm: CalendarCheckCircle,
  approve: CalendarCheckCircle,
  
  // Calendar Alert Circle
  calendarAlertCircle: CalendarAlertCircle,
  warning: CalendarAlertCircle,
  alert: CalendarAlertCircle,
  
  // Calendar Info
  calendarInfo: CalendarInfo,
  information: CalendarInfo,
  details: CalendarInfo,
  
  // Calendar Help Circle
  calendarHelpCircle: CalendarHelpCircle,
  help: CalendarHelpCircle,
  support: CalendarHelpCircle,
  
  // Calendar Question Mark Circle
  calendarQuestionMarkCircle: CalendarQuestionMarkCircle,
  question: CalendarQuestionMarkCircle,
  help: CalendarQuestionMarkCircle,
  
  // Calendar Lightbulb
  calendarLightbulb: CalendarLightbulb,
  idea: CalendarLightbulb,
  suggestion: CalendarLightbulb,
  
  // Calendar Rocket
  calendarRocket: CalendarRocket,
  launch: CalendarRocket,
  blast: CalendarRocket,
  
  // Calendar Sparkles
  calendarSparkles: CalendarSparkles,
  magic: CalendarSparkles,
  wonder: CalendarSparkles,
  
  // Calendar Wand
  calendarWand: CalendarWand2,
  magic: CalendarWand2,
  spell: CalendarWand2,
  
  // Calendar Magic
  calendarMagic: CalendarSparkles,
  spell: CalendarSparkles,
  enchant: CalendarSparkles,
  
  // Calendar Crown
  calendarCrown: CalendarCrown,
  king: CalendarCrown,
  royalty: CalendarCrown,
  
  // Calendar Key
  calendarKey: CalendarKey,
  access: CalendarKey,
  unlock: CalendarKey,
  
  // Calendar Lock
  calendarLock: CalendarLock,
  secure: CalendarLock,
  protect: CalendarLock,
  
  // Calendar Unlock
  calendarUnlock: CalendarUnlock,
  open: CalendarUnlock,
  access: CalendarUnlock,
  
  // Calendar Eye
  calendarEye: CalendarEye,
  see: CalendarEye,
  view: CalendarEye,
  
  // Calendar Eye Off
  calendarEyeOff: CalendarEyeOff,
  hide: CalendarEyeOff,
  blind: CalendarEyeOff,
  
  // Calendar Volume
  calendarVolume: CalendarVolume2,
  sound: CalendarVolume2,
  audio: CalendarVolume2,
  
  // Calendar Volume Off
  calendarVolumeOff: CalendarVolumeX,
  mute: CalendarVolumeX,
  silent: CalendarVolumeX,
  
  // Calendar Play
  calendarPlay: CalendarPlay,
  start: CalendarPlay,
  begin: CalendarPlay,
  
  // Calendar Pause
  calendarPause: CalendarPause,
  stop: CalendarPause,
  halt: CalendarPause,
  
  // Calendar Stop
  calendarStop: CalendarSquare,
  end: CalendarSquare,
  finish: CalendarSquare,
  
  // Calendar Skip
  calendarSkip: CalendarSkipForward,
  next: CalendarSkipForward,
  forward: CalendarSkipForward,
  
  // Calendar Skip Back
  calendarSkipBack: CalendarSkipBack,
  previous: CalendarSkipBack,
  back: CalendarSkipBack,
  
  // Calendar Repeat
  calendarRepeat: CalendarRepeat,
  loop: CalendarRepeat,
  cycle: CalendarRepeat,
  
  // Calendar Shuffle
  calendarShuffle: CalendarShuffle,
  random: CalendarShuffle,
  mix: CalendarShuffle,
  
  // Calendar Volume 1
  calendarVolume1: CalendarVolume1,
  low: CalendarVolume1,
  quiet: CalendarVolume1,
  
  // Calendar Mic
  calendarMic: CalendarMic,
  microphone: CalendarMic,
  record: CalendarMic,
  
  // Calendar Mic Off
  calendarMicOff: CalendarMicOff,
  mute: CalendarMicOff,
  silent: CalendarMicOff,
  
  // Calendar Camera
  calendarCamera: CalendarCamera,
  photo: CalendarCamera,
  picture: CalendarCamera,
  
  // Calendar Camera Off
  calendarCameraOff: CalendarCameraOff,
  noPhoto: CalendarCameraOff,
  disabled: CalendarCameraOff,
  
  // Calendar Video
  calendarVideo: CalendarVideo,
  clip: CalendarVideo,
  movie: CalendarVideo,
  
  // Calendar Video Off
  calendarVideoOff: CalendarVideoOff,
  noVideo: CalendarVideoOff,
  disabled: CalendarVideoOff,
  
  // Calendar Headphones
  calendarHeadphones: CalendarHeadphones,
  audio: CalendarHeadphones,
  sound: CalendarHeadphones,
  
  // Calendar Speaker
  calendarSpeaker: CalendarSpeaker,
  sound: CalendarSpeaker,
  audio: CalendarSpeaker,
  
  // Calendar Monitor
  calendarMonitor: CalendarMonitor,
  screen: CalendarMonitor,
  display: CalendarMonitor,
  
  // Calendar Smartphone
  calendarSmartphone: CalendarSmartphone,
  phone: CalendarSmartphone,
  mobile: CalendarSmartphone,
  
  // Calendar Tablet
  calendarTablet: CalendarTablet,
  pad: CalendarTablet,
  device: CalendarTablet,
  
  // Calendar Laptop
  calendarLaptop: CalendarLaptop,
  computer: CalendarLaptop,
  machine: CalendarLaptop,
  
  // Calendar Desktop
  calendarDesktop: CalendarMonitor,
  computer: CalendarMonitor,
  machine: CalendarMonitor,
  
  // Calendar Server
  calendarServer: CalendarServer,
  host: CalendarServer,
  machine: CalendarServer,
  
  // Calendar Hard Drive
  calendarHardDrive: CalendarHardDrive,
  storage: CalendarHardDrive,
  disk: CalendarHardDrive,
  
  // Calendar CPU
  calendarCpu: CalendarCpu,
  processor: CalendarCpu,
  chip: CalendarCpu,
  
  // Calendar Memory
  calendarMemory: CalendarMemoryStick,
  ram: CalendarMemoryStick,
  storage: CalendarMemoryStick,
  
  // Calendar WiFi
  calendarWifi: CalendarWifi,
  wireless: CalendarWifi,
  network: CalendarWifi,
  
  // Calendar WiFi Off
  calendarWifiOff: CalendarWifiOff,
  noWifi: CalendarWifiOff,
  offline: CalendarWifiOff,
  
  // Calendar Bluetooth
  calendarBluetooth: CalendarBluetooth,
  wireless: CalendarBluetooth,
  connect: CalendarBluetooth,
  
  // Calendar Bluetooth Off
  calendarBluetoothOff: CalendarBluetoothOff,
  noBluetooth: CalendarBluetoothOff,
  disconnect: CalendarBluetoothOff,
  
  // Calendar Battery
  calendarBattery: CalendarBattery,
  power: CalendarBattery,
  energy: CalendarBattery,
  
  // Calendar Battery Low
  calendarBatteryLow: CalendarBatteryLow,
  lowPower: CalendarBatteryLow,
  warning: CalendarBatteryLow,
  
  // Calendar Plug
  calendarPlug: CalendarPlug,
  power: CalendarPlug,
  charge: CalendarPlug,
  
  // Calendar Power
  calendarPower: CalendarPower,
  on: CalendarPower,
  start: CalendarPower,
  
  // Calendar Power Off
  calendarPowerOff: CalendarPowerOff,
  off: CalendarPowerOff,
  stop: CalendarPowerOff,
  
  // Calendar Sun
  calendarSun: CalendarSun,
  day: CalendarSun,
  light: CalendarSun,
  
  // Calendar Moon
  calendarMoon: CalendarMoon,
  night: CalendarMoon,
  dark: CalendarMoon,
  
  // Calendar Cloud
  calendarCloud: CalendarCloud,
  sky: CalendarCloud,
  weather: CalendarCloud,
  
  // Calendar Cloud Off
  calendarCloudOff: CalendarCloudOff,
  noCloud: CalendarCloudOff,
  clear: CalendarCloudOff,
  
  // Calendar Cloud Rain
  calendarCloudRain: CalendarCloudRain,
  rain: CalendarCloudRain,
  wet: CalendarCloudRain,
  
  // Calendar Cloud Snow
  calendarCloudSnow: CalendarCloudSnow,
  snow: CalendarCloudSnow,
  cold: CalendarCloudSnow,
  
  // Calendar Cloud Lightning
  calendarCloudLightning: CalendarCloudLightning,
  lightning: CalendarCloudLightning,
  storm: CalendarCloudLightning,
  
  // Calendar Wind
  calendarWind: CalendarWind,
  air: CalendarWind,
  breeze: CalendarWind,
  
  // Calendar Droplets
  calendarDroplets: CalendarDroplets,
  water: CalendarDroplets,
  liquid: CalendarDroplets,
  
  // Calendar Thermometer
  calendarThermometer: CalendarThermometer,
  temperature: CalendarThermometer,
  heat: CalendarThermometer,
  
  // Calendar Gauge
  calendarGauge: CalendarGauge,
  meter: CalendarGauge,
  measure: CalendarGauge,
  
  // Calendar Timer
  calendarTimer: CalendarTimer,
  clock: CalendarTimer,
  time: CalendarTimer,
  
  // Calendar Stopwatch
  calendarStopwatch: CalendarTimer,
  timer: CalendarTimer,
  time: CalendarTimer
} as const;

export function EmptyState({
  icon,
  title,
  description,
  action,
  secondaryAction,
  image,
  className,
  size = "md",
  variant = "default"
}: EmptyStateProps) {
  const Icon = icon || FileText;
  
  const sizeClasses = {
    sm: "py-8",
    md: "py-12",
    lg: "py-16"
  };
  
  const iconSizeClasses = {
    sm: "h-12 w-12",
    md: "h-16 w-16",
    lg: "h-20 w-20"
  };
  
  const titleSizeClasses = {
    sm: "text-lg",
    md: "text-xl",
    lg: "text-2xl"
  };
  
  const descriptionSizeClasses = {
    sm: "text-sm",
    md: "text-base",
    lg: "text-lg"
  };
  
  const variantClasses = {
    default: "text-neutral-600",
    error: "text-error-600",
    success: "text-success-600",
    warning: "text-warning-600",
    info: "text-brand-600"
  };
  
  const iconVariantClasses = {
    default: "text-neutral-400",
    error: "text-error-400",
    success: "text-success-400",
    warning: "text-warning-400",
    info: "text-brand-400"
  };

  return (
    <div className={cn(
      "flex flex-col items-center justify-center text-center",
      sizeClasses[size],
      className
    )} data-testid="empty-state">
      {image ? (
        <img
          src={image}
          alt={title}
          className={cn("mb-6", iconSizeClasses[size])}
          data-testid="empty-state-image"
        />
      ) : (
        <div className={cn(
          "mb-6 rounded-full bg-neutral-100 flex items-center justify-center",
          iconSizeClasses[size]
        )} data-testid="empty-state-icon">
          <Icon className={cn(
            iconSizeClasses[size].replace("h-", "h-").replace("w-", "w-").replace("h-16", "h-8").replace("w-16", "w-8").replace("h-20", "h-10").replace("w-20", "w-10"),
            iconVariantClasses[variant]
          )} />
        </div>
      )}
      
      <h3 className={cn(
        "font-semibold mb-2",
        titleSizeClasses[size],
        variantClasses[variant]
      )} data-testid="empty-state-title">
        {title}
      </h3>
      
      <p className={cn(
        "mb-6 max-w-md",
        descriptionSizeClasses[size],
        variantClasses[variant]
      )} data-testid="empty-state-description">
        {description}
      </p>
      
      {(action || secondaryAction) && (
        <div className="flex flex-col sm:flex-row gap-3" data-testid="empty-state-actions">
          {action && (
            <Button
              onClick={action.onClick}
              variant={action.variant || "default"}
              className={action.variant === "default" ? "btn-premium" : ""}
              data-testid="empty-state-primary-action"
            >
              {action.label}
            </Button>
          )}
          
          {secondaryAction && (
            <Button
              onClick={secondaryAction.onClick}
              variant={secondaryAction.variant || "outline"}
              className={secondaryAction.variant === "outline" ? "btn-premium-outline" : ""}
              data-testid="empty-state-secondary-action"
            >
              {secondaryAction.label}
            </Button>
          )}
        </div>
      )}
    </div>
  );
}

// Helper function to get icon by name
export function getIconByName(name: string): React.ComponentType<{ className?: string }> {
  const Icon = ICON_MAP[name.toLowerCase() as keyof typeof ICON_MAP];
  return Icon || FileText;
}

// Helper function to create empty state with icon by name
export function createEmptyState(
  name: string,
  title: string,
  description: string,
  action?: EmptyStateProps['action'],
  secondaryAction?: EmptyStateProps['secondaryAction']
): EmptyStateProps {
  return {
    icon: getIconByName(name),
    title,
    description,
    action,
    secondaryAction
  };
}
