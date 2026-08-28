"""
telegram_at.py — AT projesine OZEL Telegram bildirimi (kripto'dan AYRI bot/kanal; K60).
Token + chat_id: kod/telegram_config.json (GIT'E GIRMEZ; .gitignore'da). Dosya yoksa/eksikse
gonder() SESSIZCE no-op (False) -> bot kurulmadan da kod guvenle calisir, hicbir sey bozulmaz.
urllib ile; YENI BAGIMLILIK YOK. Hata firlatmaz.

Kurulum:
  1) Telegram'da @BotFather -> /newbot -> token al.
  2) Yeni bota bir mesaj yaz ("merhaba").
  3) python telegram_at.py --kur <TOKEN>   -> chat_id'yi bulup config'i yazar, test mesaji atar.
"""
import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

CFG = Path(__file__).resolve().parent / "telegram_config.json"
API = "https://api.telegram.org/bot"
# K139: gonderim sonucu GORUNUR olsun. takip.py ile AYNI dosya -> kullanici tek yere bakar.
LOG = Path(__file__).resolve().parent.parent / "veri" / "takip_log.txt"
_CFG_UYARISI_VERILDI = False


def _log(msg):
    """K139: tek satir log. KENDISI ASLA PATLAMAZ — gonderimi etkilemesi yasak."""
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S}  {msg}\n")
    except Exception:                                        # noqa: BLE001
        pass


def _cfg():
    if not CFG.exists():
        return None
    try:
        c = json.loads(CFG.read_text(encoding="utf-8"))
        return c if (c.get("token") and c.get("chat_id")) else None
    except Exception:
        return None


def gonder(mesaj):
    """Mesaji AT botundan chat_id'ye yollar. Doner: True/False. ASLA hata firlatmaz.

    K139: eskiden butun hatalar SESSIZCE yutuluyordu ve donus degerini kimse okumuyordu;
    "bildirim gitti mi" sorusu geriye donuk cevaplanamiyordu. Artik her sonuc
    veri/takip_log.txt'ye yazilir. Sozlesme DEGISMEDI (bool doner, hata firlatmaz)."""
    global _CFG_UYARISI_VERILDI
    c = _cfg()
    if not c:
        if not _CFG_UYARISI_VERILDI:                  # her cagride degil, surecte BIR kez
            _CFG_UYARISI_VERILDI = True
            _log("telegram: config yok/eksik -> bildirim GONDERILMIYOR "
                 "(kurulum: python kod/telegram_at.py --kur <TOKEN>)")
        return False
    try:
        data = urllib.parse.urlencode({
            "chat_id": c["chat_id"], "text": mesaj,
            "parse_mode": "HTML", "disable_web_page_preview": "true",
        }).encode()
        req = urllib.request.Request(f"{API}{c['token']}/sendMessage", data=data)
        with urllib.request.urlopen(req, timeout=15) as r:
            ok = r.status == 200
        _log(f"telegram: gonderildi ({len(mesaj)} karakter)" if ok
             else f"telegram: GONDERILEMEDI (HTTP {r.status})")
        return ok
    except urllib.error.HTTPError as e:
        detay = ""
        try:
            detay = e.read().decode("utf-8", "replace")[:200]
        except Exception:                                    # noqa: BLE001
            pass
        _log(f"telegram: GONDERILEMEDI -> HTTP {e.code} {detay}")
        return False
    except Exception as e:                                   # noqa: BLE001
        _log(f"telegram: GONDERILEMEDI -> {type(e).__name__}: {e}")
        return False


def chat_id_bul(token):
    """Botla mesajlastiktan SONRA getUpdates'ten chat_id adaylarini dondurur."""
    with urllib.request.urlopen(f"{API}{token}/getUpdates", timeout=15) as r:
        o = json.loads(r.read().decode("utf-8", "replace"))
    out = []
    for u in o.get("result", []):
        msg = u.get("message") or u.get("channel_post") or {}
        ch = msg.get("chat", {})
        if ch.get("id") is not None:
            out.append((ch["id"], ch.get("first_name") or ch.get("title") or ch.get("username") or ""))
    # tekrarsiz, sirayi koru
    gorulen, tekil = set(), []
    for cid, ad in out:
        if cid not in gorulen:
            gorulen.add(cid); tekil.append((cid, ad))
    return tekil


def _kur(token):
    """chat_id'yi bul, config'i yaz, test mesaji at."""
    adaylar = chat_id_bul(token)
    if not adaylar:
        print("chat_id bulunamadi. Once Telegram'da yeni bota bir mesaj yaz, sonra tekrar dene.")
        return 1
    cid, ad = adaylar[0]
    if len(adaylar) > 1:
        print(f"Birden fazla sohbet bulundu, ilki secildi: {adaylar}")
    CFG.write_text(json.dumps({"token": token, "chat_id": cid}, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print(f"config yazildi: chat_id={cid} ({ad}) -> {CFG.name}")
    ok = gonder("✅ AT botu kuruldu. Altılı kuponu kurulunca buraya bildirim gelecek.")
    print("test mesaji:", "GONDERILDI" if ok else "GONDERILEMEDI (token/chat_id kontrol)")
    return 0 if ok else 1


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--kur", metavar="TOKEN", help="Token ile chat_id bul + config yaz + test at")
    ap.add_argument("--test", action="store_true", help="Mevcut config ile test mesaji at")
    a = ap.parse_args()
    if a.kur:
        raise SystemExit(_kur(a.kur))
    if a.test:
        print("test:", "GONDERILDI" if gonder("AT test mesaji.") else "GONDERILEMEDI (config yok/hatali)")
