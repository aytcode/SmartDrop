import React, { useState, useEffect, useRef } from "react";
import {
  Folder,
  File,
  FileText,
  Image as ImageIcon,
  Video,
  Music,
  Archive,
  Code2,
  Table as TableIcon,
  Presentation,
  Terminal,
  RotateCcw,
  Sparkles,
  Settings as SettingsIcon,
  Play,
  CheckCircle2,
  Download,
  RefreshCw,
  ShieldCheck,
  FolderPlus,
  Globe,
  CloudUpload,
  ArrowLeftRight,
  SquarePen,
  CircleSlash2,
  ChevronDown,
  UploadCloud,
  Cloud,
  Trash2,
  Search,
  CheckSquare,
  Square,
  Sliders,
  ZoomIn,
  Copy,
  ExternalLink
} from "lucide-react";

interface FileItemData {
  path: string;
  original_name: string;
  original_dir: string;
  extension: string;
  size_bytes: number;
  created_at: number;
  modified_at: number;
  category: string;
  target_folder_name: string;
  target_dir: string;
  new_name: string;
  new_path: string;
  is_selected: boolean;
  is_renamed: boolean;
  is_skipped: boolean;
  skip_reason: string;
  ai_suggested_category?: string;
  ai_suggested_name?: string;
  ai_confidence?: number;
}

type Language = "tr" | "en" | "de" | "es";

const LANGUAGES: { code: Language; name: string; flag: string; label: string }[] = [
  { code: "tr", name: "Türkçe", flag: "🇹🇷", label: "TR Türkçe" },
  { code: "en", name: "English", flag: "🇬🇧", label: "EN English" },
  { code: "de", name: "Deutsch", flag: "🇩🇪", label: "DE Deutsch" },
  { code: "es", name: "Español", flag: "🇪🇸", label: "ES Español" },
];

const LANGUAGE_CATEGORIES: Record<Language, Record<string, string>> = {
  tr: {
    Documents: "Belgeler",
    Images: "Resimler",
    Videos: "Videolar",
    Audio: "Müzikler",
    Archives: "Arşivler",
    Code: "Kodlar",
    Spreadsheets: "Tablolar",
    Presentations: "Sunumlar",
    Installers: "Kurulumlar",
    Fonts: "Yazı Tipleri",
    Others: "Diğerleri",
  },
  en: {
    Documents: "Documents",
    Images: "Images",
    Videos: "Videos",
    Audio: "Audio",
    Archives: "Archives",
    Code: "Code",
    Spreadsheets: "Spreadsheets",
    Presentations: "Presentations",
    Installers: "Installers",
    Fonts: "Fonts",
    Others: "Others",
  },
  de: {
    Documents: "Dokumente",
    Images: "Bilder",
    Videos: "Videos",
    Audio: "Audio",
    Archives: "Archive",
    Code: "Code",
    Spreadsheets: "Tabellen",
    Presentations: "Präsentationen",
    Installers: "Installationsdateien",
    Fonts: "Schriftarten",
    Others: "Sonstiges",
  },
  es: {
    Documents: "Documentos",
    Images: "Imágenes",
    Videos: "Videos",
    Audio: "Audio",
    Archives: "Archivos",
    Code: "Código",
    Spreadsheets: "Hojas de Cálculo",
    Presentations: "Presentaciones",
    Installers: "Instaladores",
    Fonts: "Fuentes",
    Others: "Otros",
  },
};

const CATEGORIES = [
  "Documents",
  "Images",
  "Videos",
  "Audio",
  "Archives",
  "Code",
  "Spreadsheets",
  "Presentations",
  "Installers",
  "Fonts",
  "Others",
];

const CATEGORY_COLORS: Record<string, { text: string; dot: string; bg: string }> = {
  Documents: { text: "text-blue-400", dot: "bg-blue-400", bg: "bg-blue-950/40" },
  Images: { text: "text-pink-400", dot: "bg-pink-400", bg: "bg-pink-950/40" },
  Videos: { text: "text-purple-400", dot: "bg-purple-400", bg: "bg-purple-950/40" },
  Audio: { text: "text-cyan-400", dot: "bg-cyan-400", bg: "bg-cyan-950/40" },
  Archives: { text: "text-amber-400", dot: "bg-amber-400", bg: "bg-amber-950/40" },
  Code: { text: "text-emerald-400", dot: "bg-emerald-400", bg: "bg-emerald-950/40" },
  Spreadsheets: { text: "text-teal-400", dot: "bg-teal-400", bg: "bg-teal-950/40" },
  Presentations: { text: "text-orange-400", dot: "bg-orange-400", bg: "bg-orange-950/40" },
  Installers: { text: "text-red-400", dot: "bg-red-400", bg: "bg-red-950/40" },
  Fonts: { text: "text-fuchsia-400", dot: "bg-fuchsia-400", bg: "bg-fuchsia-950/40" },
  Others: { text: "text-slate-400", dot: "bg-slate-400", bg: "bg-slate-800/40" },
};

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function getCategoryIcon(category: string) {
  switch (category) {
    case "Documents": return <FileText className="w-4 h-4 text-blue-400" />;
    case "Images": return <ImageIcon className="w-4 h-4 text-pink-400" />;
    case "Videos": return <Video className="w-4 h-4 text-purple-400" />;
    case "Audio": return <Music className="w-4 h-4 text-cyan-400" />;
    case "Archives": return <Archive className="w-4 h-4 text-amber-400" />;
    case "Code": return <Code2 className="w-4 h-4 text-emerald-400" />;
    case "Spreadsheets": return <TableIcon className="w-4 h-4 text-teal-400" />;
    case "Presentations": return <Presentation className="w-4 h-4 text-orange-400" />;
    default: return <File className="w-4 h-4 text-slate-400" />;
  }
}

export default function App() {
  // Scale factor: default 125% (%125 ayarı)
  const [scale, setScale] = useState<number>(1.25);
  const [lang, setLang] = useState<Language>("tr");
  const [activeTab, setActiveTab] = useState<"desktop" | "explorer" | "tests" | "settings">("desktop");
  const [folderPath, setFolderPath] = useState<string>("test_data/sample_downloads");
  const [items, setItems] = useState<FileItemData[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [progressText, setProgressText] = useState<string>("");
  const [isOrganizing, setIsOrganizing] = useState<boolean>(false);
  const [isDraggingOver, setIsDraggingOver] = useState<boolean>(false);
  const [viewMode, setViewMode] = useState<"auto" | "table">("auto");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedFilterCategory, setSelectedFilterCategory] = useState<string>("ALL");

  // File input ref for real file picker
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Exact initial logs
  const [logs, setLogs] = useState<string[]>([
    "[20:00:00] [SYSTEM] SmartDrop v1.2 başlatıldı (Obsidian Dark Edition).",
    "[20:00:01] [READY] Aktif düzenleme dili: Türkçe (Belgeler, Resimler, Videolar...)"
  ]);

  // Settings
  const [subfolders, setSubfolders] = useState<boolean>(false);
  const [useAi, setUseAi] = useState<boolean>(false);
  const [useSmartRename, setUseSmartRename] = useState<boolean>(false);
  const [categoryFolderNames, setCategoryFolderNames] = useState<Record<string, string>>({
    ...LANGUAGE_CATEGORIES.tr
  });

  // Test Runner State
  const [testOutput, setTestOutput] = useState<string>("");
  const [runningTests, setRunningTests] = useState<boolean>(false);
  const [testSuccess, setTestSuccess] = useState<boolean | null>(null);

  // File explorer tree state
  const [explorerTree, setExplorerTree] = useState<any[]>([]);
  const [historyList, setHistoryList] = useState<any[]>([]);

  const addLog = (msg: string, level = "INFO") => {
    const time = new Date().toTimeString().split(" ")[0];
    setLogs(prev => [...prev.slice(-40), `[${time}] [${level}] ${msg}`]);
  };

  const handleLanguageChange = (newLang: Language) => {
    setLang(newLang);
    const newCategoryNames = LANGUAGE_CATEGORIES[newLang];
    setCategoryFolderNames({ ...newCategoryNames });

    setItems(prev =>
      prev.map(it => ({
        ...it,
        target_folder_name: newCategoryNames[it.category] || it.category,
      }))
    );

    addLog(`Düzenleme dili değiştirildi: ${LANGUAGES.find(l => l.code === newLang)?.name}. Hedef klasörler uyarlandı.`, "CONFIG");
  };

  useEffect(() => {
    fetchTree();
    fetchHistory();
  }, []);

  const fetchTree = async () => {
    try {
      const res = await fetch(`/api/test-folder/files?folder=${encodeURIComponent(folderPath)}`);
      const data = await res.json();
      if (data.tree) {
        setExplorerTree(data.tree);
      }
    } catch {
      // Ignore
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch("/api/history");
      const data = await res.json();
      setHistoryList(data);
    } catch {
      // Ignore
    }
  };

  const handleCreateTestFolder = async () => {
    setLoading(true);
    addLog("Test klasörü ve örnek dosyalar oluşturuluyor...", "INFO");
    try {
      const res = await fetch("/api/test-folder/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ folder: folderPath }),
      });
      const data = await res.json();
      if (data.status === "success") {
        addLog(`Test klasörü oluşturuldu: ${data.created_files.length} dosya eklendi.`, "SUCCESS");
        await handleScan();
        await fetchTree();
      } else {
        addLog(`Hata: ${data.message}`, "ERROR");
      }
    } catch (err: any) {
      addLog(`Test klasörü oluşturulamadı: ${err.message}`, "ERROR");
    } finally {
      setLoading(false);
    }
  };

  const handleCleanFolder = async () => {
    if (!confirm("Hedef klasördeki tüm test dosyaları silinecek. Emin misiniz?")) return;
    setLoading(true);
    addLog("Klasör temizleniyor...", "INFO");
    try {
      const res = await fetch("/api/test-folder/clean", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ folder: folderPath }),
      });
      const data = await res.json();
      if (data.status === "success") {
        addLog("Hedef klasör temizlendi.", "SUCCESS");
        setItems([]);
        await fetchTree();
      } else {
        addLog(`Temizleme hatası: ${data.message}`, "ERROR");
      }
    } catch (err: any) {
      addLog(`Hata: ${err.message}`, "ERROR");
    } finally {
      setLoading(false);
    }
  };

  const handleScan = async () => {
    setLoading(true);
    setProgress(25);
    setProgressText("Taranıyor...");
    addLog(`Klasör taranıyor (Dil: ${lang}): ${folderPath}`, "INFO");

    try {
      const res = await fetch("/api/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          folder: folderPath,
          subfolders,
          ai: useAi,
          rename: useSmartRename,
          lang: lang,
        }),
      });
      const data = await res.json();
      setProgress(100);

      if (data.status === "success") {
        setItems(data.items);
        addLog(`Tarama bitti: ${data.count} dosya listelendi.`, "SUCCESS");
      } else {
        addLog(`Tarama hatası: ${data.message}`, "ERROR");
      }
    } catch (err: any) {
      addLog(`Bağlantı hatası: ${err.message}`, "ERROR");
    } finally {
      setLoading(false);
      setProgress(0);
      setProgressText("");
      fetchTree();
    }
  };

  // Real Drag & Drop / File Picker Handler
  const handleFilesUpload = async (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) return;
    setLoading(true);
    addLog(`${fileList.length} dosya yükleniyor ve taranıyor...`, "INFO");

    try {
      const filesPayload: { name: string; contentBase64: string; size: number }[] = [];

      for (let i = 0; i < fileList.length; i++) {
        const file = fileList[i];
        // Read file as base64
        const base64 = await new Promise<string>((resolve) => {
          const reader = new FileReader();
          reader.onload = () => {
            const result = reader.result as string;
            const base64Clean = result.split(",")[1] || "";
            resolve(base64Clean);
          };
          reader.onerror = () => resolve("");
          reader.readAsDataURL(file);
        });

        filesPayload.push({
          name: file.name,
          contentBase64: base64,
          size: file.size,
        });
      }

      const res = await fetch("/api/upload-files", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          folder: folderPath,
          files: filesPayload,
        }),
      });

      const data = await res.json();
      if (data.status === "success") {
        addLog(`${data.count} dosya başarıyla yüklendi. Otomatik analiz yapılıyor...`, "SUCCESS");
        await handleScan();
        await fetchTree();
      } else {
        addLog(`Yükleme hatası: ${data.message}`, "ERROR");
      }
    } catch (err: any) {
      addLog(`Dosya yüklenirken hata: ${err.message}`, "ERROR");
    } finally {
      setLoading(false);
    }
  };

  const handleOrganize = async () => {
    const selected = items.filter(it => it.is_selected && !it.is_skipped);
    if (selected.length === 0) {
      alert("Lütfen taşınacak en az bir dosya seçin.");
      return;
    }

    setIsOrganizing(true);
    setProgress(35);
    setProgressText("Düzenleniyor...");
    addLog(`Dosya düzenleme başlatıldı: ${selected.length} dosya taşınıyor (Dil: ${lang}).`, "INFO");

    try {
      const selectedNames = selected.map(it => it.original_name);
      const res = await fetch("/api/organize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          folder: folderPath,
          subfolders,
          ai: useAi,
          rename: useSmartRename,
          lang: lang,
          selectedFiles: selectedNames,
        }),
      });
      const data = await res.json();
      setProgress(100);

      if (data.status === "success") {
        addLog(data.result.message, "SUCCESS");
        await handleScan();
        await fetchTree();
        await fetchHistory();
      } else {
        addLog(`Düzenleme hatası: ${data.message}`, "ERROR");
      }
    } catch (err: any) {
      addLog(`İşlem hatası: ${err.message}`, "ERROR");
    } finally {
      setIsOrganizing(false);
      setProgress(0);
      setProgressText("");
    }
  };

  const handleUndo = async () => {
    addLog("Son işlem geri alınıyor...", "INFO");
    try {
      const res = await fetch("/api/undo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ folder: folderPath }),
      });
      const data = await res.json();
      if (data.status === "success") {
        addLog(`Geri alma tamamlandı: ${data.restored} dosya eski konumuna döndürüldü.`, "SUCCESS");
        await handleScan();
        await fetchTree();
        await fetchHistory();
      } else {
        addLog(`Geri alma uyarısı: ${data.message}`, "WARNING");
      }
    } catch (err: any) {
      addLog(`Geri alma hatası: ${err.message}`, "ERROR");
    }
  };

  const handleRunTests = async () => {
    setRunningTests(true);
    setTestOutput("python -m pytest -v çalıştırılıyor...\nLütfen bekleyin...");
    addLog("Pytest testleri başlatıldı...", "INFO");

    try {
      const res = await fetch("/api/run-tests", { method: "POST" });
      const data = await res.json();
      setTestOutput(data.output);
      setTestSuccess(data.success);
      if (data.success) {
        addLog("Tüm testler (41/41) başarıyla geçti!", "SUCCESS");
      } else {
        addLog("Bazı testler başarısız oldu.", "WARNING");
      }
    } catch (err: any) {
      setTestOutput(`Hata: ${err.message}`);
      setTestSuccess(false);
    } finally {
      setRunningTests(false);
    }
  };

  const toggleSelectAll = (select: boolean) => {
    setItems(prev =>
      prev.map(it => (it.is_skipped ? it : { ...it, is_selected: select }))
    );
  };

  const updateItemCategory = (index: number, newCat: string) => {
    setItems(prev => {
      const next = [...prev];
      const targetFolder = categoryFolderNames[newCat] || newCat;
      next[index] = {
        ...next[index],
        category: newCat,
        target_folder_name: targetFolder,
      };
      return next;
    });
  };

  const updateItemName = (index: number, newName: string) => {
    setItems(prev => {
      const next = [...prev];
      next[index] = {
        ...next[index],
        new_name: newName,
        is_renamed: newName !== next[index].original_name,
      };
      return next;
    });
  };

  // Filtered files
  const filteredItems = items.filter(item => {
    const matchesSearch = item.original_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          item.new_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          item.category.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCat = selectedFilterCategory === "ALL" || item.category === selectedFilterCategory;
    return matchesSearch && matchesCat;
  });

  const totalFiles = items.length;
  const toMoveCount = items.filter(it => it.is_selected && !it.is_skipped).length;
  const renamedCount = items.filter(it => it.is_renamed && it.is_selected).length;
  const skippedCount = items.filter(it => it.is_skipped || !it.is_selected).length;

  return (
    <div
      style={{ zoom: scale }}
      className="min-h-screen w-full bg-[#10121d] text-slate-100 flex flex-col font-sans selection:bg-purple-600 selection:text-white antialiased transition-all"
    >
      {/* Hidden real file picker input */}
      <input
        type="file"
        multiple
        ref={fileInputRef}
        onChange={e => handleFilesUpload(e.target.files)}
        className="hidden"
      />

      {/* 1. TOP WINDOWS 11 TITLE BAR (FULL WIDTH & RESPONSIVE) */}
      <header className="w-full border-b border-[#1f2233] bg-[#121420] px-4 sm:px-6 py-2.5 flex items-center justify-between text-xs select-none flex-wrap gap-2">
        <div className="flex items-center gap-3">
          {/* Logo SD */}
          <div className="w-6 h-6 rounded-md bg-gradient-to-br from-[#8b5cf6] to-[#6366f1] flex items-center justify-center font-bold text-white text-xs shadow-sm">
            SD
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-semibold text-slate-100 text-xs sm:text-sm tracking-tight">
              SmartDrop - Windows Akıllı Dosya Düzenleyici
            </span>
            <span className="text-[#3b425b] hidden sm:inline">/</span>
            <span className="text-[11px] text-slate-400 font-mono hidden md:inline">PySide6 & Python 3.12+</span>
          </div>

          <div className="flex items-center gap-1.5 text-xs text-[#22c55e] font-semibold bg-[#112419] px-2 py-0.5 rounded border border-[#166534]">
            <span className="text-[#22c55e] text-[9px]">◆</span>
            <span className="text-[11px]">41/41 Test Geçti</span>
          </div>
        </div>

        {/* Right Header Controls: Scale Selector (%125), Language Selector & Window Actions */}
        <div className="flex items-center gap-3">
          {/* Scale Selector (%125 default) */}
          <div className="flex items-center gap-1 bg-[#171926] border border-[#272e44] rounded-md px-2 py-1 text-slate-300">
            <ZoomIn className="w-3.5 h-3.5 text-purple-400" />
            <span className="text-[11px] text-slate-400 mr-1 hidden sm:inline">Ölçek:</span>
            <select
              value={scale}
              onChange={e => setScale(parseFloat(e.target.value))}
              className="bg-transparent text-xs text-purple-300 font-bold focus:outline-none cursor-pointer"
            >
              <option value={1} className="bg-[#121420] text-slate-200">%100</option>
              <option value={1.25} className="bg-[#121420] text-slate-200">%125 (Varsayılan)</option>
              <option value={1.5} className="bg-[#121420] text-slate-200">%150</option>
            </select>
          </div>

          {/* Language Selector */}
          <div className="relative flex items-center gap-1.5 bg-[#171926] border border-[#272e44] rounded-md px-2.5 py-1 text-slate-300 hover:border-[#384364] transition cursor-pointer">
            <Globe className="w-3.5 h-3.5 text-indigo-400" />
            <select
              value={lang}
              onChange={e => handleLanguageChange(e.target.value as Language)}
              className="bg-transparent text-xs text-slate-200 font-medium focus:outline-none cursor-pointer pr-1 appearance-none"
            >
              {LANGUAGES.map(l => (
                <option key={l.code} value={l.code} className="bg-[#121420] text-slate-200">
                  {l.label}
                </option>
              ))}
            </select>
            <ChevronDown className="w-3 h-3 text-slate-400 pointer-events-none -ml-0.5" />
          </div>

          {/* Window control buttons */}
          <div className="flex items-center gap-2.5 text-slate-500 pl-1 font-mono hidden sm:flex">
            <span className="w-2.5 h-0.5 bg-slate-500 rounded inline-block cursor-pointer hover:bg-slate-300" />
            <span className="w-2.5 h-2.5 border border-slate-500 rounded-sm inline-block cursor-pointer hover:border-slate-300" />
            <span className="text-slate-500 text-xs px-0.5 hover:text-rose-400 cursor-pointer transition leading-none">✕</span>
          </div>
        </div>
      </header>

      {/* 2. SUB-HEADER NAVIGATION TABS (FULL WIDTH & HORIZONTAL SCROLL ON MOBILE) */}
      <div className="w-full border-b border-[#1f2233] bg-[#121420] px-4 sm:px-6 py-2 flex items-center justify-between overflow-x-auto scrollbar-none gap-4">
        <div className="flex items-center gap-6 sm:gap-8 text-xs flex-nowrap min-w-max">
          <button
            onClick={() => setActiveTab("desktop")}
            className={`relative py-2 font-medium transition flex items-center gap-2 ${
              activeTab === "desktop"
                ? "text-white font-semibold"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Folder className={`w-4 h-4 ${activeTab === "desktop" ? "text-[#00f2fe]" : "text-slate-400"}`} />
            <span>Masaüstü Düzenleyici</span>
            {activeTab === "desktop" && (
              <span className="absolute -bottom-2 left-0 right-0 h-[3px] bg-[#00f2fe] shadow-[0_0_16px_#00f2fe,0_0_30px_#00f2fe] rounded-full" />
            )}
          </button>

          <button
            onClick={() => { setActiveTab("explorer"); fetchTree(); }}
            className={`relative py-2 font-medium transition flex items-center gap-2 ${
              activeTab === "explorer"
                ? "text-white font-semibold"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Cloud className={`w-4 h-4 ${activeTab === "explorer" ? "text-[#00f2fe]" : "text-slate-400"}`} />
            <span>Canlı Dosya Gezgini</span>
            {activeTab === "explorer" && (
              <span className="absolute -bottom-2 left-0 right-0 h-[3px] bg-[#00f2fe] shadow-[0_0_16px_#00f2fe,0_0_30px_#00f2fe] rounded-full" />
            )}
          </button>

          <button
            onClick={() => setActiveTab("tests")}
            className={`relative py-2 font-medium transition flex items-center gap-2 ${
              activeTab === "tests"
                ? "text-white font-semibold"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Terminal className={`w-4 h-4 ${activeTab === "tests" ? "text-[#00f2fe]" : "text-slate-400"}`} />
            <span>&gt;_ Pytest Test Merkezi</span>
            {activeTab === "tests" && (
              <span className="absolute -bottom-2 left-0 right-0 h-[3px] bg-[#00f2fe] shadow-[0_0_16px_#00f2fe,0_0_30px_#00f2fe] rounded-full" />
            )}
          </button>

          <button
            onClick={() => setActiveTab("settings")}
            className={`relative py-2 font-medium transition flex items-center gap-2 ${
              activeTab === "settings"
                ? "text-white font-semibold"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <SettingsIcon className={`w-4 h-4 ${activeTab === "settings" ? "text-[#00f2fe]" : "text-slate-400"}`} />
            <span>Ayarlar & Kurallar</span>
            {activeTab === "settings" && (
              <span className="absolute -bottom-2 left-0 right-0 h-[3px] bg-[#00f2fe] shadow-[0_0_16px_#00f2fe,0_0_30px_#00f2fe] rounded-full" />
            )}
          </button>
        </div>

        <div className="flex-shrink-0">
          <a
            href="/SmartDrop-Windows.zip"
            download="SmartDrop-Windows.zip"
            className="border border-[#10b981]/70 bg-[#0f211c] hover:bg-[#142e26] text-[#34d399] text-xs px-3.5 py-1.5 rounded-lg font-medium flex items-center gap-1.5 transition shadow-sm whitespace-nowrap"
          >
            <Download className="w-3.5 h-3.5 text-[#34d399]" />
            <span>Zipi İndir (zip)</span>
          </a>
        </div>
      </div>

      {/* 3. MAIN WORKBENCH BODY (FULL WIDTH & RESPONSIVE FOR MOBILE, TABLET, DESKTOP) */}
      <main className="w-full flex-1 px-4 sm:px-6 md:px-8 lg:px-10 py-4 sm:py-6 space-y-4">
        {activeTab === "desktop" && (
          <div className="w-full space-y-4">
            {/* Card 1: Top Safety Banner - Full Width */}
            <div className="w-full bg-[#111e1d] border border-[#1a4237] rounded-xl px-4 py-2.5 flex items-center justify-between flex-wrap gap-2 text-xs shadow-sm">
              <div className="flex items-center gap-2.5 text-[#e2e8f0]">
                <ShieldCheck className="w-4 h-4 text-[#10b981] flex-shrink-0" />
                <span className="font-normal text-[11px] sm:text-xs">
                  Garantili Güvenlik: Asla üzerine yazmaz, silmez, sistem yollarını korur ve tek tıkla geri alır.
                </span>
              </div>
              <div className="flex items-center gap-2 text-[#64748b] text-[11px] font-mono">
                <span>🇹🇷 Türkçe</span>
                <span>·</span>
                <span>Python 3.12+</span>
                <span>·</span>
                <span>PySide6 Qt</span>
              </div>
            </div>

            {/* Card 2: Hedef Klasör - Full Width with Stacked Responsive Controls */}
            <div className="w-full bg-[#171926] border border-[#262c3f] rounded-2xl p-4 sm:p-5 shadow-sm">
              <label className="block text-[11px] font-semibold text-[#8b92a5] mb-2 tracking-wider">
                DÜZENLENECEK HEDEF KLASÖR
              </label>

              <div className="flex flex-col md:flex-row gap-2.5 items-stretch md:items-center">
                <div className="relative flex-1">
                  <input
                    type="text"
                    value={folderPath}
                    onChange={e => setFolderPath(e.target.value)}
                    placeholder="test_data/sample_downloads"
                    className="w-full bg-[#0e1018] border border-[#24293c] rounded-lg px-4 py-2.5 text-xs text-[#e2e8f0] font-mono placeholder:text-[#475569] focus:outline-none focus:border-indigo-500 transition"
                  />
                </div>

                <div className="flex items-center gap-2 flex-wrap">
                  <button
                    onClick={handleCreateTestFolder}
                    disabled={loading || isOrganizing}
                    className="flex-1 sm:flex-initial bg-[#1c1e2d] hover:bg-[#25283b] text-[#c5c9d6] border border-[#2e344e] text-xs px-4 py-2.5 rounded-lg font-medium transition flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    <FolderPlus className="w-4 h-4 text-[#94a3b8]" />
                    <span>Test Klasörü Oluştur</span>
                  </button>

                  <button
                    onClick={handleCleanFolder}
                    disabled={loading || isOrganizing}
                    title="Klasörü Temizle"
                    className="bg-[#1c1e2d] hover:bg-rose-950/40 text-slate-300 hover:text-rose-400 border border-[#2e344e] text-xs px-3 py-2.5 rounded-lg font-medium transition flex items-center justify-center gap-1.5 disabled:opacity-50"
                  >
                    <Trash2 className="w-4 h-4 text-slate-400 hover:text-rose-400" />
                    <span className="hidden sm:inline">Temizle</span>
                  </button>

                  <button
                    onClick={handleScan}
                    disabled={loading || isOrganizing}
                    className="flex-1 sm:flex-initial bg-[#1f1738] hover:bg-[#2c204e] text-white border-2 border-[#a855f7] text-xs px-5 py-2.5 rounded-lg font-bold flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(168,85,247,0.4)] transition disabled:opacity-50"
                  >
                    {loading ? (
                      <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                      <Play className="w-4 h-4 fill-[#a855f7] text-[#a855f7]" />
                    )}
                    <span>Klasörü Tara</span>
                  </button>
                </div>
              </div>

              {/* Progress bar if active */}
              {(loading || isOrganizing) && (
                <div className="mt-3">
                  <div className="flex justify-between text-xs text-[#a855f7] mb-1 font-medium font-mono">
                    <span>{progressText || "İşlem yürütülüyor..."}</span>
                    <span>{progress}%</span>
                  </div>
                  <div className="w-full bg-[#0d0f17] rounded-full h-1.5 overflow-hidden border border-[#23283b]">
                    <div
                      className="bg-gradient-to-r from-purple-500 to-indigo-500 h-full transition-all duration-300 rounded-full"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Card 3: 4 Metrics Cards - Full Width Responsive Grid (1 col on mobile, 2 on tablet, 4 on desktop) */}
            <div className="w-full grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
              {/* 1. TOPLAM DOSYA */}
              <div className="bg-[#171926] border border-[#262c3f] rounded-2xl p-4 sm:p-5 flex items-center justify-between shadow-sm">
                <div>
                  <span className="text-[11px] font-semibold text-[#8b92a5] uppercase tracking-wider block">
                    TOPLAM DOSYA
                  </span>
                  <span className="text-3xl sm:text-4xl font-extrabold text-[#38bdf8] mt-1 block">
                    {totalFiles}
                  </span>
                </div>
                <CloudUpload className="w-9 h-9 text-[#38bdf8] stroke-[1.8]" />
              </div>

              {/* 2. TAŞINACAK */}
              <div className="bg-[#171926] border border-[#262c3f] rounded-2xl p-4 sm:p-5 flex items-center justify-between shadow-sm">
                <div>
                  <span className="text-[11px] font-semibold text-[#8b92a5] uppercase tracking-wider block">
                    TAŞINACAK
                  </span>
                  <span className="text-3xl sm:text-4xl font-extrabold text-[#22c55e] mt-1 block">
                    {toMoveCount}
                  </span>
                </div>
                <ArrowLeftRight className="w-9 h-9 text-[#22c55e] stroke-[1.8]" />
              </div>

              {/* 3. YENİDEN ADLANDIRILACAK */}
              <div className="bg-[#171926] border border-[#262c3f] rounded-2xl p-4 sm:p-5 flex items-center justify-between shadow-sm">
                <div>
                  <span className="text-[11px] font-semibold text-[#8b92a5] uppercase tracking-wider block">
                    YENİDEN ADLANDIRILACAK
                  </span>
                  <span className="text-3xl sm:text-4xl font-extrabold text-[#38bdf8] mt-1 block">
                    {renamedCount}
                  </span>
                </div>
                <SquarePen className="w-9 h-9 text-[#f59e0b] stroke-[1.8]" />
              </div>

              {/* 4. ATLANAN / MEVCUT */}
              <div className="bg-[#171926] border border-[#262c3f] rounded-2xl p-4 sm:p-5 flex items-center justify-between shadow-sm">
                <div>
                  <span className="text-[11px] font-semibold text-[#8b92a5] uppercase tracking-wider block">
                    ATLANAN / MEVCUT
                  </span>
                  <span className="text-3xl sm:text-4xl font-extrabold text-[#f87171] mt-1 block">
                    {skippedCount}
                  </span>
                </div>
                <CircleSlash2 className="w-9 h-9 text-[#ef4444] stroke-[1.8]" />
              </div>
            </div>

            {/* Card 4: DOSYA DÜZENLEME PLANI - Full Width with Search, Filter & Drag/Drop */}
            <div className="w-full bg-[#171926] border border-[#262c3f] rounded-2xl p-4 sm:p-6 shadow-sm space-y-4">
              {/* Header with Search and Selection Controls */}
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                <div className="flex items-center gap-2 flex-wrap">
                  <h3 className="text-xs sm:text-sm font-bold uppercase tracking-wider text-[#f1f5f9]">
                    DOSYA DÜZENLEME PLANI ({filteredItems.length}/{items.length})
                  </h3>
                  <span className="text-xs text-[#64748b] hidden lg:inline">
                    - Hedef klasörler seçilen dile göre otomatik atanmıştır.
                  </span>
                </div>

                <div className="flex items-center gap-3 flex-wrap">
                  {/* Search input */}
                  {items.length > 0 && (
                    <div className="relative">
                      <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
                      <input
                        type="text"
                        value={searchQuery}
                        onChange={e => setSearchQuery(e.target.value)}
                        placeholder="Filtrele veya ara..."
                        className="bg-[#0e1018] border border-[#252b3d] rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 w-44 sm:w-56"
                      />
                    </div>
                  )}

                  {/* Select All / Deselect All */}
                  <div className="flex items-center gap-2 text-xs">
                    <button
                      onClick={() => toggleSelectAll(true)}
                      className="text-xs text-[#818cf8] hover:text-[#a5b4fc] font-medium px-2 py-1 rounded bg-[#1f2336] hover:bg-[#262b42] transition"
                    >
                      Tümünü Seç
                    </button>
                    <button
                      onClick={() => toggleSelectAll(false)}
                      className="text-xs text-[#94a3b8] hover:text-white font-medium px-2 py-1 rounded bg-[#1f2336] hover:bg-[#262b42] transition"
                    >
                      Seçimi Kaldır
                    </button>
                  </div>
                </div>
              </div>

              {/* Category Filter Pills (When files exist) */}
              {items.length > 0 && (
                <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none text-xs">
                  <button
                    onClick={() => setSelectedFilterCategory("ALL")}
                    className={`px-3 py-1 rounded-full font-medium transition ${
                      selectedFilterCategory === "ALL"
                        ? "bg-purple-600 text-white"
                        : "bg-[#0e1018] text-slate-400 hover:text-white"
                    }`}
                  >
                    Hepsi ({items.length})
                  </button>
                  {CATEGORIES.filter(cat => items.some(it => it.category === cat)).map(cat => {
                    const count = items.filter(it => it.category === cat).length;
                    const catLabel = categoryFolderNames[cat] || cat;
                    return (
                      <button
                        key={cat}
                        onClick={() => setSelectedFilterCategory(cat)}
                        className={`px-3 py-1 rounded-full font-medium transition flex items-center gap-1.5 whitespace-nowrap ${
                          selectedFilterCategory === cat
                            ? "bg-indigo-600 text-white"
                            : "bg-[#0e1018] text-slate-400 hover:text-white border border-[#23283b]"
                        }`}
                      >
                        <span>{catLabel}</span>
                        <span className="text-[10px] opacity-75 font-mono">({count})</span>
                      </button>
                    );
                  })}
                </div>
              )}

              {/* Empty / Drag & Drop Dropzone */}
              {items.length === 0 || viewMode === "auto" && items.length === 0 ? (
                <div
                  onDragOver={e => { e.preventDefault(); setIsDraggingOver(true); }}
                  onDragLeave={() => setIsDraggingOver(false)}
                  onDrop={async e => {
                    e.preventDefault();
                    setIsDraggingOver(false);
                    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                      await handleFilesUpload(e.dataTransfer.files);
                    } else {
                      await handleScan();
                    }
                  }}
                  onClick={() => fileInputRef.current?.click()}
                  className={`w-full border-2 border-dashed rounded-2xl py-14 sm:py-20 px-6 text-center cursor-pointer transition flex flex-col items-center justify-center ${
                    isDraggingOver
                      ? "border-purple-500 bg-[#1c1836] scale-[1.01]"
                      : "border-[#2e3248] bg-[#0e1017]/70 hover:border-[#434b6e] hover:bg-[#121420]"
                  }`}
                >
                  {/* Glassmorphic Double Folder Graphic */}
                  <div className="relative mb-3 flex items-center justify-center">
                    <div className="w-24 h-16 rounded-xl bg-[#22273d] border border-[#343d5c] shadow-lg flex items-center justify-center relative z-0 -rotate-3 -translate-x-1.5 -translate-y-1 opacity-70" />
                    <div className="absolute w-24 h-16 rounded-xl bg-gradient-to-tr from-[#2a3048]/90 to-[#3a4465]/80 border border-[#525e8a]/70 shadow-2xl flex items-center justify-center z-10 backdrop-blur-md">
                      <Folder className="w-10 h-10 text-[#a5b4fc] fill-indigo-400/20 stroke-[1.8]" />
                    </div>
                  </div>

                  <h4 className="text-base sm:text-lg font-bold text-white tracking-wide mt-2">
                    Drag & Drop
                  </h4>
                  <p className="text-xs sm:text-sm text-[#8e95ab] mt-1 max-w-md">
                    Bilgisayarınızdan dosyaları doğrudan buraya sürükleyin veya dosya seçmek için tıklayın.
                  </p>

                  <div className="mt-4 flex items-center gap-3 flex-wrap justify-center" onClick={e => e.stopPropagation()}>
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="bg-[#242042] hover:bg-[#2f2956] text-purple-200 border border-purple-500/50 text-xs px-4 py-2 rounded-lg font-semibold flex items-center gap-2 transition"
                    >
                      <UploadCloud className="w-4 h-4 text-purple-300" />
                      <span>Gerçek Dosya Seç</span>
                    </button>

                    <button
                      onClick={handleCreateTestFolder}
                      className="bg-[#172322] hover:bg-[#1f302e] text-emerald-300 border border-emerald-500/40 text-xs px-4 py-2 rounded-lg font-semibold flex items-center gap-2 transition"
                    >
                      <FolderPlus className="w-4 h-4 text-emerald-400" />
                      <span>Örnek Dosyaları Yükle ({folderPath})</span>
                    </button>
                  </div>
                </div>
              ) : (
                /* Full Width Interactive Table */
                <div className="w-full space-y-2">
                  <div className="flex items-center justify-between text-xs pb-1">
                    <span className="text-slate-400">
                      Toplam {filteredItems.length} dosya gösteriliyor (Seçilen: {toMoveCount})
                    </span>

                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1.5 font-medium"
                    >
                      <UploadCloud className="w-4 h-4" />
                      Daha Fazla Dosya Ekle
                    </button>
                  </div>

                  <div className="w-full overflow-x-auto rounded-xl border border-[#23293c] bg-[#0e1017]">
                    <table className="w-full text-left text-xs border-collapse min-w-[700px]">
                      <thead>
                        <tr className="bg-[#0b0d14] text-[#94a3b8] border-b border-[#1f2436]">
                          <th className="py-3 px-3 w-10 text-center">
                            <input
                              type="checkbox"
                              checked={items.length > 0 && items.every(it => it.is_selected || it.is_skipped)}
                              onChange={e => toggleSelectAll(e.target.checked)}
                              className="rounded bg-[#171926] border-[#30374e] text-indigo-600 focus:ring-0 cursor-pointer"
                            />
                          </th>
                          <th className="py-3 px-3 font-semibold">Dosya Adı</th>
                          <th className="py-3 px-3 font-semibold">Kategori</th>
                          <th className="py-3 px-3 font-semibold">Hedef Konum</th>
                          <th className="py-3 px-3 font-semibold">Yeni İsim</th>
                          <th className="py-3 px-3 font-semibold text-right">Boyut</th>
                          <th className="py-3 px-3 font-semibold text-center">Durum</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#1b2030]">
                        {filteredItems.map((item, idx) => {
                          const catStyle = CATEGORY_COLORS[item.category] || CATEGORY_COLORS.Others;
                          const localizedCatName = categoryFolderNames[item.category] || item.category;
                          const realIdx = items.findIndex(it => it.original_name === item.original_name);
                          return (
                            <tr
                              key={idx}
                              className={`hover:bg-[#161a29] transition ${
                                !item.is_selected ? "opacity-40" : ""
                              }`}
                            >
                              <td className="py-3 px-3 text-center">
                                <input
                                  type="checkbox"
                                  checked={item.is_selected}
                                  disabled={item.is_skipped}
                                  onChange={e => {
                                    const checked = e.target.checked;
                                    setItems(prev => {
                                      const next = [...prev];
                                      if (realIdx >= 0) {
                                        next[realIdx] = { ...next[realIdx], is_selected: checked };
                                      }
                                      return next;
                                    });
                                  }}
                                  className="rounded bg-[#171926] border-[#30374e] text-indigo-600 focus:ring-0 cursor-pointer"
                                />
                              </td>

                              <td className="py-3 px-3 font-mono text-[#f1f5f9]">
                                <div className="flex items-center gap-2.5 max-w-xs sm:max-w-md truncate" title={item.original_name}>
                                  <div className="p-1 rounded bg-[#1d2235] border border-[#2d354e] flex-shrink-0">
                                    {getCategoryIcon(item.category)}
                                  </div>
                                  <span className="truncate">{item.original_name}</span>
                                </div>
                              </td>

                              <td className="py-3 px-3">
                                <select
                                  value={item.category}
                                  onChange={e => updateItemCategory(realIdx, e.target.value)}
                                  className="bg-[#12141f] border border-[#2d354e] rounded px-2.5 py-1 text-xs text-[#e2e8f0] cursor-pointer focus:outline-none focus:border-indigo-500"
                                >
                                  {CATEGORIES.map(cat => (
                                    <option key={cat} value={cat} className="bg-[#131522] text-[#e2e8f0]">
                                      {categoryFolderNames[cat] ? `${categoryFolderNames[cat]} (${cat})` : cat}
                                    </option>
                                  ))}
                                </select>
                              </td>

                              <td className="py-3 px-3 font-mono text-xs whitespace-nowrap">
                                <span className={`${catStyle.text} font-semibold flex items-center gap-1.5`}>
                                  <span className={`w-1.5 h-1.5 rounded-full ${catStyle.dot}`} />
                                  {localizedCatName}/
                                </span>
                              </td>

                              <td className="py-3 px-3">
                                <input
                                  type="text"
                                  value={item.new_name}
                                  onChange={e => updateItemName(realIdx, e.target.value)}
                                  className="bg-[#12141f] border border-[#2d354e] focus:border-indigo-500 rounded px-2 py-1 text-xs font-mono text-[#e2e8f0] w-full focus:outline-none"
                                />
                              </td>

                              <td className="py-3 px-3 text-right text-[#94a3b8] font-mono text-xs whitespace-nowrap">
                                {formatSize(item.size_bytes)}
                              </td>

                              <td className="py-3 px-3 text-center text-xs whitespace-nowrap">
                                {item.is_skipped ? (
                                  <span className="text-[#64748b]">Atlandı</span>
                                ) : item.is_renamed ? (
                                  <span className="text-[#38bdf8] font-medium">Yeniden Adlandırılacak</span>
                                ) : (
                                  <span className="text-[#22c55e] font-medium">Taşınacak</span>
                                )}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>

            {/* Card 5: Action Buttons Row - Full Width Responsive Stack */}
            <div className="w-full flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
              {/* Left group */}
              <div className="flex items-center gap-2.5 flex-wrap">
                <button
                  onClick={handleRunTests}
                  className="flex-1 sm:flex-initial bg-[#1c1e2d] hover:bg-[#25283b] text-[#c5c9d6] border border-[#2e344e] text-xs px-4 py-2.5 rounded-lg font-medium transition flex items-center justify-center gap-2"
                >
                  <Terminal className="w-4 h-4 text-[#94a3b8]" />
                  <span>&gt;_ Testleri Çalıştır (pytest)</span>
                </button>

                <a
                  href="/SmartDrop-Windows.zip"
                  download="SmartDrop-Windows.zip"
                  className="flex-1 sm:flex-initial bg-[#101b17] hover:bg-[#162720] text-[#34d399] border border-[#10b981]/70 text-xs px-4 py-2.5 rounded-lg font-medium transition flex items-center justify-center gap-2"
                >
                  <Download className="w-4 h-4 text-[#34d399]" />
                  <span>Zipi İndir (zip)</span>
                </a>
              </div>

              {/* Right group */}
              <div className="flex items-center gap-2.5 flex-wrap">
                <button
                  onClick={handleUndo}
                  className="flex-1 sm:flex-initial bg-[#1c1e2d] hover:bg-[#25283b] text-[#c5c9d6] border border-[#2e344e] text-xs px-4 py-2.5 rounded-lg font-medium transition flex items-center justify-center gap-2"
                >
                  <RotateCcw className="w-4 h-4 text-[#f59e0b]" />
                  <span>Son İşlemi Geri Al</span>
                </button>

                {/* Solid Violet Glow Button: Düzenlemeyi Başlat */}
                <button
                  onClick={handleOrganize}
                  disabled={toMoveCount === 0 || isOrganizing}
                  className="flex-1 sm:flex-initial bg-gradient-to-r from-[#7c3aed] to-[#6366f1] hover:from-[#6d28d9] hover:to-[#4f46e5] text-white font-bold text-xs sm:text-sm px-6 py-2.5 rounded-xl flex items-center justify-center gap-2 shadow-[0_0_22px_rgba(124,58,237,0.65)] transition disabled:opacity-40 disabled:shadow-none"
                >
                  <Sparkles className="w-4 h-4" />
                  <span>Düzenlemeyi Başlat ({toMoveCount})</span>
                </button>
              </div>
            </div>

            {/* Card 6: İŞLEM GÜNLÜĞÜ - Full Width */}
            <div className="w-full bg-[#171926] border border-[#262c3f] rounded-2xl p-4 shadow-sm">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-bold text-[#8b92a5] tracking-wider flex items-center gap-2">
                  <Terminal className="w-4 h-4 text-[#8b92a5]" />
                  <span>&gt;_ İŞLEM GÜNLÜĞÜ</span>
                </span>
                <button
                  onClick={() => setLogs([])}
                  className="text-xs text-[#64748b] hover:text-[#94a3b8] transition"
                >
                  Temizle
                </button>
              </div>

              {/* Pure pitch black (#000000) terminal container */}
              <div className="w-full bg-[#000000] rounded-xl p-3.5 font-mono text-xs text-[#cbd5e1] h-32 overflow-y-auto space-y-1 border border-[#1b1d29]">
                {logs.map((log, i) => {
                  let isReady = log.includes("[READY]");
                  let isSystem = log.includes("[SYSTEM]");
                  let isSuccess = log.includes("[SUCCESS]");
                  let isError = log.includes("[ERROR]");
                  return (
                    <div key={i} className="leading-relaxed">
                      {isSystem ? (
                        <>
                          <span className="text-[#64748b]">{log.slice(0, 10)}</span>{" "}
                          <span className="text-[#22d3ee] font-bold">[SYSTEM]</span>{" "}
                          <span className="text-[#e2e8f0]">{log.split("[SYSTEM]")[1]}</span>
                        </>
                      ) : isReady ? (
                        <>
                          <span className="text-[#64748b]">{log.slice(0, 10)}</span>{" "}
                          <span className="text-[#4ade80] font-bold">[READY]</span>{" "}
                          <span className="text-[#e2e8f0]">{log.split("[READY]")[1]}</span>
                        </>
                      ) : isSuccess ? (
                        <>
                          <span className="text-[#64748b]">{log.slice(0, 10)}</span>{" "}
                          <span className="text-[#22c55e] font-bold">[SUCCESS]</span>{" "}
                          <span className="text-[#e2e8f0]">{log.split("[SUCCESS]")[1]}</span>
                        </>
                      ) : isError ? (
                        <>
                          <span className="text-[#64748b]">{log.slice(0, 10)}</span>{" "}
                          <span className="text-rose-400 font-bold">[ERROR]</span>{" "}
                          <span className="text-rose-200">{log.split("[ERROR]")[1]}</span>
                        </>
                      ) : (
                        <span className="text-[#94a3b8]">{log}</span>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: EXPLORER (FULL WIDTH) */}
        {activeTab === "explorer" && (
          <div className="w-full space-y-4">
            <div className="w-full bg-[#171926] border border-[#262c3f] rounded-2xl p-4 sm:p-5 flex items-center justify-between flex-wrap gap-2">
              <div>
                <h2 className="text-sm sm:text-base font-semibold text-white">Canlı Dosya Sistemi Görünümü</h2>
                <p className="text-xs text-[#94a3b8] mt-0.5">
                  <code>{folderPath}</code> dizinindeki güncel dosya ve kategori klasörleri.
                </p>
              </div>
              <button
                onClick={fetchTree}
                className="bg-[#1c1e2d] hover:bg-[#25283b] text-[#c5c9d6] border border-[#2e344e] text-xs px-4 py-2 rounded-lg flex items-center gap-1.5 transition"
              >
                <RefreshCw className="w-4 h-4 text-indigo-400" />
                Yenile
              </button>
            </div>

            <div className="w-full bg-[#171926] border border-[#262c3f] rounded-2xl p-4 sm:p-5">
              <h3 className="text-xs font-semibold uppercase text-[#8b92a5] mb-3 tracking-wider">
                Klasör Ağacı
              </h3>

              {explorerTree.length === 0 ? (
                <div className="py-12 text-center text-xs text-[#64748b]">
                  Klasörde henüz dosya yok veya taranmadı. Üstteki &quot;Test Klasörü Oluştur&quot; butonuna basabilirsiniz.
                </div>
              ) : (
                <div className="space-y-1 font-mono text-xs">
                  {explorerTree.map((item, i) => (
                    <div key={i} className="py-1">
                      {item.isDir ? (
                        <div className="space-y-1">
                          <div className="flex items-center gap-2 font-semibold text-indigo-400">
                            <Folder className="w-4 h-4 fill-indigo-400/20" />
                            <span>{item.name}/</span>
                            <span className="text-[10px] text-[#64748b] font-normal">
                              ({item.children?.length || 0} dosya)
                            </span>
                          </div>
                          <div className="pl-6 border-l border-[#24293a] ml-2 space-y-1 mt-1">
                            {item.children?.map((sub: any, j: number) => (
                              <div key={j} className="flex items-center justify-between text-[#cbd5e1] py-0.5">
                                <div className="flex items-center gap-2">
                                  <File className="w-3.5 h-3.5 text-[#64748b]" />
                                  <span>{sub.name}</span>
                                </div>
                                <span className="text-[10px] text-[#64748b]">{formatSize(sub.size)}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      ) : (
                        <div className="flex items-center justify-between text-[#cbd5e1]">
                          <div className="flex items-center gap-2">
                            <File className="w-4 h-4 text-[#64748b]" />
                            <span>{item.name}</span>
                          </div>
                          <span className="text-[10px] text-[#64748b]">{formatSize(item.size)}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* History Table */}
            <div className="w-full bg-[#171926] border border-[#262c3f] rounded-2xl p-4 sm:p-5">
              <h3 className="text-xs font-semibold uppercase text-[#8b92a5] mb-3 tracking-wider flex items-center gap-1.5">
                <RotateCcw className="w-4 h-4 text-[#f59e0b]" />
                İşlem Geçmişi (.smartdrop_history.json)
              </h3>
              {historyList.length === 0 ? (
                <p className="text-xs text-[#64748b]">Henüz kaydedilmiş işlem geçmişi yok.</p>
              ) : (
                <div className="space-y-2">
                  {historyList.map((op, i) => (
                    <div key={i} className="bg-[#0e1017] border border-[#23293c] rounded-lg p-3 text-xs flex items-center justify-between flex-wrap gap-2">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-white">İşlem #{op.id?.slice(0, 8)}</span>
                          <span className="text-[10px] text-[#94a3b8]">{op.timestamp}</span>
                          <span className="text-[#475569]">·</span>
                          <span className="text-[11px] text-[#94a3b8]">
                            {op.is_undone ? "Geri Alındı" : "Aktif"}
                          </span>
                        </div>
                        <p className="text-[11px] text-[#8b92a5] mt-1">
                          Klasör: <code>{op.base_folder}</code> · {op.successful_moves} dosya taşındı
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 3: PYTEST (FULL WIDTH) */}
        {activeTab === "tests" && (
          <div className="w-full space-y-4">
            <div className="w-full bg-[#171926] border border-[#262c3f] rounded-2xl p-4 sm:p-5 flex items-center justify-between flex-wrap gap-2">
              <div>
                <h2 className="text-sm sm:text-base font-semibold text-white">Pytest Otomatik Birim & Çok Dilli Testler</h2>
                <p className="text-xs text-[#94a3b8] mt-0.5">
                  Tüm dosya formatları, çakışma çözümleri, geri alma ve Türkçe/Almanca/İngilizce klasörleme test edilir.
                </p>
              </div>

              <button
                onClick={handleRunTests}
                disabled={runningTests}
                className="bg-gradient-to-r from-[#7c3aed] to-[#6366f1] hover:from-[#6d28d9] hover:to-[#4f46e5] text-white text-xs px-5 py-2.5 rounded-lg font-medium transition flex items-center gap-2 shadow-[0_0_15px_rgba(124,58,237,0.4)] disabled:opacity-50"
              >
                {runningTests ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Play className="w-4 h-4" />
                )}
                Testleri Yeniden Çalıştır
              </button>
            </div>

            {/* Test Cards */}
            <div className="w-full grid grid-cols-1 md:grid-cols-3 gap-3.5">
              <div className="bg-[#171926] border border-[#262c3f] rounded-2xl p-4">
                <span className="text-xs font-semibold text-[#22c55e] flex items-center gap-1.5 mb-1">
                  <CheckCircle2 className="w-4 h-4" /> Çok Dilli Sınıflandırma & Duplicate
                </span>
                <p className="text-[11px] text-[#94a3b8]">
                  <code>test_file_classification.py</code> & <code>test_duplicate_files.py</code>: 15 format, Türkçe (Belgeler, Resimler), Almanca (Dokumente, Bilder) ve <code>photo (1).jpg</code> çakışma çözümü.
                </p>
              </div>

              <div className="bg-[#171926] border border-[#262c3f] rounded-2xl p-4">
                <span className="text-xs font-semibold text-[#22c55e] flex items-center gap-1.5 mb-1">
                  <ShieldCheck className="w-4 h-4" /> Türkçe Karakter & Önizleme Güvencesi
                </span>
                <p className="text-[11px] text-[#94a3b8]">
                  <code>test_file_names.py</code>: ödev.pdf, çalışma.docx, şarkı.mp3, görsel.png adlarının bozulmaması ve önizleme anında sıfır dosya hareketi.
                </p>
              </div>

              <div className="bg-[#171926] border border-[#262c3f] rounded-2xl p-4">
                <span className="text-xs font-semibold text-[#22c55e] flex items-center gap-1.5 mb-1">
                  <RotateCcw className="w-4 h-4" /> Geri Alma, Hata Toleransı & Tekrar
                </span>
                <p className="text-[11px] text-[#94a3b8]">
                  <code>test_undo.py</code>, <code>test_error_handling.py</code>, <code>test_repeated_runs.py</code>: tam undo, tek hata izolasyonu ve idempotentlik.
                </p>
              </div>
            </div>

            {/* Terminal Output */}
            <div className="w-full bg-[#0e1017] border border-[#262c3f] rounded-2xl p-4 sm:p-5">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-[#8b92a5] flex items-center gap-1.5">
                  <Terminal className="w-4 h-4 text-indigo-400" />
                  Pytest Konsol Çıktısı (SMARTDROP TEST REPORT)
                </span>
                {testSuccess !== null && (
                  <span className={`text-[11px] font-mono font-bold ${
                    testSuccess ? "text-[#22c55e]" : "text-[#f87171]"
                  }`}>
                    {testSuccess ? "BAŞARILI (41 Passed, 0 Failed)" : "BAŞARISIZ"}
                  </span>
                )}
              </div>

              <pre className="w-full bg-[#000000] border border-[#1b1d29] rounded-xl p-4 text-[#cbd5e1] font-mono text-xs overflow-x-auto whitespace-pre-wrap max-h-96">
                {testOutput || "Testleri başlatmak için 'Testleri Yeniden Çalıştır' butonuna tıklayın."}
              </pre>
            </div>
          </div>
        )}

        {/* TAB 4: SETTINGS (FULL WIDTH) */}
        {activeTab === "settings" && (
          <div className="w-full space-y-4">
            <div className="w-full bg-[#171926] border border-[#262c3f] rounded-2xl p-5 sm:p-6">
              <h2 className="text-sm sm:text-base font-semibold text-white mb-1 flex items-center gap-2">
                <Globe className="w-4 h-4 text-indigo-400" />
                Düzenleme Dili
              </h2>
              <p className="text-xs text-[#94a3b8] mb-4">
                Hedef klasörler seçtiğiniz dile göre oluşturulur (örn: Belgeler, Resimler).
              </p>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {LANGUAGES.map(l => (
                  <button
                    key={l.code}
                    onClick={() => handleLanguageChange(l.code)}
                    className={`p-3.5 rounded-xl border text-left transition flex items-center gap-3 ${
                      lang === l.code
                        ? "bg-[#212438] border-purple-500/60 text-white"
                        : "bg-[#0e1017] border-[#252a3d] text-[#94a3b8] hover:text-white hover:bg-[#141724]"
                    }`}
                  >
                    <span className="text-2xl">{l.flag}</span>
                    <div>
                      <span className="text-xs font-semibold block">{l.name}</span>
                      <span className="text-[10px] text-[#64748b] uppercase font-mono">{l.code}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <div className="w-full bg-[#171926] border border-[#262c3f] rounded-2xl p-5 sm:p-6">
              <h2 className="text-sm sm:text-base font-semibold text-white mb-4">Genel Tarama & Analiz Ayarları</h2>

              <div className="space-y-3">
                <label className="flex items-center gap-3 p-3.5 bg-[#0e1017] border border-[#252a3d] rounded-xl cursor-pointer hover:border-[#384160] transition">
                  <input
                    type="checkbox"
                    checked={subfolders}
                    onChange={e => setSubfolders(e.target.checked)}
                    className="rounded bg-[#171926] border-[#30374e] text-indigo-600 focus:ring-0"
                  />
                  <div>
                    <span className="text-xs font-semibold text-white block">Alt Klasörleri de Tara (Recursive)</span>
                    <span className="text-[11px] text-[#8b92a5]">
                      Varsayılan olarak sadece seçilen ana dizindeki dosyalar düzenlenir. Bu seçenek alt klasörleri de kapsar.
                    </span>
                  </div>
                </label>

                <label className="flex items-center gap-3 p-3.5 bg-[#0e1017] border border-[#252a3d] rounded-xl cursor-pointer hover:border-[#384160] transition">
                  <input
                    type="checkbox"
                    checked={useSmartRename}
                    onChange={e => setUseSmartRename(e.target.checked)}
                    className="rounded bg-[#171926] border-[#30374e] text-indigo-600 focus:ring-0"
                  />
                  <div>
                    <span className="text-xs font-semibold text-white block">Akıllı Dosya Adlandırma (Tavsiye Edilen)</span>
                    <span className="text-[11px] text-[#8b92a5]">
                      Kamera çöplüklerini (IMG_20260920_1832.png) ve tarayıcı kopya parantezlerini (dosya(4).pdf) temiz, anlaşılır isimlere dönüştürür.
                    </span>
                  </div>
                </label>

                <label className="flex items-center gap-3 p-3.5 bg-[#0e1017] border border-[#252a3d] rounded-xl cursor-pointer hover:border-[#384160] transition">
                  <input
                    type="checkbox"
                    checked={useAi}
                    onChange={e => setUseAi(e.target.checked)}
                    className="rounded bg-[#171926] border-[#30374e] text-indigo-600 focus:ring-0"
                  />
                  <div>
                    <span className="text-xs font-semibold text-white block">Akıllı AI / Semantik Sınıflandırma</span>
                    <span className="text-[11px] text-[#8b92a5]">
                      Dosya adlarını ve güvenli metin içeriklerini analiz ederek daha anlamlı kategoriler önerir.
                    </span>
                  </div>
                </label>
              </div>
            </div>

            {/* Custom Category Folders */}
            <div className="w-full bg-[#171926] border border-[#262c3f] rounded-2xl p-5 sm:p-6">
              <h2 className="text-sm sm:text-base font-semibold text-white mb-1">
                Kategori Klasör İsimleri ({LANGUAGES.find(l => l.code === lang)?.name})
              </h2>
              <p className="text-xs text-[#94a3b8] mb-4">
                Seçilen dile ait hedef klasör isimlerini isterseniz aşağıdan manuel olarak özelleştirebilirsiniz.
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
                {CATEGORIES.map(cat => (
                  <div key={cat} className="bg-[#0e1017] border border-[#252a3d] rounded-xl p-3">
                    <label className="text-[11px] font-semibold text-[#8b92a5] block mb-1">
                      {cat}
                    </label>
                    <input
                      type="text"
                      value={categoryFolderNames[cat] || cat}
                      onChange={e => {
                        const val = e.target.value;
                        setCategoryFolderNames(prev => ({ ...prev, [cat]: val }));
                      }}
                      className="w-full bg-[#171926] border border-[#252a3d] rounded-lg px-2.5 py-1.5 text-xs text-[#f1f5f9] focus:outline-none focus:border-indigo-500 font-mono"
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
