# -*- coding: utf-8 -*-
import os
import sys
import time
import shutil
import ctypes
import subprocess
import threading
import webbrowser
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image
import pystray

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def elevate():
    if not is_admin():
        params = " ".join([f'"{arg}"' for arg in sys.argv])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        sys.exit(0)

def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()
APP_DIR = get_app_dir()

# Kalıcı servis kurulum klasörü
PERM_DIR = r"C:\ProgramData\ExelansDiscordFix"
os.makedirs(PERM_DIR, exist_ok=True)

DEFAULT_DOMAINS = """# Discord Temel Alan Adlari
discord.com
discord.gg
discordapp.com
discordapp.net
discord.media
discordcdn.com
discord.dev
discordstatus.com
discord.co
discord.design
dis.gd
watchanimeattheoffice.net

# Gateway, API, Ses, Medya, Guncelleyici ve CDN Sunuculari
updates.discord.com
gateway.discord.gg
cdn.discordapp.com
media.discordapp.net
images-ext-1.discordapp.net
images-ext-2.discordapp.net
status.discord.com
latency.discord.media
router.discordapp.net
dl.discordapp.net
"""

DOMAINS_FILE = os.path.join(APP_DIR, "discord_domains.txt")
if not os.path.exists(DOMAINS_FILE):
    with open(DOMAINS_FILE, "w", encoding="utf-8") as f:
        f.write(DEFAULT_DOMAINS)

def ensure_permanent_files():
    """Servis için gerekli dosyaları C:\ProgramData\ExelansDiscordFix içine kopyalar"""
    os.makedirs(PERM_DIR, exist_ok=True)
    
    # goodbyedpi.exe, WinDivert.dll, WinDivert64.sys bul
    src_candidates = [
        os.path.join(APP_DIR, "bin"),
        os.path.join(BASE_PATH, "bin"),
        r"D:\PROGRAM\6_Suruculer_ve_Diger_Araclar\goodbyedpi-0.2.3rc3-turkey\x86_64",
        r"D:\proje\ExelansDiscordFix\bin"
    ]
    
    for candidate in src_candidates:
        exe_path = os.path.join(candidate, "goodbyedpi.exe")
        if os.path.exists(exe_path):
            for fname in ["goodbyedpi.exe", "WinDivert.dll", "WinDivert64.sys"]:
                src_f = os.path.join(candidate, fname)
                dst_f = os.path.join(PERM_DIR, fname)
                if os.path.exists(src_f) and not os.path.exists(dst_f):
                    try:
                        shutil.copy2(src_f, dst_f)
                    except Exception:
                        pass
            break
            
    # Domain listesini kalıcı klasöre de kopyala
    perm_domains = os.path.join(PERM_DIR, "discord_domains.txt")
    if os.path.exists(DOMAINS_FILE):
        try:
            shutil.copy2(DOMAINS_FILE, perm_domains)
        except Exception:
            pass
    elif not os.path.exists(perm_domains):
        with open(perm_domains, "w", encoding="utf-8") as f:
            f.write(DEFAULT_DOMAINS)

def get_binary_path():
    # Önce kalıcı klasör
    p0 = os.path.join(PERM_DIR, "goodbyedpi.exe")
    if os.path.exists(p0):
        return p0
    p1 = os.path.join(APP_DIR, "bin", "goodbyedpi.exe")
    if os.path.exists(p1):
        return p1
    p2 = os.path.join(BASE_PATH, "bin", "goodbyedpi.exe")
    if os.path.exists(p2):
        return p2
    p3 = r"D:\PROGRAM\6_Suruculer_ve_Diger_Araclar\goodbyedpi-0.2.3rc3-turkey\x86_64\goodbyedpi.exe"
    if os.path.exists(p3):
        return p3
    return "goodbyedpi.exe"

PROFILES = {
    "Türk Telekom / TurkNet / Kablonet (Önerilen)": [
        "-5", "--set-ttl", "5",
        "--dns-addr", "77.88.8.8", "--dns-port", "1253",
        "--dnsv6-addr", "2a02:6b8::feed:0ff", "--dnsv6-port", "1253"
    ],
    "Superonline / Vodafone (TTL 3)": [
        "--set-ttl", "3",
        "--dns-addr", "77.88.8.8", "--dns-port", "1253",
        "--dnsv6-addr", "2a02:6b8::feed:0ff", "--dnsv6-port", "1253"
    ],
    "Superonline Alternatif 1 (Mod -5)": [
        "-5",
        "--dns-addr", "77.88.8.8", "--dns-port", "1253",
        "--dnsv6-addr", "2a02:6b8::feed:0ff", "--dnsv6-port", "1253"
    ],
    "Superonline Alternatif 2 (Ağır DPI - Mod -9)": [
        "-9",
        "--dns-addr", "77.88.8.8", "--dns-port", "1253",
        "--dnsv6-addr", "2a02:6b8::feed:0ff", "--dnsv6-port", "1253"
    ],
    "Sadece DPI Bypass (DNS Yönlendirmesiz)": [
        "-5", "--set-ttl", "5"
    ]
}

class DiscordFixApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Exelans Discord Fixer - Sadece Discord DPI Bypass")
        self.geometry("560x660")
        self.resizable(False, False)
        
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        ensure_permanent_files()
        
        icon_path = os.path.join(BASE_PATH, "discord_fix.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(APP_DIR, "discord_fix.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass
                
        self.process = None
        self.is_running = False
        self.tray_icon = None
        self.minimize_to_tray = tk.BooleanVar(value=True)
        
        self.setup_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Servis durumunu periyodik kontrol et (Canlı İzleme)
        self.service_is_active = False
        self.start_service_monitor()
        
    def start_service_monitor(self):
        self.check_service_status()
        self.after(2500, self.start_service_monitor)
        
    def setup_ui(self):
        self.configure(fg_color="#111215")
        
        # Header Frame
        header = ctk.CTkFrame(self, fg_color="#18191c", corner_radius=12)
        header.pack(fill="x", padx=16, pady=(16, 8))
        
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(pady=10, padx=16)
        
        title_label = ctk.CTkLabel(
            title_box, 
            text="⚡ EXELANS DISCORD FIXER", 
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#5865F2"
        )
        title_label.pack()
        
        sub_label = ctk.CTkLabel(
            title_box, 
            text="Yalnızca Discord Trafiğini Hedefler • Diğer Siteler ve Oyunlar Kesinlikle Etkilenmez", 
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#949ba4"
        )
        sub_label.pack(pady=(2, 0))
        
        # Durum Kartı (Status Card)
        self.status_card = ctk.CTkFrame(self, fg_color="#1e1f22", corner_radius=12)
        self.status_card.pack(fill="x", padx=16, pady=6)
        
        status_inner = ctk.CTkFrame(self.status_card, fg_color="transparent")
        status_inner.pack(pady=14, padx=16)
        
        self.status_badge = ctk.CTkLabel(
            status_inner,
            text="● KORUMA KAPALI",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#ed4245"
        )
        self.status_badge.pack()
        
        self.status_desc = ctk.CTkLabel(
            status_inner,
            text="Discord erişimi henüz aktif değil. Anlık başlatabilir veya kalıcı servis olarak kurabilirsiniz.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#b5bac1"
        )
        self.status_desc.pack(pady=(3, 0))
        
        # Ayarlar Kartı
        settings_card = ctk.CTkFrame(self, fg_color="#18191c", corner_radius=12)
        settings_card.pack(fill="x", padx=16, pady=6)
        
        p_label = ctk.CTkLabel(
            settings_card, 
            text="İnternet Servis Sağlayıcı (İSS) Modu:",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#dbdee1"
        )
        p_label.pack(anchor="w", padx=16, pady=(10, 4))
        
        self.profile_var = ctk.StringVar(value=list(PROFILES.keys())[0])
        self.profile_combo = ctk.CTkComboBox(
            settings_card,
            values=list(PROFILES.keys()),
            variable=self.profile_var,
            width=490,
            height=34,
            corner_radius=8,
            fg_color="#2b2d31",
            border_color="#383a40",
            button_color="#5865F2",
            dropdown_fg_color="#2b2d31",
            text_color="#ffffff"
        )
        self.profile_combo.pack(padx=16, pady=(0, 8))
        
        domain_row = ctk.CTkFrame(settings_card, fg_color="transparent")
        domain_row.pack(fill="x", padx=16, pady=(0, 10))
        
        domain_count = self.get_domain_count()
        self.domain_info_label = ctk.CTkLabel(
            domain_row,
            text=f"🎯 Hedef Liste: {domain_count} Discord Alan Adı",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#57F287"
        )
        self.domain_info_label.pack(side="left")
        
        edit_domains_btn = ctk.CTkButton(
            domain_row,
            text="Alan Adlarını Düzenle",
            width=140,
            height=26,
            corner_radius=6,
            fg_color="#313338",
            hover_color="#383a40",
            text_color="#dbdee1",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            command=self.open_domains_editor
        )
        edit_domains_btn.pack(side="right")
        
        # BÖLÜM 1: Anlık Başlat / Durdur
        self.action_btn = ctk.CTkButton(
            self,
            text="DİSCORD KORUMASINI ANLIK BAŞLAT",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            height=44,
            corner_radius=10,
            fg_color="#5865F2",
            hover_color="#4752C4",
            text_color="#ffffff",
            command=self.toggle_service
        )
        self.action_btn.pack(fill="x", padx=16, pady=4)
        
        # BÖLÜM 2: Kalıcı Windows Hizmeti Kartı
        service_frame = ctk.CTkFrame(self, fg_color="#18191c", corner_radius=12)
        service_frame.pack(fill="x", padx=16, pady=6)
        
        serv_title_row = ctk.CTkFrame(service_frame, fg_color="transparent")
        serv_title_row.pack(fill="x", padx=16, pady=(10, 4))
        
        serv_title = ctk.CTkLabel(
            serv_title_row,
            text="🛠 Kalıcı Windows Hizmeti (Kaldırana Kadar 7/24)",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#dbdee1"
        )
        serv_title.pack(side="left")
        
        self.service_status_label = ctk.CTkLabel(
            serv_title_row,
            text="Hizmet: Kurulu Değil",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#949ba4"
        )
        self.service_status_label.pack(side="right")
        
        serv_desc = ctk.CTkLabel(
            service_frame,
            text="Windows'a servis olarak kurulur. PC açıldığında otomatik başlar,\nuygulamayı kapatsanız bile siz kaldırana kadar arkada sadece Discord için çalışır.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#949ba4",
            justify="left"
        )
        serv_desc.pack(anchor="w", padx=16, pady=(0, 8))
        
        serv_btn_row = ctk.CTkFrame(service_frame, fg_color="transparent")
        serv_btn_row.pack(fill="x", padx=16, pady=(0, 10))
        
        self.install_service_btn = ctk.CTkButton(
            serv_btn_row,
            text="🚀 Windows Hizmeti Olarak Kur (Kalıcı)",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=36,
            corner_radius=8,
            fg_color="#23a55a",
            hover_color="#1b8547",
            command=self.install_as_service
        )
        self.install_service_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))
        
        self.remove_service_btn = ctk.CTkButton(
            serv_btn_row,
            text="🛑 Hizmeti Kaldır",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=36,
            corner_radius=8,
            fg_color="#da373c",
            hover_color="#a82b2f",
            command=self.remove_service
        )
        self.remove_service_btn.pack(side="right", fill="x", expand=True, padx=(6, 0))
        
        # Discord'u Yeniden Başlat Yardımcısı
        restart_discord_btn = ctk.CTkButton(
            self,
            text="🔄 Discord'u Yeniden Başlat (Gerektiğinde Önbelleği Temizler)",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            height=30,
            corner_radius=8,
            fg_color="#2b2d31",
            hover_color="#383a40",
            text_color="#dbdee1",
            command=self.restart_discord_app
        )
        restart_discord_btn.pack(fill="x", padx=16, pady=(2, 4))
        
        # Seçenekler
        options_row = ctk.CTkFrame(self, fg_color="transparent")
        options_row.pack(fill="x", padx=20, pady=2)
        
        tray_cb = ctk.CTkCheckBox(
            options_row,
            text="Kapatıldığında saatin yanına (tepsiye) küçült",
            variable=self.minimize_to_tray,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#949ba4",
            checkbox_height=16,
            checkbox_width=16,
            corner_radius=4,
            fg_color="#5865F2"
        )
        tray_cb.pack(side="left")
        
        # Footer
        footer = ctk.CTkFrame(self, fg_color="#18191c", height=36, corner_radius=10)
        footer.pack(fill="x", padx=16, pady=(6, 12), side="bottom")
        
        ad_label = ctk.CTkLabel(
            footer,
            text="🌐 Resmi Web Sitemiz: www.exelansmacro.com",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#5865F2",
            cursor="hand2"
        )
        ad_label.pack(pady=7)
        ad_label.bind("<Button-1>", lambda e: webbrowser.open("https://www.exelansmacro.com"))

    def get_domain_count(self):
        try:
            if os.path.exists(DOMAINS_FILE):
                with open(DOMAINS_FILE, "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
                return len(lines)
        except Exception:
            pass
        return 0

    def open_domains_editor(self):
        editor = ctk.CTkToplevel(self)
        editor.title("Discord Alan Adları Listesi")
        editor.geometry("460x420")
        editor.grab_set()
        
        desc = ctk.CTkLabel(
            editor, 
            text="GoodbyeDPI sadece bu listedeki adreslere DPI atlatması uygular.\nHer satıra bir alan adı yazınız.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#b5bac1",
            justify="center"
        )
        desc.pack(padx=16, pady=(12, 6))
        
        textbox = ctk.CTkTextbox(editor, font=ctk.CTkFont(family="Consolas", size=12), corner_radius=8)
        textbox.pack(fill="both", expand=True, padx=16, pady=8)
        
        if os.path.exists(DOMAINS_FILE):
            with open(DOMAINS_FILE, "r", encoding="utf-8") as f:
                textbox.insert("1.0", f.read())
                
        def save_and_close():
            content = textbox.get("1.0", "end-1c")
            with open(DOMAINS_FILE, "w", encoding="utf-8") as f:
                f.write(content)
            # Kalıcı klasöre de eşitle
            perm_domains = os.path.join(PERM_DIR, "discord_domains.txt")
            with open(perm_domains, "w", encoding="utf-8") as f:
                f.write(content)
            self.domain_info_label.configure(text=f"🎯 Hedef Liste: {self.get_domain_count()} Discord Alan Adı")
            editor.destroy()
            
        save_btn = ctk.CTkButton(
            editor,
            text="Kaydet ve Kapat",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#5865F2",
            hover_color="#4752C4",
            height=36,
            command=save_and_close
        )
        save_btn.pack(fill="x", padx=16, pady=(0, 14))

    def flush_dns(self):
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.run(["ipconfig", "/flushdns"], startupinfo=startupinfo, creationflags=0x08000000)
        except Exception:
            pass

    def cleanup_leftovers(self):
        # Eğer Windows Hizmeti olarak çalışıyorsa servisi öldürme!
        if getattr(self, 'service_is_active', False):
            return
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.run(["taskkill", "/F", "/IM", "goodbyedpi.exe"], startupinfo=startupinfo, creationflags=0x08000000)
        except Exception:
            pass

    def restart_discord_app(self):
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.run(["taskkill", "/F", "/IM", "Discord.exe"], startupinfo=startupinfo, creationflags=0x08000000)
            self.flush_dns()
            time.sleep(1)
            # Discord'u kullanıcı local appdata'sından başlat
            user_prof = os.environ.get("USERPROFILE", "")
            discord_lnk = os.path.join(user_prof, r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Discord Inc\Discord.lnk")
            if os.path.exists(discord_lnk):
                os.startfile(discord_lnk)
            else:
                discord_update = os.path.join(user_prof, r"AppData\Local\Discord\Update.exe")
                if os.path.exists(discord_update):
                    subprocess.Popen([discord_update, "--processStart", "Discord.exe"])
                else:
                    messagebox.showinfo("Bilgi", "Discord kapatıldı ve DNS temizlendi. Lütfen Discord'u masaüstünden açın.")
                    return
            messagebox.showinfo("Bilgi", "Discord yeniden başlatıldı.")
        except Exception as e:
            messagebox.showerror("Hata", f"Discord yeniden başlatılamadı: {e}")

    def check_service_status(self):
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            res = subprocess.run(["sc", "query", "GoodbyeDPI"], startupinfo=startupinfo, creationflags=0x08000000, capture_output=True, text=True)
            if "RUNNING" in res.stdout:
                self.service_is_active = True
                self.service_status_label.configure(text="Hizmet: 🟢 ÇALIŞIYOR (KALICI)", text_color="#57F287")
                self.status_badge.configure(text="● KALICI HİZMET AKTİF (DISCORD BAĞLI)", text_color="#57F287")
                self.status_desc.configure(
                    text="Windows Hizmeti devrede. Uygulamayı kapatsanız veya PC'yi yeniden başlatsanız dahi çalışacaktır.",
                    text_color="#dbdee1"
                )
                self.action_btn.configure(state="disabled", text="DİSCORD KALICI HİZMETİ ÇALIŞIYOR")
            elif "STOPPED" in res.stdout:
                self.service_is_active = False
                self.service_status_label.configure(text="Hizmet: 🟡 DURDURULDU", text_color="#faa61a")
                if not self.is_running:
                    self.action_btn.configure(state="normal", text="DİSCORD KORUMASINI ANLIK BAŞLAT")
                    self.status_badge.configure(text="● KORUMA KAPALI", text_color="#ed4245")
            else:
                self.service_is_active = False
                self.service_status_label.configure(text="Hizmet: ⚪ KURULU DEĞİL", text_color="#949ba4")
                if not self.is_running:
                    self.action_btn.configure(state="normal", text="DİSCORD KORUMASINI ANLIK BAŞLAT")
        except Exception:
            pass

    def install_as_service(self):
        ensure_permanent_files()
        
        # Hizmet doğrudan kalıcı C:\ProgramData\ExelansDiscordFix klasörünü kullanmalı!
        perm_bin = os.path.join(PERM_DIR, "goodbyedpi.exe")
        perm_domains = os.path.join(PERM_DIR, "discord_domains.txt")
        
        if not os.path.exists(perm_bin):
            messagebox.showerror("Hata", f"Kalıcı goodbyedpi.exe bulunamadı:\n{perm_bin}")
            return
            
        profile_key = self.profile_var.get()
        args = PROFILES.get(profile_key, PROFILES["Türk Telekom / TurkNet / Kablonet (Önerilen)"])
        args_str = " ".join(args)
        
        # cmd.exe aracılığıyla tam tırnaklı binPath ve otomatik kurtarma (sc failure restart) ekle
        cmd_service = f'cmd.exe /c "sc stop GoodbyeDPI & sc delete GoodbyeDPI & sc stop WinDivert & sc delete WinDivert & sc create GoodbyeDPI binPath= "\\"{perm_bin}\\" {args_str} --blacklist \\"{perm_domains}\\"" start= auto & sc description GoodbyeDPI "Yalnizca Discord DPI Engelini Kaldirir (Exelans)" & sc failure GoodbyeDPI reset= 86400 actions= restart/2000/restart/2000/restart/5000 & sc start GoodbyeDPI"'
        
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            if self.is_running:
                self.stop_service()
                
            res = subprocess.run(
                cmd_service,
                startupinfo=startupinfo,
                creationflags=0x08000000,
                capture_output=True,
                text=True,
                shell=True
            )
            
            self.flush_dns()
            time.sleep(1.2)
            
            # Hizmet durumunu kontrol et
            check_res = subprocess.run(["sc", "query", "GoodbyeDPI"], startupinfo=startupinfo, creationflags=0x08000000, capture_output=True, text=True)
            
            if "RUNNING" in check_res.stdout:
                self.check_service_status()
                messagebox.showinfo("Başarılı", "Windows Hizmeti başarıyla kuruldu ve BAŞLATILDI!\n\nArtık hiçbir pencere açmanıza gerek yoktur. Bilgisayarınızı yeniden başlatsanız dahi arkada siz kaldırana kadar 7/24 çalışacaktır.\n\nEğer Discord arkada açıksa 'Discord'u Yeniden Başlat' butonuna basabilir veya Discord'u kapatıp açabilirsiniz.")
            else:
                self.check_service_status()
                err_detail = check_res.stdout or res.stdout or res.stderr
                messagebox.showerror("Hata", f"Hizmet kuruldu ancak çalıştırılamadı.\n\nDetay:\n{err_detail}\n\nLütfen yönetici haklarıyla çalıştığınızdan emin olun.")
        except Exception as e:
            messagebox.showerror("Hata", f"Hizmet kurulurken hata oluştu: {e}")

    def remove_service(self):
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            cmd_remove = 'cmd.exe /c "sc stop GoodbyeDPI & sc delete GoodbyeDPI & sc stop WinDivert & sc delete WinDivert & sc stop WinDivert14 & sc delete WinDivert14"'
            subprocess.run(cmd_remove, startupinfo=startupinfo, creationflags=0x08000000, shell=True)
            
            self.flush_dns()
            self.action_btn.configure(state="normal", text="DİSCORD KORUMASINI ANLIK BAŞLAT")
            self.update_ui_stopped()
            self.check_service_status()
            messagebox.showinfo("Bilgi", "Windows Hizmeti başarıyla durduruldu ve sistemden kaldırıldı.")
        except Exception as e:
            messagebox.showerror("Hata", f"Hizmet kaldırılırken hata oluştu: {e}")

    def toggle_service(self):
        if self.is_running:
            self.stop_service()
        else:
            self.start_service()

    def start_service(self):
        bin_path = get_binary_path()
        if not os.path.exists(bin_path):
            messagebox.showerror("Hata", f"goodbyedpi.exe bulunamadı:\n{bin_path}")
            return
            
        profile_key = self.profile_var.get()
        args = PROFILES.get(profile_key, PROFILES["Türk Telekom / TurkNet / Kablonet (Önerilen)"])
        cmd = [bin_path] + args + ["--blacklist", DOMAINS_FILE]
        working_dir = os.path.dirname(bin_path)
        
        try:
            self.cleanup_leftovers()
            self.flush_dns()
            
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            self.process = subprocess.Popen(
                cmd,
                cwd=working_dir,
                startupinfo=startupinfo,
                creationflags=0x08000000,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            time.sleep(0.5)
            if self.process.poll() is not None:
                err = self.process.stderr.read().decode('cp850', errors='ignore')
                messagebox.showerror("Hata", f"Başlatılamadı!\n\nDetay: {err}\n\nYönetici haklarıyla çalıştığınızdan emin olun.")
                return
                
            self.is_running = True
            self.update_ui_running()
            threading.Thread(target=self.monitor_process, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Servis başlatılırken hata oluştu: {e}")

    def monitor_process(self):
        while self.is_running and self.process:
            if self.process.poll() is not None:
                self.after(0, self.on_process_unexpected_exit)
                break
            time.sleep(1)

    def on_process_unexpected_exit(self):
        if self.is_running:
            self.is_running = False
            self.update_ui_stopped()

    def stop_service(self):
        self.is_running = False
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=1.5)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
            self.process = None
            
        self.cleanup_leftovers()
        self.flush_dns()
        self.update_ui_stopped()

    def update_ui_running(self):
        self.status_badge.configure(text="● ANLIK KORUMA AKTİF (DISCORD BAĞLI)", text_color="#57F287")
        self.status_desc.configure(
            text="Discord trafiği başarıyla yönlendiriliyor. Diğer tüm internet trafiğiniz orijinal hızında akıyor.",
            text_color="#dbdee1"
        )
        self.action_btn.configure(
            text="KORUMAYI DURDUR",
            fg_color="#ed4245",
            hover_color="#c03537"
        )
        self.profile_combo.configure(state="disabled")

    def update_ui_stopped(self):
        self.status_badge.configure(text="● KORUMA KAPALI", text_color="#ed4245")
        self.status_desc.configure(
            text="Discord erişimi henüz aktif değil. Anlık başlatabilir veya kalıcı servis olarak kurabilirsiniz.",
            text_color="#b5bac1"
        )
        self.action_btn.configure(
            text="DİSCORD KORUMASINI ANLIK BAŞLAT",
            fg_color="#5865F2",
            hover_color="#4752C4"
        )
        self.profile_combo.configure(state="normal")

    def on_close(self):
        if self.minimize_to_tray.get():
            self.withdraw()
            self.create_tray_icon()
        else:
            self.full_exit()

    def create_tray_icon(self):
        if self.tray_icon:
            return
            
        icon_path = os.path.join(BASE_PATH, "discord_fix.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(APP_DIR, "discord_fix.ico")
            
        if os.path.exists(icon_path):
            img = Image.open(icon_path)
        else:
            img = Image.new("RGBA", (64, 64), (88, 101, 242, 255))
            
        menu = pystray.Menu(
            pystray.MenuItem("Pencereyi Göster", self.tray_show_window, default=True),
            pystray.MenuItem("Korumayı Aç / Kapat", self.tray_toggle_service),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Tamamen Çıkış", self.tray_full_exit)
        )
        
        self.tray_icon = pystray.Icon("ExelansDiscordFix", img, "Exelans Discord Fixer", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def tray_show_window(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        self.after(0, self.deiconify)

    def tray_toggle_service(self, icon=None, item=None):
        self.after(0, self.toggle_service)

    def tray_full_exit(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        self.after(0, self.full_exit)

    def full_exit(self):
        self.stop_service()
        self.destroy()
        sys.exit(0)

if __name__ == "__main__":
    elevate()
    app = DiscordFixApp()
    app.mainloop()
