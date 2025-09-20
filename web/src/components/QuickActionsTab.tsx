"use client";

import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Zap,
  FileText,
  Calendar,
  BarChart3,
  Users,
  Search,
  Image,
  Upload,
  Download,
  MessageSquare,
  Settings,
  Play,
  Pause,
  Stop,
  RotateCcw,
  Plus,
  Edit,
  Trash2,
  Copy,
  Share2,
  Heart,
  Star,
  Bookmark,
  Tag,
  Filter,
  SortAsc,
  SortDesc,
  MoreHorizontal,
  ExternalLink,
  AlertCircle,
  CheckCircle,
  XCircle,
  Loader2,
  Clock,
  Activity,
  TrendingUp,
  Globe,
  Newspaper,
  Video,
  Music,
  MapPin,
  Phone,
  Mail,
  Map,
  Info,
  HelpCircle,
  Save,
  Archive,
  Send,
  Sparkles,
  Target,
  Rocket,
  Shield,
  Lock,
  Unlock,
  Eye,
  EyeOff,
  RefreshCw,
  RotateCcw as RotateCcwIcon,
  Maximize,
  Minimize,
  Move,
  Grip,
  Grid,
  List,
  Layout,
  Layers,
  Palette,
  Brush,
  Scissors,
  Crop,
  Focus,
  ZoomIn,
  ZoomOut,
  RotateCw,
  FlipHorizontal,
  FlipVertical,
  Type,
  Bold,
  Italic,
  Underline,
  Strikethrough,
  AlignLeft,
  AlignCenter,
  AlignRight,
  AlignJustify,
  Indent,
  Outdent,
  List as ListIcon,
  ListOrdered,
  Quote,
  Code,
  Terminal,
  Database,
  Server,
  Cloud,
  Wifi,
  WifiOff,
  Bluetooth,
  Battery,
  BatteryLow,
  Volume2,
  VolumeX,
  Mic,
  MicOff,
  Camera,
  CameraOff,
  Monitor,
  Smartphone,
  Tablet,
  Laptop,
  Desktop,
  Headphones,
  Speaker,
  Radio,
  Tv,
  Gamepad2,
  Joystick,
  Mouse,
  Keyboard,
  HardDrive,
  Cpu,
  MemoryStick,
  Disc,
  Disc3,
  Cd,
  Dvd,
  Cassette,
  Vinyl,
  Radio as RadioIcon,
  Podcast,
  Rss,
  Atom,
  Globe2,
  Compass,
  Map as MapIcon,
  Navigation,
  Route,
  Flag,
  FlagOff,
  Award,
  Trophy,
  Medal,
  Crown,
  Gem,
  Diamond,
  Circle,
  Square,
  Triangle,
  Hexagon,
  Pentagon,
  Octagon,
  Star as StarIcon,
  Heart as HeartIcon,
  Smile,
  Frown,
  Meh,
  Laugh,
  Angry,
  Sad,
  Surprised,
  Confused,
  Kiss,
  Wink,
  Tongue,
  ThumbsUp,
  ThumbsDown,
  Clap,
  Wave,
  Peace,
  Victory,
  Ok,
  No,
  Yes,
  Maybe,
  Question,
  Exclamation,
  Warning,
  Error,
  Success,
  Info as InfoIcon,
  Lightbulb,
  Bulb,
  Sun,
  Moon,
  Cloud as CloudIcon,
  CloudRain,
  CloudSnow,
  CloudLightning,
  CloudDrizzle,
  CloudHail,
  CloudFog,
  Wind,
  Thermometer,
  Droplets,
  Flame,
  Snowflake,
  Umbrella,
  Rainbow,
  Zap as ZapIcon,
  Thunder,
  Hurricane,
  Tornado,
  Earthquake,
  Volcano,
  Mountain,
  Hills,
  Trees,
  Leaf,
  Flower,
  Rose,
  Tulip,
  Sunflower,
  Cherry,
  Apple,
  Banana,
  Orange,
  Lemon,
  Grape,
  Strawberry,
  Watermelon,
  Pineapple,
  Peach,
  Pear,
  Avocado,
  Carrot,
  Broccoli,
  Corn,
  Tomato,
  Potato,
  Onion,
  Garlic,
  Pepper,
  Cucumber,
  Lettuce,
  Spinach,
  Cabbage,
  Cauliflower,
  Eggplant,
  Pumpkin,
  Squash,
  Radish,
  Beet,
  Turnip,
  Parsnip,
  Celery,
  Asparagus,
  Artichoke,
  Mushroom,
  Peanut,
  Almond,
  Walnut,
  Cashew,
  Pistachio,
  Hazelnut,
  Chestnut,
  Coconut,
  Bread,
  Croissant,
  Bagel,
  Pretzel,
  Cookie,
  Cake,
  Pie,
  Donut,
  Muffin,
  Pancake,
  Waffle,
  Toast,
  Sandwich,
  Burger,
  Hotdog,
  Pizza,
  Taco,
  Burrito,
  Quesadilla,
  Nachos,
  Popcorn,
  Chips,
  Crackers,
  Nuts,
  Seeds,
  Granola,
  Cereal,
  Oatmeal,
  Yogurt,
  Cheese,
  Milk,
  Butter,
  Cream,
  IceCream,
  Sorbet,
  Gelato,
  Pudding,
  Jello,
  Candy,
  Chocolate,
  Lollipop,
  Gum,
  Marshmallow,
  CottonCandy,
  Honey,
  Syrup,
  Jam,
  Jelly,
  Marmalade,
  PeanutButter,
  Nutella,
  Ketchup,
  Mustard,
  Mayo,
  Ranch,
  BBQ,
  HotSauce,
  SoySauce,
  Worcestershire,
  Vinegar,
  Oil,
  Salt,
  Pepper as PepperIcon,
  Sugar,
  Flour,
  Rice,
  Pasta,
  Noodles,
  Quinoa,
  Barley,
  Oats,
  Wheat,
  Corn as CornIcon,
  Beans,
  Lentils,
  Chickpeas,
  Peas,
  GreenBeans,
  LimaBeans,
  BlackBeans,
  KidneyBeans,
  PintoBeans,
  NavyBeans,
  GarbanzoBeans,
  SoyBeans,
  Tofu,
  Tempeh,
  Seitan,
  Meat,
  Beef,
  Pork,
  Lamb,
  Chicken,
  Turkey,
  Duck,
  Fish,
  Salmon,
  Tuna,
  Cod,
  Halibut,
  Shrimp,
  Crab,
  Lobster,
  Scallops,
  Mussels,
  Clams,
  Oysters,
  Octopus,
  Squid,
  Eel,
  Caviar,
  Roe,
  Eggs,
  Omelet,
  Scrambled,
  Fried,
  Poached,
  Boiled,
  Deviled,
  Benedict,
  Frittata,
  Quiche,
  Souffle,
  Casserole,
  Stew,
  Soup,
  Broth,
  Stock,
  Bouillon,
  Consomme,
  Bisque,
  Chowder,
  Gazpacho,
  Minestrone,
  Lentil,
  Bean,
  Vegetable,
  Chicken as ChickenIcon,
  Beef as BeefIcon,
  Pork as PorkIcon,
  Fish as FishIcon,
  Seafood,
  Pasta as PastaIcon,
  Rice as RiceIcon,
  Noodle,
  Ramen,
  Udon,
  Soba,
  Pho,
  PadThai,
  LoMein,
  ChowMein,
  FriedRice,
  Risotto,
  Paella,
  Jambalaya,
  Gumbo,
  Etouffee,
  Creole,
  Cajun,
  TexMex,
  Mexican,
  Italian,
  French,
  Chinese,
  Japanese,
  Korean,
  Thai,
  Vietnamese,
  Indian,
  MiddleEastern,
  Mediterranean,
  Greek,
  Spanish,
  German,
  British,
  Irish,
  Scottish,
  Welsh,
  Scandinavian,
  Russian,
  Polish,
  Hungarian,
  Romanian,
  Bulgarian,
  Croatian,
  Serbian,
  Bosnian,
  Montenegrin,
  Macedonian,
  Albanian,
  Kosovar,
  Moldovan,
  Ukrainian,
  Belarusian,
  Lithuanian,
  Latvian,
  Estonian,
  Finnish,
  Swedish,
  Norwegian,
  Danish,
  Icelandic,
  Dutch,
  Belgian,
  Swiss,
  Austrian,
  Czech,
  Slovak,
  Slovenian,
  Hungarian as HungarianIcon,
  Romanian as RomanianIcon,
  Bulgarian as BulgarianIcon,
  Croatian as CroatianIcon,
  Serbian as SerbianIcon,
  Bosnian as BosnianIcon,
  Montenegrin as MontenegrinIcon,
  Macedonian as MacedonianIcon,
  Albanian as AlbanianIcon,
  Kosovar as KosovarIcon,
  Moldovan as MoldovanIcon,
  Ukrainian as UkrainianIcon,
  Belarusian as BelarusianIcon,
  Lithuanian as LithuanianIcon,
  Latvian as LatvianIcon,
  Estonian as EstonianIcon,
  Finnish as FinnishIcon,
  Swedish as SwedishIcon,
  Norwegian as NorwegianIcon,
  Danish as DanishIcon,
  Icelandic as IcelandicIcon,
  Dutch as DutchIcon,
  Belgian as BelgianIcon,
  Swiss as SwissIcon,
  Austrian as AustrianIcon,
  Czech as CzechIcon,
  Slovak as SlovakIcon,
  Slovenian as SlovenianIcon,
  Book,
  Presentation,
  Folder,
  Cloud
} from 'lucide-react';
import { toast } from 'react-hot-toast';

interface QuickAction {
  id: string;
  title: string;
  description?: string;
  icon: React.ReactNode;
  action: () => void | Promise<void>;
  keywords?: string[];
  disabled?: boolean;
  loading?: boolean;
  badge?: string;
  color?: string;
  category?: string;
}

interface QuickActionsTabProps {
  className?: string;
  defaultTab?: string;
  showCategories?: boolean;
  maxActionsPerTab?: number;
}

export function QuickActionsTab({ 
  className = "",
  defaultTab = "content",
  showCategories = true,
  maxActionsPerTab = 12
}: QuickActionsTabProps) {
  const [activeTab, setActiveTab] = useState(defaultTab);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const handleAction = async (action: QuickAction) => {
    if (action.disabled || action.loading) return;
    
    setActionLoading(action.id);
    
    try {
      await action.action();
    } catch (error) {
      toast.error('Failed to execute action');
      console.error('Quick action error:', error);
    } finally {
      setActionLoading(null);
    }
  };

  const contentActions: QuickAction[] = [
    {
      id: 'create-draft',
      title: 'Create Draft',
      description: 'Start writing new content',
      icon: <FileText className="h-4 w-4" />,
      action: () => {
        toast.success('Creating new draft...');
        window.location.href = '/composer';
      },
      category: 'content',
      keywords: ['create', 'draft', 'content', 'write']
    },
    {
      id: 'create-post',
      title: 'Create Post',
      description: 'Create social media post',
      icon: <Edit className="h-4 w-4" />,
      action: () => {
        toast.success('Creating new post...');
        window.location.href = '/composer?type=post';
      },
      category: 'content',
      keywords: ['create', 'post', 'social', 'media']
    },
    {
      id: 'create-article',
      title: 'Create Article',
      description: 'Write long-form article',
      icon: <Newspaper className="h-4 w-4" />,
      action: () => {
        toast.success('Creating new article...');
        window.location.href = '/composer?type=article';
      },
      category: 'content',
      keywords: ['create', 'article', 'blog', 'long-form']
    },
    {
      id: 'create-video',
      title: 'Create Video',
      description: 'Plan video content',
      icon: <Video className="h-4 w-4" />,
      action: () => {
        toast.success('Creating video content...');
        window.location.href = '/composer?type=video';
      },
      category: 'content',
      keywords: ['create', 'video', 'content', 'plan']
    },
    {
      id: 'create-podcast',
      title: 'Create Podcast',
      description: 'Plan podcast episode',
      icon: <Podcast className="h-4 w-4" />,
      action: () => {
        toast.success('Creating podcast content...');
        window.location.href = '/composer?type=podcast';
      },
      category: 'content',
      keywords: ['create', 'podcast', 'audio', 'episode']
    },
    {
      id: 'create-newsletter',
      title: 'Create Newsletter',
      description: 'Write email newsletter',
      icon: <Mail className="h-4 w-4" />,
      action: () => {
        toast.success('Creating newsletter...');
        window.location.href = '/composer?type=newsletter';
      },
      category: 'content',
      keywords: ['create', 'newsletter', 'email', 'marketing']
    },
    {
      id: 'create-press-release',
      title: 'Create Press Release',
      description: 'Write press release',
      icon: <Newspaper className="h-4 w-4" />,
      action: () => {
        toast.success('Creating press release...');
        window.location.href = '/composer?type=press-release';
      },
      category: 'content',
      keywords: ['create', 'press', 'release', 'announcement']
    },
    {
      id: 'create-case-study',
      title: 'Create Case Study',
      description: 'Write case study',
      icon: <FileText className="h-4 w-4" />,
      action: () => {
        toast.success('Creating case study...');
        window.location.href = '/composer?type=case-study';
      },
      category: 'content',
      keywords: ['create', 'case', 'study', 'analysis']
    },
    {
      id: 'create-whitepaper',
      title: 'Create Whitepaper',
      description: 'Write whitepaper',
      icon: <FileText className="h-4 w-4" />,
      action: () => {
        toast.success('Creating whitepaper...');
        window.location.href = '/composer?type=whitepaper';
      },
      category: 'content',
      keywords: ['create', 'whitepaper', 'research', 'report']
    },
    {
      id: 'create-ebook',
      title: 'Create E-book',
      description: 'Write e-book',
      icon: <Book className="h-4 w-4" />,
      action: () => {
        toast.success('Creating e-book...');
        window.location.href = '/composer?type=ebook';
      },
      category: 'content',
      keywords: ['create', 'ebook', 'book', 'digital']
    },
    {
      id: 'create-infographic',
      title: 'Create Infographic',
      description: 'Design infographic',
      icon: <Image className="h-4 w-4" />,
      action: () => {
        toast.success('Creating infographic...');
        window.location.href = '/composer?type=infographic';
      },
      category: 'content',
      keywords: ['create', 'infographic', 'visual', 'design']
    },
    {
      id: 'create-presentation',
      title: 'Create Presentation',
      description: 'Create slide presentation',
      icon: <Presentation className="h-4 w-4" />,
      action: () => {
        toast.success('Creating presentation...');
        window.location.href = '/composer?type=presentation';
      },
      category: 'content',
      keywords: ['create', 'presentation', 'slides', 'pitch']
    }
  ];

  const scheduleActions: QuickAction[] = [
    {
      id: 'schedule-now',
      title: 'Schedule Now',
      description: 'Schedule content for immediate publishing',
      icon: <Clock className="h-4 w-4" />,
      action: () => {
        toast.success('Opening scheduler...');
        window.location.href = '/calendar?action=schedule';
      },
      category: 'schedule',
      keywords: ['schedule', 'publish', 'now', 'immediate']
    },
    {
      id: 'schedule-later',
      title: 'Schedule Later',
      description: 'Schedule content for future publishing',
      icon: <Calendar className="h-4 w-4" />,
      action: () => {
        toast.success('Opening scheduler...');
        window.location.href = '/calendar?action=schedule&type=later';
      },
      category: 'schedule',
      keywords: ['schedule', 'publish', 'later', 'future']
    },
    {
      id: 'schedule-recurring',
      title: 'Schedule Recurring',
      description: 'Set up recurring content schedule',
      icon: <RotateCcw className="h-4 w-4" />,
      action: () => {
        toast.success('Setting up recurring schedule...');
        window.location.href = '/calendar?action=recurring';
      },
      category: 'schedule',
      keywords: ['schedule', 'recurring', 'repeat', 'automation']
    },
    {
      id: 'schedule-bulk',
      title: 'Bulk Schedule',
      description: 'Schedule multiple pieces of content',
      icon: <Layers className="h-4 w-4" />,
      action: () => {
        toast.success('Opening bulk scheduler...');
        window.location.href = '/calendar?action=bulk';
      },
      category: 'schedule',
      keywords: ['schedule', 'bulk', 'multiple', 'batch']
    },
    {
      id: 'schedule-optimal',
      title: 'Optimal Timing',
      description: 'Schedule at optimal times for engagement',
      icon: <Target className="h-4 w-4" />,
      action: () => {
        toast.success('Finding optimal timing...');
        window.location.href = '/calendar?action=optimal';
      },
      category: 'schedule',
      keywords: ['schedule', 'optimal', 'timing', 'engagement']
    },
    {
      id: 'schedule-timezone',
      title: 'Timezone Schedule',
      description: 'Schedule across different timezones',
      icon: <Globe className="h-4 w-4" />,
      action: () => {
        toast.success('Opening timezone scheduler...');
        window.location.href = '/calendar?action=timezone';
      },
      category: 'schedule',
      keywords: ['schedule', 'timezone', 'global', 'international']
    }
  ];

  const analyticsActions: QuickAction[] = [
    {
      id: 'view-analytics',
      title: 'View Analytics',
      description: 'Check performance metrics and insights',
      icon: <BarChart3 className="h-4 w-4" />,
      action: () => {
        toast.success('Loading analytics...');
        window.location.href = '/analytics';
      },
      category: 'analytics',
      keywords: ['analytics', 'metrics', 'performance', 'insights']
    },
    {
      id: 'view-reports',
      title: 'View Reports',
      description: 'Generate detailed reports',
      icon: <FileText className="h-4 w-4" />,
      action: () => {
        toast.success('Generating reports...');
        window.location.href = '/reports';
      },
      category: 'analytics',
      keywords: ['reports', 'analytics', 'detailed', 'generate']
    },
    {
      id: 'view-trends',
      title: 'View Trends',
      description: 'Analyze content trends and patterns',
      icon: <TrendingUp className="h-4 w-4" />,
      action: () => {
        toast.success('Analyzing trends...');
        window.location.href = '/analytics?view=trends';
      },
      category: 'analytics',
      keywords: ['trends', 'patterns', 'analysis', 'insights']
    },
    {
      id: 'view-engagement',
      title: 'View Engagement',
      description: 'Check engagement metrics',
      icon: <Heart className="h-4 w-4" />,
      action: () => {
        toast.success('Loading engagement data...');
        window.location.href = '/analytics?view=engagement';
      },
      category: 'analytics',
      keywords: ['engagement', 'likes', 'shares', 'comments']
    },
    {
      id: 'view-reach',
      title: 'View Reach',
      description: 'Check reach and impressions',
      icon: <Eye className="h-4 w-4" />,
      action: () => {
        toast.success('Loading reach data...');
        window.location.href = '/analytics?view=reach';
      },
      category: 'analytics',
      keywords: ['reach', 'impressions', 'views', 'audience']
    },
    {
      id: 'view-conversion',
      title: 'View Conversion',
      description: 'Check conversion rates and ROI',
      icon: <Target className="h-4 w-4" />,
      action: () => {
        toast.success('Loading conversion data...');
        window.location.href = '/analytics?view=conversion';
      },
      category: 'analytics',
      keywords: ['conversion', 'roi', 'sales', 'leads']
    }
  ];

  const teamActions: QuickAction[] = [
    {
      id: 'manage-team',
      title: 'Manage Team',
      description: 'Add, remove, or manage team members',
      icon: <Users className="h-4 w-4" />,
      action: () => {
        toast.success('Opening team management...');
        window.location.href = '/team';
      },
      category: 'team',
      keywords: ['team', 'members', 'users', 'manage']
    },
    {
      id: 'view-collaboration',
      title: 'View Collaboration',
      description: 'View team collaboration hub',
      icon: <MessageSquare className="h-4 w-4" />,
      action: () => {
        toast.success('Opening collaboration hub...');
        window.location.href = '/collaboration';
      },
      category: 'team',
      keywords: ['collaboration', 'team', 'messages', 'hub']
    },
    {
      id: 'view-permissions',
      title: 'View Permissions',
      description: 'Manage user permissions and roles',
      icon: <Shield className="h-4 w-4" />,
      action: () => {
        toast.success('Opening permissions...');
        window.location.href = '/team?view=permissions';
      },
      category: 'team',
      keywords: ['permissions', 'roles', 'access', 'security']
    },
    {
      id: 'view-activity',
      title: 'View Activity',
      description: 'Check team activity and updates',
      icon: <Activity className="h-4 w-4" />,
      action: () => {
        toast.success('Loading team activity...');
        window.location.href = '/team?view=activity';
      },
      category: 'team',
      keywords: ['activity', 'updates', 'team', 'monitoring']
    },
    {
      id: 'view-workload',
      title: 'View Workload',
      description: 'Check team workload and capacity',
      icon: <BarChart3 className="h-4 w-4" />,
      action: () => {
        toast.success('Loading workload data...');
        window.location.href = '/team?view=workload';
      },
      category: 'team',
      keywords: ['workload', 'capacity', 'team', 'planning']
    },
    {
      id: 'view-performance',
      title: 'View Performance',
      description: 'Check team performance metrics',
      icon: <TrendingUp className="h-4 w-4" />,
      action: () => {
        toast.success('Loading performance data...');
        window.location.href = '/team?view=performance';
      },
      category: 'team',
      keywords: ['performance', 'metrics', 'team', 'evaluation']
    }
  ];

  const automationActions: QuickAction[] = [
    {
      id: 'view-automation',
      title: 'View Automation',
      description: 'Manage automated workflows and rules',
      icon: <Zap className="h-4 w-4" />,
      action: () => {
        toast.success('Opening automation dashboard...');
        window.location.href = '/automation';
      },
      category: 'automation',
      keywords: ['automation', 'workflows', 'rules', 'auto']
    },
    {
      id: 'create-workflow',
      title: 'Create Workflow',
      description: 'Create new automation workflow',
      icon: <Plus className="h-4 w-4" />,
      action: () => {
        toast.success('Creating new workflow...');
        window.location.href = '/automation?action=create';
      },
      category: 'automation',
      keywords: ['create', 'workflow', 'automation', 'new']
    },
    {
      id: 'view-rules',
      title: 'View Rules',
      description: 'Manage automation rules',
      icon: <Settings className="h-4 w-4" />,
      action: () => {
        toast.success('Opening rules management...');
        window.location.href = '/automation?view=rules';
      },
      category: 'automation',
      keywords: ['rules', 'automation', 'manage', 'settings']
    },
    {
      id: 'view-triggers',
      title: 'View Triggers',
      description: 'Manage automation triggers',
      icon: <Play className="h-4 w-4" />,
      action: () => {
        toast.success('Opening triggers...');
        window.location.href = '/automation?view=triggers';
      },
      category: 'automation',
      keywords: ['triggers', 'automation', 'events', 'start']
    },
    {
      id: 'view-actions',
      title: 'View Actions',
      description: 'Manage automation actions',
      icon: <Target className="h-4 w-4" />,
      action: () => {
        toast.success('Opening actions...');
        window.location.href = '/automation?view=actions';
      },
      category: 'automation',
      keywords: ['actions', 'automation', 'execute', 'perform']
    },
    {
      id: 'view-logs',
      title: 'View Logs',
      description: 'Check automation execution logs',
      icon: <FileText className="h-4 w-4" />,
      action: () => {
        toast.success('Loading execution logs...');
        window.location.href = '/automation?view=logs';
      },
      category: 'automation',
      keywords: ['logs', 'execution', 'automation', 'history']
    }
  ];

  const mediaActions: QuickAction[] = [
    {
      id: 'upload-media',
      title: 'Upload Media',
      description: 'Upload images, videos, or other media files',
      icon: <Upload className="h-4 w-4" />,
      action: () => {
        toast.success('Opening media upload...');
        window.location.href = '/media?action=upload';
      },
      category: 'media',
      keywords: ['upload', 'media', 'images', 'videos', 'files']
    },
    {
      id: 'view-media',
      title: 'View Media',
      description: 'Browse and manage media library',
      icon: <Image className="h-4 w-4" />,
      action: () => {
        toast.success('Opening media library...');
        window.location.href = '/media';
      },
      category: 'media',
      keywords: ['view', 'media', 'library', 'browse']
    },
    {
      id: 'edit-media',
      title: 'Edit Media',
      description: 'Edit images and videos',
      icon: <Edit className="h-4 w-4" />,
      action: () => {
        toast.success('Opening media editor...');
        window.location.href = '/media?action=edit';
      },
      category: 'media',
      keywords: ['edit', 'media', 'images', 'videos', 'modify']
    },
    {
      id: 'organize-media',
      title: 'Organize Media',
      description: 'Organize and categorize media files',
      icon: <Folder className="h-4 w-4" />,
      action: () => {
        toast.success('Opening media organizer...');
        window.location.href = '/media?action=organize';
      },
      category: 'media',
      keywords: ['organize', 'media', 'categorize', 'sort']
    },
    {
      id: 'optimize-media',
      title: 'Optimize Media',
      description: 'Optimize media files for web',
      icon: <Zap className="h-4 w-4" />,
      action: () => {
        toast.success('Opening media optimizer...');
        window.location.href = '/media?action=optimize';
      },
      category: 'media',
      keywords: ['optimize', 'media', 'compress', 'web']
    },
    {
      id: 'backup-media',
      title: 'Backup Media',
      description: 'Backup media files to cloud storage',
      icon: <Cloud className="h-4 w-4" />,
      action: () => {
        toast.success('Starting media backup...');
        window.location.href = '/media?action=backup';
      },
      category: 'media',
      keywords: ['backup', 'media', 'cloud', 'storage']
    }
  ];

  const tabs = [
    { id: 'content', label: 'Content', icon: <FileText className="h-4 w-4" />, actions: contentActions },
    { id: 'schedule', label: 'Schedule', icon: <Calendar className="h-4 w-4" />, actions: scheduleActions },
    { id: 'analytics', label: 'Analytics', icon: <BarChart3 className="h-4 w-4" />, actions: analyticsActions },
    { id: 'team', label: 'Team', icon: <Users className="h-4 w-4" />, actions: teamActions },
    { id: 'automation', label: 'Automation', icon: <Zap className="h-4 w-4" />, actions: automationActions },
    { id: 'media', label: 'Media', icon: <Image className="h-4 w-4" />, actions: mediaActions }
  ];

  const currentTab = tabs.find(tab => tab.id === activeTab);
  const displayActions = currentTab?.actions.slice(0, maxActionsPerTab) || [];

  return (
    <div className={className}>
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-6">
          {tabs.map((tab) => (
            <TabsTrigger key={tab.id} value={tab.id} className="flex items-center gap-2">
              {tab.icon}
              <span className="hidden sm:inline">{tab.label}</span>
            </TabsTrigger>
          ))}
        </TabsList>

        {tabs.map((tab) => (
          <TabsContent key={tab.id} value={tab.id} className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {tab.icon}
                  {tab.label} Actions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                  {displayActions.map((action) => (
                    <Button
                      key={action.id}
                      variant="outline"
                      className="h-20 flex flex-col gap-2 hover:bg-accent transition-colors"
                      onClick={() => handleAction(action)}
                      disabled={action.disabled || actionLoading === action.id}
                    >
                      {actionLoading === action.id ? (
                        <Loader2 className="h-5 w-5 animate-spin" />
                      ) : (
                        <div className="h-5 w-5">{action.icon}</div>
                      )}
                      <span className="text-xs text-center">{action.title}</span>
                      {action.badge && (
                        <Badge variant="secondary" className="text-xs">
                          {action.badge}
                        </Badge>
                      )}
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
}
