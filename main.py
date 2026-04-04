import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import asyncio
import yt_dlp
import json
import sqlite3
import time
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# ========================================================
# TOP.GG LİNKİNİ BURAYA YAZ (Yazana kadar kilit sistemi kapalı kalır)
TOPGG_LINK = "" # Örn: "https://top.gg/bot/123456"
# ========================================================

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
}
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

# --- VERİTABANI (SQLITE) KURULUMU ---
conn = sqlite3.connect('oyuncular.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS profiller 
             (id INTEGER PRIMARY KEY, puan INTEGER DEFAULT 0, oynanan_oyun INTEGER DEFAULT 0)''')
try: c.execute("ALTER TABLE profiller ADD COLUMN son_gunluk REAL DEFAULT 0")
except: pass
try: c.execute("ALTER TABLE profiller ADD COLUMN secili_unvan TEXT DEFAULT 'Acemi Dinleyici'")
except: pass
try: c.execute("ALTER TABLE profiller ADD COLUMN pay_miktari INTEGER DEFAULT 0")
except: pass
try: c.execute("ALTER TABLE profiller ADD COLUMN son_pay_tarihi REAL DEFAULT 0")
except: pass

c.execute('''CREATE TABLE IF NOT EXISTS envanter (kullanici_id INTEGER, unvan TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS sunucular (guild_id INTEGER PRIMARY KEY, aktif INTEGER DEFAULT 0)''')
conn.commit()

# --- MARKET SİSTEMİ ---
MARKET = {
    "nota çırağı": 1000, "meraklı plak": 1000, "acemi şifreci": 1000, "fısıldayan melodi": 1000, "şarkı çaylağı": 1000, "müzikal tomurcuk": 1000,
    "ritim gezgini": 2500, "melodi dedektifi": 2500, "akor avcısı": 2500, "ses izcisi": 2500, "gizemli kaset": 2500, "müzikal bulmaca": 2500,
    "bilmece ozanı": 4500, "şifreli notalar": 4500, "akustik kâhin": 4500, "bilmece bestekârı": 4500, "melodik zeka": 4500, "gizemli solist": 4500,
    "muamma maestrosu": 6500, "senfoni bilgini": 6500, "şarkıların sırdaşı": 6500, "müzikal sherlock": 6500, "ritim büyücüsü": 6500, "melodi şifre çözücüsü": 6500,
    "bilmece üstadı": 10000, "evrensel virtüöz": 10000, "şarkıların kâhini": 10000, "notaların efendisi": 10000, "altın sesli dahi": 10000, "müzik ve gizem efsanesi": 10000
}

EXACT_TITLES = {
    "nota çırağı": "Nota Çırağı", "meraklı plak": "Meraklı Plak", "acemi şifreci": "Acemi Şifreci", "fısıldayan melodi": "Fısıldayan Melodi", "şarkı çaylağı": "Şarkı Çaylağı", "müzikal tomurcuk": "Müzikal Tomurcuk",
    "ritim gezgini": "Ritim Gezgini", "melodi dedektifi": "Melodi Dedektifi", "akor avcısı": "Akor Avcısı", "ses izcisi": "Ses İzcisi", "gizemli kaset": "Gizemli Kaset", "müzikal bulmaca": "Müzikal Bulmaca",
    "bilmece ozanı": "Bilmece Ozanı", "şifreli notalar": "Şifreli Notalar", "akustik kâhin": "Akustik Kâhin", "bilmece bestekârı": "Bilmece Bestekârı", "melodik zeka": "Melodik Zeka", "gizemli solist": "Gizemli Solist",
    "muamma maestrosu": "Muamma Maestrosu", "senfoni bilgini": "Senfoni Bilgini", "şarkıların sırdaşı": "Şarkıların Sırdaşı", "müzikal sherlock": "Müzikal Sherlock", "ritim büyücüsü": "Ritim Büyücüsü", "melodi şifre çözücüsü": "Melodi Şifre Çözücüsü",
    "bilmece üstadı": "Bilmece Üstadı", "evrensel virtüöz": "Evrensel Virtüöz", "şarkıların kâhini": "Şarkıların Kâhini", "notaların efendisi": "Notaların Efendisi", "altın sesli dahi": "Altın Sesli Dahi", "müzik ve gizem efsanesi": "Müzik ve Gizem Efsanesi"
}

# --- GLOBAL DURUM ---
aktif_oyun_sayisi = 0

async def bot_durumunu_guncelle():
    global aktif_oyun_sayisi
    if aktif_oyun_sayisi > 0:
        await bot.change_presence(activity=discord.Game(name=f"Şu an oyun oynanıyor (Sıradasın)"))
    else:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!help | /profil"))

# --- SUNUCU KİLİDİ KONTROLLERİ ---
def sunucu_aktif_mi(guild_id):
    if not TOPGG_LINK: return True 
    if not guild_id: return True
    c.execute("SELECT aktif FROM sunucular WHERE guild_id = ?", (guild_id,))
    sonuc = c.fetchone()
    if not sonuc:
        c.execute("INSERT INTO sunucular (guild_id, aktif) VALUES (?, 0)", (guild_id,))
        conn.commit()
        return False
    return sonuc[0] == 1

@bot.check
async def global_check(ctx):
    if ctx.command.name in ['help', 'yardim', 'info', 'onayla']: return True
    if not sunucu_aktif_mi(ctx.guild.id):
        await ctx.send(f"🔒 **Bot bu sunucuda henüz kilitli!**\nLütfen botun rolünü ayarlardan yukarı taşıyın ve [Top.gg Üzerinden]({TOPGG_LINK}) oy verdikten sonra kilidi açmak için **`!onayla`** yazın.")
        return False
    return True

@bot.tree.interaction_check
async def slash_check(interaction: discord.Interaction):
    if not sunucu_aktif_mi(interaction.guild_id):
        await interaction.response.send_message("🔒 **Bot kilitli!** Kilidi açmak için sohbete `!onayla` yazın.", ephemeral=True)
        return False
    return True

@bot.event
async def on_guild_join(guild):
    c.execute("INSERT OR IGNORE INTO sunucular (guild_id, aktif) VALUES (?, 0)", (guild.id,))
    conn.commit()
    if not TOPGG_LINK: return 
    
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            embed = discord.Embed(title="🎵 Rentunes Arena'ya Hoş Geldiniz!", description="Sıradan bir müzik botu değil; E-Spor ve Kumar arenasına adım attınız!", color=discord.Color.red())
            embed.add_field(name="⚙️ ADIM 1: Rolü Yukarı Taşı!", value="Botun sizleri maç başladığında özel odalara çekebilmesi için sunucu ayarlarından **Rentunes** rolünü diğer üyelerin üstüne taşıyın.", inline=False)
            embed.add_field(name="🚀 ADIM 2: Kilidi Aç (Oy Ver)!", value=f"Botu kullanmaya başlamak için [Top.gg Sayfamıza]({TOPGG_LINK}) gidip oy verin. Oy verdikten sonra bu kanala **`!onayla`** yazarak botun kilidini açabilirsiniz.", inline=False)
            embed.set_footer(text="Bu adımları tamamlayana kadar sadece !help komutu çalışır.")
            await channel.send(embed=embed)
            break

# --- VERİTABANI İŞLEMLERİ ---
def db_puan_getir(kullanici_id):
    c.execute("SELECT puan FROM profiller WHERE id = ?", (kullanici_id,))
    sonuc = c.fetchone()
    return sonuc[0] if sonuc else 0

def db_puan_ekle(kullanici_id, eklenecek_puan):
    c.execute("SELECT puan FROM profiller WHERE id = ?", (kullanici_id,))
    sonuc = c.fetchone()
    if sonuc is None:
        yeni_puan = max(0, eklenecek_puan)
        c.execute("INSERT INTO profiller (id, puan, oynanan_oyun, son_gunluk, secili_unvan, pay_miktari, son_pay_tarihi) VALUES (?, ?, ?, 0, 'Acemi Dinleyici', 0, 0)", (kullanici_id, yeni_puan, 1))
    else:
        yeni_puan = max(0, sonuc[0] + eklenecek_puan)
        c.execute("UPDATE profiller SET puan = ? WHERE id = ?", (yeni_puan, kullanici_id))
    conn.commit()

def db_oyun_sayisi_arttir(kullanici_id):
    c.execute("SELECT oynanan_oyun FROM profiller WHERE id = ?", (kullanici_id,))
    sonuc = c.fetchone()
    if sonuc is None:
        c.execute("INSERT INTO profiller (id, puan, oynanan_oyun, son_gunluk, secili_unvan, pay_miktari, son_pay_tarihi) VALUES (?, 0, 1, 0, 'Acemi Dinleyici', 0, 0)", (kullanici_id,))
    else:
        c.execute("UPDATE profiller SET oynanan_oyun = ? WHERE id = ?", (sonuc[0] + 1, kullanici_id))
    conn.commit()

def db_profil_getir(kullanici_id):
    c.execute("SELECT puan, oynanan_oyun, secili_unvan FROM profiller WHERE id = ?", (kullanici_id,))
    sonuc = c.fetchone()
    return sonuc if sonuc else (0, 0, 'Acemi Dinleyici')

def db_unvan_var_mi(kullanici_id, unvan):
    c.execute("SELECT 1 FROM envanter WHERE kullanici_id = ? AND unvan = ?", (kullanici_id, unvan))
    return c.fetchone() is not None

# --- YARDIMCI FONKSİYONLAR ---
def sarkicilari_bul():
    secenekler = [discord.SelectOption(label="🌟 KARIŞIK (HEPSİ)", value="karisik", description="Herkes çalar!")]
    for dosya in os.listdir('.'):
        if dosya.endswith('.json'):
            isim = dosya[:-5]
            secenekler.append(discord.SelectOption(label=isim.upper(), value=isim))
    if len(secenekler) > 25: secenekler = secenekler[:25]
    if len(secenekler) == 1: secenekler.append(discord.SelectOption(label="Şarkıcı Bulunamadı", value="yok"))
    return secenekler

def sarkici_getir(isim):
    dosya_adi = f"{isim.lower()}.json"
    if os.path.exists(dosya_adi):
        with open(dosya_adi, 'r', encoding='utf-8') as f: return json.load(f)
    return None

def rastgele_secimler_uret():
    json_dosyalar = [f[:-5] for f in os.listdir('.') if f.endswith('.json')]
    if not json_dosyalar: return None
    return {
        "sarkici": "karisik" if len(json_dosyalar) > 1 else json_dosyalar[0],
        "mod": random.choice(["tum", "populer"]),
        "zorluk": random.choice(["kolay", "normal", "zor"]),
        "raund": random.choice(["1", "3", "5", "10"])
    }

def ayar_cevir(secimler):
    if isinstance(secimler['sarkici'], list):
        sarkici_g = f"✨ SEÇİLİ ({len(secimler['sarkici'])} Şarkıcı)"
    elif secimler['sarkici'] == "karisik":
        sarkici_g = "🌟 KARIŞIK"
    else:
        sarkici_g = secimler['sarkici'].upper()
    return sarkici_g, secimler['zorluk'].upper(), secimler['raund']

(TEMİZLİK SİSTEMLİ) ---
class SecenekButonu(discord.ui.Button):
    def __init__(self, etiket, dogru_cevap):
        super().__init__(label=etiket, style=discord.ButtonStyle.primary)
        self.dogru_cevap = dogru_cevap

    async def callback(self, interaction: discord.Interaction):
        if interaction.user not in self.view.oyuncular:
            return await interaction.response.send_message("Sen bu oyunda değilsin ekmek kafa!", ephemeral=True)
        if self.view.kazanan_belli_mi:
            return await interaction.response.send_message("Geç kaldın!", ephemeral=True)
        self.view.kazanan_belli_mi = True
        
        if self.label == self.dogru_cevap:
            self.view.puanlar[interaction.user.id] += 10
            mesaj = f"🎉 **Helal!** {interaction.user.mention} doğru bildi!"
        else:
            if getattr(self.view, 'rekabetci', False):
                self.view.puanlar[interaction.user.id] -= 10
                mesaj = f"💥 **BÜYÜK HATA!** {interaction.user.mention} yanlış bildi ve maç skorundan **-10 Puan** yedi! Doğrusu: **{self.dogru_cevap}**"
            else:
                mesaj = f"❌ **Patladın!** {interaction.user.mention} yanlış bildi. Doğrusu: **{self.dogru_cevap}**"
        
        yeni_icerik = f"{interaction.message.content}\n\n{mesaj}"
        await interaction.response.edit_message(content=yeni_icerik, view=None)
        self.view.stop()

class TahminView(discord.ui.View):
    def __init__(self, dogru_cevap, sahte_siklar, oyuncular, puanlar, rekabetci=False):
        super().__init__(timeout=15)
        self.dogru_cevap = dogru_cevap
        self.oyuncular = oyuncular
        self.puanlar = puanlar
        self.rekabetci = rekabetci
        self.kazanan_belli_mi = False

        secenekler = [dogru_cevap]
        while len(secenekler) < 4:
            rastgele_secim = random.choice(sahte_siklar)
            if rastgele_secim not in secenekler: secenekler.append(rastgele_secim)
        random.shuffle(secenekler)
        for secenek in secenekler: self.add_item(SecenekButonu(secenek, dogru_cevap))

# --- AYAR VE DAVET MENÜLERİ ---
class AyarSelect(discord.ui.Select):
    def __init__(self, placeholder, options, custom_id, row, max_vals=1):
        super().__init__(placeholder=placeholder, min_values=1, max_values=max_vals, options=options, custom_id=custom_id, row=row)
    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.view.kurucu: return await interaction.response.send_message("Sen kurucu değilsin!", ephemeral=True)
        if self.custom_id == "sarkici_coklu":
            self.view.secilen_sarkicilar = self.values
        else:
            self.view.secimler[self.custom_id] = self.values[0]
        await interaction.response.defer()

class NormalAyarView(discord.ui.View):
    def __init__(self, kurucu):
        super().__init__(timeout=120)
        self.kurucu = kurucu
        self.secimler = {"sarkici": None, "mod": None, "zorluk": None, "raund": None}
        self.basladi = False

        self.add_item(AyarSelect("🎤 Şarkıcıyı Seç", sarkicilari_bul(), "sarkici", 0))
        self.add_item(AyarSelect("💽 Oyun Modunu Seç", [discord.SelectOption(label="Tüm Şarkılar", value="tum"), discord.SelectOption(label="En Popüler 15 Şarkı", value="populer")], "mod", 1))
        self.add_item(AyarSelect("⚙️ Zorluğu Seç", [discord.SelectOption(label="Kolay (5 Saniye)", value="kolay"), discord.SelectOption(label="Normal (3 Saniye)", value="normal"), discord.SelectOption(label="Zor (1.5 Saniye)", value="zor")], "zorluk", 2))
        self.add_item(AyarSelect("🔄 Raund Sayısı", [discord.SelectOption(label="1 Raund", value="1"), discord.SelectOption(label="3 Raund", value="3"), discord.SelectOption(label="5 Raund", value="5"), discord.SelectOption(label="10 Raund", value="10")], "raund", 3))

    @discord.ui.button(label="🚀 AYARLARI ONAYLA VE BAŞLAT", style=discord.ButtonStyle.success, row=4)
    async def basla_buton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.kurucu: return await interaction.response.send_message("Sen değilsin!", ephemeral=True)
        if not all(self.secimler.values()): return await interaction.response.send_message("Bütün seçimleri yap!", ephemeral=True)
        self.basladi = True
        await interaction.response.edit_message(content="✅ Ayarlar onaylandı!", view=None)
        self.stop()

class CokluSarkiciView(discord.ui.View):
    def __init__(self, kurucu):
        super().__init__(timeout=120)
        self.kurucu = kurucu
        self.secilen_sarkicilar = []
        self.basladi = False
        
        options = []
        for dosya in os.listdir('.'):
            if dosya.endswith('.json'):
                isim = dosya[:-5]
                options.append(discord.SelectOption(label=isim.upper(), value=isim))
        if len(options) > 25: options = options[:25]
        if not options: options.append(discord.SelectOption(label="Yok", value="yok"))
        
        self.add_item(AyarSelect("🎤 Çoklu Şarkıcı Seç (İstediğin kadar)", options, "sarkici_coklu", 0, max_vals=len(options)))

    @discord.ui.button(label="İleri ➡️", style=discord.ButtonStyle.primary, row=1)
    async def ileri_buton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.kurucu: return await interaction.response.send_message("Sen değilsin!", ephemeral=True)
        if not self.secilen_sarkicilar: return await interaction.response.send_message("En az 1 şarkıcı seç!", ephemeral=True)
        self.basladi = True
        await interaction.response.defer()
        self.stop()

class SeciliAyarView(discord.ui.View):
    def __init__(self, kurucu):
        super().__init__(timeout=120)
        self.kurucu = kurucu
        self.secimler = {"mod": None, "zorluk": None, "raund": None}
        self.basladi = False

        self.add_item(AyarSelect("💽 Oyun Modunu Seç", [discord.SelectOption(label="Tüm Şarkılar", value="tum"), discord.SelectOption(label="En Popüler 15 Şarkı", value="populer")], "mod", 0))
        self.add_item(AyarSelect("⚙️ Zorluğu Seç", [discord.SelectOption(label="Kolay (5 Saniye)", value="kolay"), discord.SelectOption(label="Normal (3 Saniye)", value="normal"), discord.SelectOption(label="Zor (1.5 Saniye)", value="zor")], "zorluk", 1))
        self.add_item(AyarSelect("🔄 Raund Sayısı", [discord.SelectOption(label="1 Raund", value="1"), discord.SelectOption(label="3 Raund", value="3"), discord.SelectOption(label="5 Raund", value="5"), discord.SelectOption(label="10 Raund", value="10")], "raund", 2))

    @discord.ui.button(label="🚀 AYARLARI ONAYLA", style=discord.ButtonStyle.success, row=3)
    async def basla_buton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.kurucu: return await interaction.response.send_message("Sen değilsin!", ephemeral=True)
        if not all(self.secimler.values()): return await interaction.response.send_message("Bütün seçimleri yap!", ephemeral=True)
        self.basladi = True
        await interaction.response.edit_message(content="✅ Ayarlar onaylandı!", view=None)
        self.stop()

class CokluDavetView(discord.ui.View):
    def __init__(self, davetliler):
        super().__init__(timeout=90)
        self.davetliler = davetliler 
        self.kabul_edenler = set()
        self.kabul_edildi = False

    @discord.ui.button(label="Kılıçları Çek (Kabul Et)", style=discord.ButtonStyle.success)
    async def btn_kabul(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user not in self.davetliler: return await interaction.response.send_message("Bu sana değil!", ephemeral=True)
        self.kabul_edenler.add(interaction.user)
        if len(self.kabul_edenler) == len(self.davetliler):
            self.kabul_edildi = True
            await interaction.response.edit_message(content="⚔️ Herkes kabul etti! Oyun başlıyor...", view=None)
            self.stop()
        else:
            await interaction.response.send_message(f"Savaşa katıldın! Diğerleri bekleniyor... ({len(self.kabul_edenler)}/{len(self.davetliler)})", ephemeral=True)

    @discord.ui.button(label="Korktum (Reddet)", style=discord.ButtonStyle.danger)
    async def btn_red(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.davetliler:
            await interaction.response.edit_message(content=f"💥 {interaction.user.mention} korktu ve daveti reddetti! İptal.", view=None)
            self.stop()

# --- MERKEZİ AYAR ALMA FONKSİYONU ---
async def ayarlari_al(ctx, secili=False): # BURADAKİ HATA DÜZELTİLDİ (secili_mod yerine secili oldu)
    if secili:
        view1 = CokluSarkiciView(ctx.author)
        msg = await ctx.send("🎤 **1. ADIM: Şarkıcı Seçimi**\nBirden fazla şarkıcı seçip 'İleri' butonuna bas:", view=view1)
        await view1.wait()
        if not view1.basladi: return None, None
        
        view2 = SeciliAyarView(ctx.author)
        await msg.edit(content="⚙️ **2. ADIM: Oyun Ayarları**\nZorluk, Mod ve Tur sayısı seç:", view=view2)
        await view2.wait()
        if not view2.basladi: return None, None
        
        secimler = view2.secimler
        secimler['sarkici'] = view1.secilen_sarkicilar
        return secimler, msg
    else:
        view = NormalAyarView(ctx.author)
        msg = await ctx.send(f"🎮 **{ctx.author.mention}**, Oyun Ayarlarını Yap:", view=view)
        await view.wait()
        if not view.basladi: return None, None
        return view.secimler, msg

# --- ANA OYUN MOTORU (SENKRONİZE VE TEMİZ) ---
async def oyun_motoru(ctx, secimler, oyuncular, ozel_kanal=None, eski_kanallar=None, takimlar=None, rekabetci=False, bahis=0):
    global aktif_oyun_sayisi
    aktif_oyun_sayisi += 1
    await bot_durumunu_guncelle()

    try:
        kanal = ozel_kanal if ozel_kanal else ctx.author.voice.channel
        if not ctx.voice_client: vc = await kanal.connect()
        else:
            vc = ctx.voice_client
            if vc.channel != kanal: await vc.move_to(kanal)

        for oyuncu in oyuncular: db_oyun_sayisi_arttir(oyuncu.id)

        sure = 3
        if secimler["zorluk"] == "kolay": sure = 5
        elif secimler["zorluk"] == "zor": sure = 1.5
        raund_sayisi = int(secimler["raund"])
        
        puanlar = {oyuncu.id: 0 for oyuncu in oyuncular}
        sarkici_sayaclari = {}
        json_dosyalar = [f[:-5] for f in os.listdir('.') if f.endswith('.json')]
        silinecek_mesajlar = []

        if rekabetci and bahis > 0:
            odul_havuzu = bahis * len(oyuncular)
            bhs_msg = await ctx.send(f"💸 **BAHİSLER YATIRILDI!** Ortada tam **{odul_havuzu} Puan** var!")
            silinecek_mesajlar.append(bhs_msg)

        for r in range(1, raund_sayisi + 1):
            if isinstance(secimler["sarkici"], list):
                uygun_sarkicilar = [s for s in secimler["sarkici"] if sarkici_sayaclari.get(s, 0) < 2]
                if not uygun_sarkicilar:
                    uygun_sarkicilar = secimler["sarkici"]
                    sarkici_sayaclari.clear()
                aktif_sarkici = random.choice(uygun_sarkicilar)
                sarkici_sayaclari[aktif_sarkici] = sarkici_sayaclari.get(aktif_sarkici, 0) + 1
            elif secimler["sarkici"] == "karisik":
                uygun_sarkicilar = [s for s in json_dosyalar if sarkici_sayaclari.get(s, 0) < 2]
                if not uygun_sarkicilar:
                    uygun_sarkicilar = json_dosyalar
                    sarkici_sayaclari.clear()
                aktif_sarkici = random.choice(uygun_sarkicilar)
                sarkici_sayaclari[aktif_sarkici] = sarkici_sayaclari.get(aktif_sarkici, 0) + 1
            else:
                aktif_sarkici = secimler["sarkici"]

            sarkici_verisi = sarkici_getir(aktif_sarkici)
            tum_sarkilar_dict = sarkici_verisi["sarkilar"]
            sarki_isimleri = list(tum_sarkilar_dict.keys())
            if secimler["mod"] == "populer": sarki_isimleri = sarki_isimleri[:15]

            sarki_adi = random.choice(sarki_isimleri)
            sarki_detayi = tum_sarkilar_dict[sarki_adi]
            toplam_sure = int(sarki_detayi.get("sure", 180))
            baslangic_saniyesi = random.randint(15, toplam_sure - int(sure) - 10) if toplam_sure > 30 else 0

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(sarki_detayi["url"], download=False))
            
            ffmpeg_options = {
                'before_options': f'-reconnect 1 -reconnect_streamed 1 -reconnect_on_network_error 1 -reconnect_delay_max 5 -ss {baslangic_saniyesi} -probesize 32 -analyzeduration 0',
                'options': f'-vn -t {sure} -af "volume=1.5,silenceremove=start_periods=1:start_duration=0:start_threshold=-50dB"'
            }

            vc.play(discord.FFmpegPCMAudio(data['url'], **ffmpeg_options))
            
            # --- KUSURSUZ SENKRONİZASYON ---
            await asyncio.sleep(1.5)
            
            tahmin_view = TahminView(sarki_adi, sarkici_verisi["sahte_siklar"], oyuncular, puanlar, rekabetci)
            tahmin_mesaji = await ctx.send(f"🔥 **RAUND {r}/{raund_sayisi}:** 🎵 **{aktif_sarkici.upper()}** çalıyor!", view=tahmin_view)
            silinecek_mesajlar.append(tahmin_mesaji)
            
            await tahmin_view.wait() 
            if not tahmin_view.kazanan_belli_mi: 
                try: await tahmin_mesaji.edit(content=f"{tahmin_mesaji.content}\n\n⏰ Süre doldu! Doğru cevap **{sarki_adi}** olacaktı.", view=None)
                except: pass
            await asyncio.sleep(1) 

        for msg in silinecek_mesajlar:
            try: await msg.delete()
            except: pass

        await ctx.send("🏁 **OYUN BİTTİ! İŞTE SIRALAMA:**")
        
        if takimlar:
            takim_skorlari = {t_adi: sum(puanlar[o.id] for o in t_oyuncular) for t_adi, t_oyuncular in takimlar.items()}
            sirali_takimlar = sorted(takim_skorlari.items(), key=lambda x: x[1], reverse=True)
            
            sira = 1
            for takim, skor in sirali_takimlar:
                ikon = "🥇" if sira == 1 else "🥈"
                await ctx.send(f"{ikon} **{sira}. {takim}** - Toplam: **{skor} Skor**")
                for o in takimlar[takim]: await ctx.send(f"   └ 👤 {o.name}: {puanlar[o.id]}")
                sira += 1
                
            kazanan_takim_adi, kazanan_skor = sirali_takimlar[0]
            ikinci_skor = sirali_takimlar[1][1]

            if kazanan_skor == ikinci_skor:
                await ctx.send("⚖️ **BERABERLİK!** Ödül havuzu iade edildi.")
                if rekabetci and bahis > 0:
                    for o in oyuncular: db_puan_ekle(o.id, bahis)
            else:
                await ctx.send(f"\n🏆 **ŞAMPİYON: {kazanan_takim_adi}** 🎉")
                if rekabetci and bahis > 0:
                    kisi_basi_odul = (bahis * len(oyuncular)) // len(takimlar[kazanan_takim_adi])
                    for o in takimlar[kazanan_takim_adi]: db_puan_ekle(o.id, kisi_basi_odul)
                    await ctx.send(f"💰 Kazanan takımdaki her oyuncu **+{kisi_basi_odul} Puan** kazandı!")
        else:
            sirali_oyuncular = sorted(puanlar.items(), key=lambda x: x[1], reverse=True)
            sira = 1
            for o_id, skor in sirali_oyuncular:
                oyuncu_obj = discord.utils.get(oyuncular, id=o_id)
                ikon = "🥇" if sira == 1 else "🥈" if sira == 2 else "🥉" if sira == 3 else "🏅"
                await ctx.send(f"{ikon} **{sira}. {oyuncu_obj.name}** - Skor: **{skor}**")
                sira += 1
                
            kazanan_id, kazanan_skor = sirali_oyuncular[0]
            
            if len(sirali_oyuncular) > 1 and kazanan_skor == sirali_oyuncular[1][1]:
                await ctx.send("⚖️ **BERABERLİK!** Ödüller iade edildi.")
                if rekabetci and bahis > 0:
                    for o in oyuncular: db_puan_ekle(o.id, bahis)
            else:
                kazanan_isim = discord.utils.get(oyuncular, id=kazanan_id).mention
                await ctx.send(f"\n🏆 **ŞAMPİYON:** {kazanan_isim} 🎉")
                if rekabetci and bahis > 0:
                    odul = bahis * len(oyuncular)
                    db_puan_ekle(kazanan_id, odul)
                    await ctx.send(f"💰 {kazanan_isim} büyük ödül olan **{odul} Puanı** indirdi!")
        
        if vc.is_connected(): await vc.disconnect()
        
        if ozel_kanal:
            await ctx.send("🌪️ 5 saniye içinde eski odalarınıza ışınlanıyorsunuz...")
            await asyncio.sleep(5)
            if eski_kanallar:
                for oyuncu in oyuncular:
                    if oyuncu.voice and oyuncu.voice.channel == ozel_kanal:
                        try: await oyuncu.move_to(eski_kanallar.get(oyuncu.id))
                        except: pass 
            await asyncio.sleep(1)
            await ozel_kanal.delete()
            
    finally:
        aktif_oyun_sayisi -= 1
        await bot_durumunu_guncelle()

# --- EKONOMİ VE MAĞAZA KOMUTLARI ---
@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} (Rentunes) sese ve kumar masasına hazır!')
    await bot_durumunu_guncelle()
    try:
        synced = await bot.tree.sync()
        print(f"🔄 {len(synced)} adet Slash (/) komutu başarıyla yüklendi!")
    except: pass

@bot.command()
async def onayla(ctx):
    if sunucu_aktif_mi(ctx.guild.id): return await ctx.send("✅ Bot zaten bu sunucuda aktif durumda! Oyunlar başlasın!")
    c.execute("UPDATE sunucular SET aktif = 1 WHERE guild_id = ?", (ctx.guild.id,))
    conn.commit()
    await ctx.send("🎉 **Tebrikler!** Botun kilidi başarıyla açıldı. Artık tüm komutları kullanabilir, arenaya giriş yapabilirsiniz. `!help` yazarak komutları keşfedin!")

@bot.tree.command(name="profil", description="Kendinizin veya bir başkasının detaylı müzik profilini gösterir.")
@app_commands.describe(uye="Profiline bakmak istediğiniz kullanıcı (İsteğe bağlı)")
async def slash_profil(interaction: discord.Interaction, uye: discord.Member = None):
    hedef = uye or interaction.user
    puan, oynanan, secili_unvan = db_profil_getir(hedef.id)
    if not secili_unvan: secili_unvan = "Acemi Dinleyici"
    
    embed = discord.Embed(title=f"🎵 {hedef.display_name} - Oyuncu Profili", color=discord.Color.purple())
    embed.set_thumbnail(url=hedef.display_avatar.url)
    embed.add_field(name="🎖️ Ünvan", value=f"**[{secili_unvan}]**", inline=False)
    embed.add_field(name="💰 Cüzdan", value=f"**{puan} Puan**", inline=True)
    embed.add_field(name="🎮 Oynanan Maç", value=f"**{oynanan}**", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.command(aliases=['bakiye', 'para'])
async def cuzdan(ctx):
    puan = db_puan_getir(ctx.author.id)
    await ctx.send(f"💳 **{ctx.author.name}**, cüzdanında **{puan} Puan** var.")

@bot.command()
async def gunluk(ctx):
    kullanici_id = ctx.author.id
    c.execute("SELECT son_gunluk FROM profiller WHERE id = ?", (kullanici_id,))
    sonuc = c.fetchone()
    su_an = time.time()
    
    if sonuc is None or (su_an - sonuc[0]) >= 86400: 
        odul = 50
        db_puan_ekle(kullanici_id, odul)
        c.execute("UPDATE profiller SET son_gunluk = ? WHERE id = ?", (su_an, kullanici_id))
        conn.commit()
        await ctx.send(f"🎁 Günlük maaşını aldın! Cüzdanına **+{odul} Puan** eklendi.")
    else:
        kalan_saniye = 86400 - (su_an - sonuc[0])
        saat = int(kalan_saniye // 3600)
        dakika = int((kalan_saniye % 3600) // 60)
        await ctx.send(f"⏳ Açgözlülük yapma! Yeni maaş için **{saat} saat {dakika} dakika** bekle.")

@bot.command(aliases=['gonder', 'transfer'])
async def pay(ctx, hedef: discord.Member = None, miktar: int = None):
    if not hedef or not miktar or miktar <= 0: return await ctx.send("Kullanım: `!pay @kisi <miktar>`")
    if hedef == ctx.author: return await ctx.send("Kendine para gönderemezsin ekmek kafa!")
    if hedef.bot: return await ctx.send("Botlara para gönderemezsin!")
        
    c.execute("SELECT puan, pay_miktari, son_pay_tarihi FROM profiller WHERE id = ?", (ctx.author.id,))
    veri = c.fetchone()
    if not veri: return await ctx.send("Cüzdanında para yok!")
        
    puan, pay_miktari, son_pay_tarihi = veri
    su_an = time.time()
    
    if su_an - son_pay_tarihi >= 86400: pay_miktari = 0
    kalan_limit = 50 - pay_miktari
    if miktar > kalan_limit: return await ctx.send(f"❌ Günlük maksimum 50 Puan gönderebilirsin! (Kalan limitin: **{kalan_limit} Puan**)")
    if puan < miktar: return await ctx.send("❌ Cüzdanında bu kadar puan yok!")
        
    db_puan_ekle(ctx.author.id, -miktar)
    yeni_pay_miktari = pay_miktari + miktar
    yeni_tarih = su_an if pay_miktari == 0 else son_pay_tarihi 
    c.execute("UPDATE profiller SET pay_miktari = ?, son_pay_tarihi = ? WHERE id = ?", (yeni_pay_miktari, yeni_tarih, ctx.author.id))
    db_puan_ekle(hedef.id, miktar)
    conn.commit()
    await ctx.send(f"💸 **Başarılı!** {hedef.mention} kişisine **{miktar} Puan** gönderdin. (Bugün kalan limitin: {50 - yeni_pay_miktari})")

@bot.command(aliases=['magaza', 'shop'])
async def market(ctx):
    embed = discord.Embed(title="🛒 RENTUNES ÜNVAN MARKETİ", description="Puanlarını harcayarak profilin için efsanevi ünvanlar alabilirsin!", color=discord.Color.green())
    embed.add_field(name="🌱 Başlangıç Seviyesi (1000 Puan)", value="`Nota Çırağı`, `Meraklı Plak`, `Acemi Şifreci`, `Fısıldayan Melodi`, `Şarkı Çaylağı`, `Müzikal Tomurcuk`", inline=False)
    embed.add_field(name="🔍 Gelişim Seviyesi (2500 Puan)", value="`Ritim Gezgini`, `Melodi Dedektifi`, `Akor Avcısı`, `Ses İzcisi`, `Gizemli Kaset`, `Müzikal Bulmaca`", inline=False)
    embed.add_field(name="🧠 İleri Seviye (4500 Puan)", value="`Bilmece Ozanı`, `Şifreli Notalar`, `Akustik Kâhin`, `Bilmece Bestekârı`, `Melodik Zeka`, `Gizemli Solist`", inline=False)
    embed.add_field(name="🎻 Uzman Seviyesi (6500 Puan)", value="`Muamma Maestrosu`, `Senfoni Bilgini`, `Şarkıların Sırdaşı`, `Müzikal Sherlock`, `Ritim Büyücüsü`, `Melodi Şifre Çözücüsü`", inline=False)
    embed.add_field(name="👑 Efsanevi Seviye (10000 Puan)", value="`Bilmece Üstadı`, `Evrensel Virtüöz`, `Şarkıların Kâhini`, `Notaların Efendisi`, `Altın Sesli Dahi`, `Müzik ve Gizem Efsanesi`", inline=False)
    embed.set_footer(text="Satın almak için: !satinal <ünvan_adi> (Örn: !satinal nota çırağı)")
    await ctx.send(embed=embed)

@bot.command(aliases=['al'])
async def satinal(ctx, *, secilen_unvan: str = None):
    if not secilen_unvan: return await ctx.send("Neyi satın alacaksın? Kullanım: `!satinal nota çırağı`")
    secilen_unvan_kucuk = secilen_unvan.lower()
    if secilen_unvan_kucuk not in MARKET: return await ctx.send("❌ Markette böyle bir ünvan yok! Lütfen `!market` yazıp tam adını kontrol et.")
    if db_unvan_var_mi(ctx.author.id, secilen_unvan_kucuk): return await ctx.send("❌ Bu ünvana zaten sahipsin ekmek kafa!")
    
    fiyat = MARKET[secilen_unvan_kucuk]
    bakiye = db_puan_getir(ctx.author.id)
    if bakiye < fiyat: return await ctx.send(f"❌ Kasa yetersiz! Bu ünvan **{fiyat} Puan** ama sende sadece **{bakiye} Puan** var.")
        
    db_puan_ekle(ctx.author.id, -fiyat)
    c.execute("INSERT INTO envanter (kullanici_id, unvan) VALUES (?, ?)", (ctx.author.id, secilen_unvan_kucuk))
    gercek_isim = EXACT_TITLES[secilen_unvan_kucuk]
    c.execute("UPDATE profiller SET secili_unvan = ? WHERE id = ?", (gercek_isim, ctx.author.id))
    conn.commit()
    await ctx.send(f"🎉 **Tebrikler!** **{fiyat} Puan** ödeyerek **[{gercek_isim}]** ünvanını aldın. Profiline otomatik eklendi!")

@bot.command()
async def unvan(ctx, islem: str = None, *, unvan_adi: str = None):
    if islem not in ["ayarla", "set"]:
        c.execute("SELECT unvan FROM envanter WHERE kullanici_id = ?", (ctx.author.id,))
        sahip_olunanlar = c.fetchall()
        if not sahip_olunanlar: return await ctx.send("🎒 Envanterin bomboş! Önce `!market` üzerinden bir ünvan satın al.")
        liste = "\n".join([f"🔸 {EXACT_TITLES[u[0]]}" for u in sahip_olunanlar])
        embed = discord.Embed(title=f"🎒 {ctx.author.name} - Sahip Olduğun Ünvanlar", description=liste, color=discord.Color.blue())
        embed.set_footer(text="Kuşanmak için: !unvan ayarla <ünvan_adi>")
        return await ctx.send(embed=embed)
        
    if not unvan_adi: return await ctx.send("Kullanım: `!unvan ayarla <ünvan_adi>`")
    unvan_adi_kucuk = unvan_adi.lower()
    
    if unvan_adi_kucuk == "acemi dinleyici":
        c.execute("UPDATE profiller SET secili_unvan = 'Acemi Dinleyici' WHERE id = ?", (ctx.author.id,))
        conn.commit()
        return await ctx.send("✅ Ünvanın sıfırlandı: **[Acemi Dinleyici]**")

    if not db_unvan_var_mi(ctx.author.id, unvan_adi_kucuk): return await ctx.send("❌ Envanterinde böyle bir ünvan yok!")
    gercek_isim = EXACT_TITLES[unvan_adi_kucuk]
    c.execute("UPDATE profiller SET secili_unvan = ? WHERE id = ?", (gercek_isim, ctx.author.id))
    conn.commit()
    await ctx.send(f"✅ Profilin güncellendi! Yeni ünvanın: **[{gercek_isim}]**")

@bot.command()
async def profil(ctx, uye: discord.Member = None):
    hedef = uye or ctx.author
    puan, oynanan, secili_unvan = db_profil_getir(hedef.id)
    if not secili_unvan: secili_unvan = "Acemi Dinleyici"
    
    embed = discord.Embed(title=f"🎵 {hedef.display_name} - Oyuncu Profili", color=discord.Color.purple())
    embed.set_thumbnail(url=hedef.display_avatar.url)
    embed.add_field(name="🎖️ Ünvan", value=f"**[{secili_unvan}]**", inline=False)
    embed.add_field(name="💰 Cüzdan", value=f"**{puan} Puan**", inline=True)
    embed.add_field(name="🎮 Oynanan Maç", value=f"**{oynanan}**", inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def top(ctx):
    c.execute("SELECT id, puan FROM profiller ORDER BY puan DESC LIMIT 10")
    liderler = c.fetchall()
    if not liderler: return await ctx.send("Henüz kimse puan kazanmamış!")
    embed = discord.Embed(title="🏆 ZENGİNLER LİSTESİ (TOP 10)", color=discord.Color.gold())
    sira = 1
    for kullanici_id, puan in liderler:
        kullanici = bot.get_user(kullanici_id)
        if not kullanici:
            try: kullanici = await bot.fetch_user(kullanici_id)
            except: pass
        isim = kullanici.name if kullanici else f"Gizemli Oyuncu"
        ikon = "🥇" if sira == 1 else "🥈" if sira == 2 else "🥉" if sira == 3 else "💸"
        embed.add_field(name=f"{ikon} {sira}. {isim}", value=f"**{puan} Puan**", inline=False)
        sira += 1
    await ctx.send(embed=embed)

@bot.command(aliases=['yardim', 'info'])
async def help(ctx):
    mesaj = """
🎧 **RENTUNES BOT - KOMUT LİSTESİ** 🎧

**Ekonomi & Market:**
💰 `!gunluk` - Maaşını al (50 Puan).
💸 `!pay @kisi miktar` - Arkadaşına para gönder (Limit 50 Puan).
💳 `!cuzdan` - Paranızı gösterir. 
🛒 `!market` - Efsanevi RPG Ünvanları Mağazası.
🛍️ `!satinal <ünvan>` - Marketten ünvan alırsın.
🎒 `!unvan` - Envanterini açar. `!unvan ayarla <isim>` ile seçersin.
👤 `/profil` VEYA `!profil [@kisi]` & 🏆 `!top` - İstatistikler.

**Dostluk Modları (Puan Düşmez, Mikrofonlar Açık!):**
🎮 `!oyna [@kisi]` - Teksen antrenman, etiketlersen DOSTLUK 1V1 atar.
🤝 `!secili @kisi` - Seçtiğin çoklu şarkıcılarla dostluk 1v1'i at.
🎉 `!oynabirlikte` & `!secilibirlikte` - Arkadaşlarınla bedava parti odası!
🎲 `!rastgele` - Rastgele ayarlarla antrenman.

**Kumar & Rekabetçi (Giriş Ücretli, Yanlış Şık -10 Puan, Ses Kilitli!):**
⚔️ `!vs @kisi [bahis]` - Düello at, paraları kap! (Örn: !vs @ahmet 100)
⚔️ `!secilivs @kisi [bahis]` - Seçtiğin çoklu şarkıcılarla kumar düellosu.
🩸 `!ffa [bahis]` & `!seciliffa` - Herkes tek kumar masası!
🔵🔴 `!2vs2` & `!3vs3` - Klan savaşları (Giriş 10 Puan).
"""
    await ctx.send(mesaj)

# --- OYUN KOMUTLARI ALTYAPISI ---
def bakiye_kontrol(oyuncular, gereken_bakiye):
    return [o.mention for o in oyuncular if db_puan_getir(o.id) < gereken_bakiye]

async def vs_base(ctx, arg1, arg2, secili=False):
    rakip = None; bahis = 10
    if not arg1: return await ctx.send("Kimi döveceksin? Birini etiketle!")
    try: rakip = await commands.MemberConverter().convert(ctx, arg1)
    except:
        if arg1.isdigit(): bahis = int(arg1)
    if arg2:
        try: rakip = await commands.MemberConverter().convert(ctx, arg2)
        except:
            if arg2.isdigit(): bahis = int(arg2)
            
    if not rakip: return await ctx.send("Geçerli bir rakip etiketlemelisin!")
    if bahis < 10: return await ctx.send("En düşük bahis 10 Puan olmak zorundadır!")
    if not ctx.author.voice: return await ctx.send("Önce sese gir!")
    
    oyuncular = [ctx.author, rakip]
    fakirler = bakiye_kontrol(oyuncular, bahis)
    if fakirler: return await ctx.send(f"❌ Kasa yetersiz! {' ve '.join(fakirler)} cüzdanında **{bahis} Puan** yok.")

    secimler, msg = await ayarlari_al(ctx, secili=secili)
    if not secimler: return

    sarkici_g, zorluk_g, raund_g = ayar_cevir(secimler)
    davet_view = CokluDavetView([rakip])
    await msg.edit(content=f"🚨 **DÜELLO!** {rakip.mention}, {ctx.author.mention} senden **{bahis} Puan** koparmak için meydan okuyor!\n🎤 **Şarkıcı:** {sarkici_g} | ⚙️ **Zorluk:** {zorluk_g} | 🔄 **{raund_g} Raund**\nKabul mü?", view=davet_view)
    await davet_view.wait()
    if not davet_view.kabul_edildi: return

    for o in oyuncular: db_puan_ekle(o.id, -bahis)
    eski_kanallar = {o.id: o.voice.channel for o in oyuncular if o.voice}
    kategori = ctx.author.voice.channel.category
    overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=False)}
    for o in oyuncular: overwrites[o] = discord.PermissionOverwrite(connect=True, speak=False, view_channel=True)
    overwrites[ctx.guild.me] = discord.PermissionOverwrite(connect=True, speak=True, view_channel=True)
    yeni_kanal = await ctx.guild.create_voice_channel(f"⚔️ {ctx.author.name} vs {rakip.name}", category=kategori, overwrites=overwrites)
    for o in oyuncular:
        if o.voice: await o.move_to(yeni_kanal)
    await oyun_motoru(ctx, secimler, oyuncular, yeni_kanal, eski_kanallar, rekabetci=True, bahis=bahis)

async def ffa_base(ctx, args, secili=False):
    if not ctx.author.voice: return await ctx.send("Önce sese gir!")
    bahis = 10; rakipler = []
    for arg in args:
        if arg.isdigit(): bahis = int(arg)
        else:
            try: 
                member = await commands.MemberConverter().convert(ctx, arg)
                if member not in rakipler and not member.bot and member != ctx.author: rakipler.append(member)
            except: pass
            
    oyuncular = [ctx.author] + rakipler
    if len(oyuncular) < 2: return await ctx.send("En az 1 kişiyi daha etiketlemelisin!")
    if bahis < 10: return await ctx.send("En düşük bahis 10 Puan olmak zorundadır!")
    fakirler = bakiye_kontrol(oyuncular, bahis)
    if fakirler: return await ctx.send(f"❌ Kasa yetersiz! Şu fakirlerin **{bahis} Puanı** yok:\n{', '.join(fakirler)}")

    secimler, msg = await ayarlari_al(ctx, secili=secili)
    if not secimler: return

    sarkici_g, zorluk_g, raund_g = ayar_cevir(secimler)
    etiketler = " ".join([r.mention for r in rakipler])
    davet_view = CokluDavetView(rakipler)
    await msg.edit(content=f"📢 **KANLI ARENA DAVETİ!** {etiketler}\n💰 **Giriş:** {bahis} Puan | 🎤 **Şarkıcı:** {sarkici_g} | ⚙️ **Zorluk:** {zorluk_g} | 🔄 **{raund_g} Raund**\nKazanan devasa havuzu alır. Kabul mü?", view=davet_view)
    await davet_view.wait()
    if not davet_view.kabul_edildi: return

    for o in oyuncular: db_puan_ekle(o.id, -bahis)
    eski_kanallar = {o.id: o.voice.channel for o in oyuncular if o.voice}
    kategori = ctx.author.voice.channel.category
    overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=False)}
    for o in oyuncular: overwrites[o] = discord.PermissionOverwrite(connect=True, speak=False, view_channel=True)
    overwrites[ctx.guild.me] = discord.PermissionOverwrite(connect=True, speak=True, view_channel=True)
    yeni_kanal = await ctx.guild.create_voice_channel("🩸 KANLI FFA ARENASI", category=kategori, overwrites=overwrites)
    for o in oyuncular:
        if o.voice: await o.move_to(yeni_kanal)
    await oyun_motoru(ctx, secimler, oyuncular, yeni_kanal, eski_kanallar, rekabetci=True, bahis=bahis)

async def birlikte_base(ctx, rakipler, secili=False):
    if not ctx.author.voice: return await ctx.send("Önce sese gir!")
    oyuncular = [ctx.author]
    davetliler = []
    for r in rakipler:
        if r not in oyuncular and not r.bot:
            oyuncular.append(r); davetliler.append(r)
    if not davetliler: return await ctx.send("En az 1 kişiyi daha etiketlemelisin!")

    secimler, msg = await ayarlari_al(ctx, secili=secili)
    if not secimler: return

    sarkici_g, zorluk_g, raund_g = ayar_cevir(secimler)
    etiketler = " ".join([d.mention for d in davetliler])
    davet_view = CokluDavetView(davetliler)
    await msg.edit(content=f"📢 **EĞLENCE DAVETİ (Bedava)!** {etiketler}\n🎤 **Şarkıcı:** {sarkici_g} | ⚙️ **Zorluk:** {zorluk_g} | 🔄 **{raund_g} Raund**\nHerkes onaylasın:", view=davet_view)
    await davet_view.wait()
    if not davet_view.kabul_edildi: return

    eski_kanallar = {o.id: o.voice.channel for o in oyuncular if o.voice}
    kategori = ctx.author.voice.channel.category
    overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=False)}
    for o in oyuncular: overwrites[o] = discord.PermissionOverwrite(connect=True, speak=True, view_channel=True)
    overwrites[ctx.guild.me] = discord.PermissionOverwrite(connect=True, speak=True, view_channel=True)
    yeni_kanal = await ctx.guild.create_voice_channel("🎉 DOSTLUK ODASI", category=kategori, overwrites=overwrites)
    for o in oyuncular:
        if o.voice: await o.move_to(yeni_kanal)
    await oyun_motoru(ctx, secimler, oyuncular, yeni_kanal, eski_kanallar, rekabetci=False)

# --- DOSTLUK KOMUTLARI ---
@bot.command(aliases=['play'])
async def oyna(ctx, rakip: discord.Member = None):
    if not ctx.author.voice: return await ctx.send("Önce sese gir!")
    
    if rakip:
        if rakip == ctx.author or rakip.bot: return await ctx.send("Kendinle veya botlarla kapışamazsın!")
        
        oyuncular = [ctx.author, rakip]
        secimler, msg = await ayarlari_al(ctx, secili=False)
        if not secimler: return

        sarkici_g, zorluk_g, raund_g = ayar_cevir(secimler)
        davet_view = CokluDavetView([rakip])
        await msg.edit(content=f"🤝 **DOSTLUK 1V1 MAÇI!** {rakip.mention}, {ctx.author.mention} seni bedava (puan düşmeyen) maça çağırıyor.\n🎤 **Şarkıcı:** {sarkici_g} | ⚙️ **Zorluk:** {zorluk_g} | 🔄 **{raund_g} Raund**\nKabul mü?", view=davet_view)
        await davet_view.wait()
        if not davet_view.kabul_edildi: return

        eski_kanallar = {o.id: o.voice.channel for o in oyuncular if o.voice}
        kategori = ctx.author.voice.channel.category
        overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=False)}
        for o in oyuncular: overwrites[o] = discord.PermissionOverwrite(connect=True, speak=True, view_channel=True)
        overwrites[ctx.guild.me] = discord.PermissionOverwrite(connect=True, speak=True, view_channel=True)
        
        yeni_kanal = await ctx.guild.create_voice_channel("🤝 DOSTLUK ARENASI", category=kategori, overwrites=overwrites)
        for o in oyuncular:
            if o.voice: await o.move_to(yeni_kanal)
        await oyun_motoru(ctx, secimler, oyuncular, yeni_kanal, eski_kanallar, rekabetci=False)
        
    else:
        secimler, msg = await ayarlari_al(ctx, secili=False)
        if not secimler: return

        eski_kanallar = {ctx.author.id: ctx.author.voice.channel}
        kategori = ctx.author.voice.channel.category
        overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=False), ctx.author: discord.PermissionOverwrite(connect=True, speak=True, view_channel=True), ctx.guild.me: discord.PermissionOverwrite(connect=True, speak=True, view_channel=True)}
        yeni_kanal = await ctx.guild.create_voice_channel(f"🎮 {ctx.author.name} Antrenman", category=kategori, overwrites=overwrites)
        await ctx.author.move_to(yeni_kanal)
        await oyun_motoru(ctx, secimler, [ctx.author], yeni_kanal, eski_kanallar, rekabetci=False)

@bot.command()
async def secili(ctx, rakip: discord.Member = None):
    if not rakip: return await ctx.send("Kime bedava maç atacaksın? Kullanım: `!secili @kisi`")
    if not ctx.author.voice: return await ctx.send("Önce sese gir!")
    
    oyuncular = [ctx.author, rakip]
    secimler, msg = await ayarlari_al(ctx, secili=True)
    if not secimler: return

    sarkici_g, zorluk_g, raund_g = ayar_cevir(secimler)
    davet_view = CokluDavetView([rakip])
    await msg.edit(content=f"🤝 **DOSTLUK MAÇI DAVETİ!** {rakip.mention}, {ctx.author.mention} seni bedava maça çağırıyor.\n🎤 **Şarkıcı:** {sarkici_g} | ⚙️ **Zorluk:** {zorluk_g} | 🔄 **{raund_g} Raund**\nKabul mü?", view=davet_view)
    await davet_view.wait()
    if not davet_view.kabul_edildi: return

    eski_kanallar = {o.id: o.voice.channel for o in oyuncular if o.voice}
    kategori = ctx.author.voice.channel.category
    overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=False)}
    for o in oyuncular: overwrites[o] = discord.PermissionOverwrite(connect=True, speak=True, view_channel=True)
    overwrites[ctx.guild.me] = discord.PermissionOverwrite(connect=True, speak=True, view_channel=True)
    yeni_kanal = await ctx.guild.create_voice_channel("🤝 DOSTLUK ARENASI", category=kategori, overwrites=overwrites)
    for o in oyuncular:
        if o.voice: await o.move_to(yeni_kanal)
    await oyun_motoru(ctx, secimler, oyuncular, yeni_kanal, eski_kanallar, rekabetci=False)

@bot.command(aliases=['coklu', 'party'])
async def oynabirlikte(ctx, *rakipler: discord.Member):
    await birlikte_base(ctx, rakipler, secili=False)

@bot.command()
async def secilibirlikte(ctx, *rakipler: discord.Member):
    await birlikte_base(ctx, rakipler, secili=True)

# --- REKABETÇİ KOMUTLARI ---
@bot.command(aliases=['duel', 'duello'])
async def vs(ctx, arg1: str = None, arg2: str = None):
    await vs_base(ctx, arg1, arg2, secili=False)

@bot.command()
async def secilivs(ctx, arg1: str = None, arg2: str = None):
    await vs_base(ctx, arg1, arg2, secili=True)

@bot.command()
async def ffa(ctx, *args):
    await ffa_base(ctx, args, secili=False)

@bot.command()
async def seciliffa(ctx, *args):
    await ffa_base(ctx, args, secili=True)

@bot.command(aliases=['oynabukanalda', 'ortakoyna'])
async def oynaburada(ctx):
    if not ctx.author.voice: return await ctx.send("Önce sese gir!")
    kanal = ctx.author.voice.channel
    oyuncular = [uye for uye in kanal.members if not uye.bot]
    secimler, msg = await ayarlari_al(ctx, secili=False)
    if not secimler: return
    
    davetliler = [o for o in oyuncular if o != ctx.author]
    if davetliler:
        sarkici_g, zorluk_g, raund_g = ayar_cevir(secimler)
        etiketler = " ".join([d.mention for d in davetliler])
        davet_view = CokluDavetView(davetliler)
        await msg.edit(content=f"📢 **DOSTLUK MAÇI!** {etiketler}\n🎤 **Şarkıcı:** {sarkici_g} | ⚙️ **Zorluk:** {zorluk_g} | 🔄 **{raund_g} Raund**\nHerkes onaylasın:", view=davet_view)
        await davet_view.wait()
        if not davet_view.kabul_edildi: return
    await oyun_motoru(ctx, secimler, oyuncular, ozel_kanal=None, eski_kanallar=None, rekabetci=False)

@bot.command(aliases=['random'])
async def rastgele(ctx):
    if not ctx.author.voice: return await ctx.send("Önce sese gir!")
    secimler = rastgele_secimler_uret()
    if not secimler: return await ctx.send("❌ Kütüphanede hiç şarkıcı bulunamadı!")
    
    eski_kanallar = {ctx.author.id: ctx.author.voice.channel}
    kategori = ctx.author.voice.channel.category
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=False),
        ctx.author: discord.PermissionOverwrite(connect=True, speak=True, view_channel=True),
        ctx.guild.me: discord.PermissionOverwrite(connect=True, speak=True, view_channel=True)
    }
    yeni_kanal = await ctx.guild.create_voice_channel(f"🎲 {ctx.author.name} Rastgele", category=kategori, overwrites=overwrites)
    await ctx.author.move_to(yeni_kanal)
    await ctx.send(f"🎲 **RASTGELE MOD:** ({secimler['sarkici'].upper()} / {secimler['zorluk'].upper()} / {secimler['raund']} Raund)")
    await oyun_motoru(ctx, secimler, [ctx.author], yeni_kanal, eski_kanallar, rekabetci=False)

@bot.command(name="2vs2", aliases=["2v2"])
async def ikivsiki(ctx, kanka: discord.Member, rakip1: discord.Member, rakip2: discord.Member):
    bahis = 10
    if not ctx.author.voice: return await ctx.send("Önce sese gir!")
    oyuncular = [ctx.author, kanka, rakip1, rakip2]
    davetliler = [kanka, rakip1, rakip2]
    if len(set(oyuncular)) != 4 or any(o.bot for o in oyuncular): return await ctx.send("Tam 4 farklı gerçek kişi etiketlemelisin!")
    fakirler = bakiye_kontrol(oyuncular, bahis)
    if fakirler: return await ctx.send(f"❌ Birilerinin giriş ücretini ödeyecek {bahis} puanı yok:\n{', '.join(fakirler)}")

    takimlar = {"🔵 MAVİ TAKIM": [ctx.author, kanka], "🔴 KIRMIZI TAKIM": [rakip1, rakip2]}
    secimler, msg = await ayarlari_al(ctx, secili=False)
    if not secimler: return

    sarkici_g, zorluk_g, raund_g = ayar_cevir(secimler)
    etiketler = " ".join([d.mention for d in davetliler])
    davet_view = CokluDavetView(davetliler)
    await msg.edit(content=f"🛡️ **TAKIM SAVAŞI!** {etiketler}\n💰 **Giriş:** {bahis} Puan | 🎤 **Şarkıcı:** {sarkici_g} | ⚙️ **Zorluk:** {zorluk_g} | 🔄 **{raund_g} Raund**\nMavi vs Kırmızı! Herkesin kılıçları çekmesi gerek:", view=davet_view)
    await davet_view.wait()
    if not davet_view.kabul_edildi: return

    for o in oyuncular: db_puan_ekle(o.id, -bahis)
    eski_kanallar = {o.id: o.voice.channel for o in oyuncular if o.voice}
    kategori = ctx.author.voice.channel.category
    overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=False)}
    for o in oyuncular: overwrites[o] = discord.PermissionOverwrite(connect=True, speak=False, view_channel=True)
    overwrites[ctx.guild.me] = discord.PermissionOverwrite(connect=True, speak=True, view_channel=True)
    yeni_kanal = await ctx.guild.create_voice_channel("⚔️ 2VS2 ARENA", category=kategori, overwrites=overwrites)
    for o in oyuncular:
        if o.voice: await o.move_to(yeni_kanal)
    await oyun_motoru(ctx, secimler, oyuncular, yeni_kanal, eski_kanallar, takimlar, rekabetci=True, bahis=bahis)

@bot.command(name="3vs3", aliases=["3v3"])
async def ucvsuc(ctx, kanka1: discord.Member, kanka2: discord.Member, rakip1: discord.Member, rakip2: discord.Member, rakip3: discord.Member):
    bahis = 10
    if not ctx.author.voice: return await ctx.send("Önce sese gir!")
    oyuncular = [ctx.author, kanka1, kanka2, rakip1, rakip2, rakip3]
    davetliler = [kanka1, kanka2, rakip1, rakip2, rakip3]
    
    if len(set(oyuncular)) != 6 or any(o.bot for o in oyuncular): return await ctx.send("Tam 6 farklı gerçek kişi etiketlemelisin!")
    fakirler = bakiye_kontrol(oyuncular, bahis)
    if fakirler: return await ctx.send(f"❌ Bazı askerlerin savaşa girecek 10 puanı yok:\n{', '.join(fakirler)}")

    takimlar = {"🔵 MAVİ TAKIM": [ctx.author, kanka1, kanka2], "🔴 KIRMIZI TAKIM": [rakip1, rakip2, rakip3]}
    secimler, msg = await ayarlari_al(ctx, secili=False)
    if not secimler: return

    sarkici_g, zorluk_g, raund_g = ayar_cevir(secimler)
    etiketler = " ".join([d.mention for d in davetliler])
    davet_view = CokluDavetView(davetliler)
    await msg.edit(content=f"🛡️ **DESTANSI SAVAŞ!** {etiketler}\n💰 **Giriş:** {bahis} Puan | 🎤 **Şarkıcı:** {sarkici_g} | ⚙️ **Zorluk:** {zorluk_g} | 🔄 **{raund_g} Raund**\nHerkes kılıçları çeksin:", view=davet_view)
    await davet_view.wait()
    if not davet_view.kabul_edildi: return

    for o in oyuncular: db_puan_ekle(o.id, -bahis)
    eski_kanallar = {o.id: o.voice.channel for o in oyuncular if o.voice}
    kategori = ctx.author.voice.channel.category
    overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=False)}
    for o in oyuncular: overwrites[o] = discord.PermissionOverwrite(connect=True, speak=False, view_channel=True)
    overwrites[ctx.guild.me] = discord.PermissionOverwrite(connect=True, speak=True, view_channel=True)
    yeni_kanal = await ctx.guild.create_voice_channel("⚔️ 3VS3 ARENA", category=kategori, overwrites=overwrites)
    for o in oyuncular:
        if o.voice: await o.move_to(yeni_kanal)
    await oyun_motoru(ctx, secimler, oyuncular, yeni_kanal, eski_kanallar, takimlar, rekabetci=True, bahis=bahis)

@bot.command(aliases=['randomvs'])
async def rastgelevs(ctx, rakip: discord.Member):
    if not ctx.author.voice: return await ctx.send("Önce sese gir!")
    if rakip == ctx.author or rakip.bot: return await ctx.send("Kendinle veya botlarla kapışamazsın!")

    secimler = rastgele_secimler_uret()
    if not secimler: return await ctx.send("❌ Kütüphanede hiç şarkıcı bulunamadı!")

    bahis = 10
    oyuncular = [ctx.author, rakip]
    fakirler = bakiye_kontrol(oyuncular, bahis)
    if fakirler: return await ctx.send(f"❌ Kasa yetersiz! Biri veya ikinizin **{bahis} Puanı** yok!")

    davet_view = CokluDavetView([rakip])
    await ctx.send(f"🌪️ **RASTGELE DÜELLO!** {rakip.mention}, {ctx.author.mention} seni **10 Puan** bahisli rastgele kapışmaya çağırıyor! Kabul mü?", view=davet_view)
    await davet_view.wait()
    if not davet_view.kabul_edildi: return 
    
    for o in oyuncular: db_puan_ekle(o.id, -bahis)
    eski_kanallar = {o.id: o.voice.channel for o in oyuncular if o.voice}

    kategori = ctx.author.voice.channel.category
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=False),
        ctx.author: discord.PermissionOverwrite(connect=True, speak=False, view_channel=True),
        rakip: discord.PermissionOverwrite(connect=True, speak=False, view_channel=True),
        ctx.guild.me: discord.PermissionOverwrite(connect=True, speak=True, view_channel=True)
    }
    yeni_kanal = await ctx.guild.create_voice_channel(f"🎲 {ctx.author.name} vs {rakip.name}", category=kategori, overwrites=overwrites)
    for o in oyuncular:
        if o.voice: await o.move_to(yeni_kanal)
        
    await ctx.send(f"🎙️ Rastgele mod aktif! Seçimler: ({secimler['sarkici'].upper()} / {secimler['zorluk'].upper()} / {secimler['raund']} Raund)")
    await oyun_motoru(ctx, secimler, oyuncular, yeni_kanal, eski_kanallar, rekabetci=True, bahis=bahis)

bot.run(TOKEN)